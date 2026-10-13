"""Isolation priority ranking (blueprint Sections 4.11 and 5.7), extra view.

For every road node: travel time to the nearest suitable facility on the unmodified graph (T_base) and
on the flood-modified graph (T_fa), each from ONE multi-source search on the reversed graph. A node is
`isolated` if it reaches a facility normally but not after flooding, `delayed` if it loses
ISOLATION_DELAY_MIN minutes or more, and `baseline_disconnected` (excluded, counted) if it could not
reach any facility even without flooding.

Units: the ward polygons and Census populations were NOT loaded (the join was cut from the 2-hour
plan), so the units are the fallback grid cells of ISOLATION_FALLBACK_GRID_M and every cell has the
placeholder population weight 1.0. The ranking is therefore by the share of road nodes, not by
people, and the "people" column is a share of sample points. Indicative only; not a forecast.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
from shapely.geometry import box

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, Config  # noqa: E402

PLACEHOLDER_POPULATION = 1.0
COLUMNS = ["unit_id", "unit_name", "population", "population_basis", "nodes_total", "nodes_eligible",
           "nodes_baseline_disconnected", "nodes_isolated", "nodes_delayed", "isolated_share", "delayed_share",
           "estimated_people_isolated", "priority_score", "rank"]


class IsolationError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code


def node_times(G: nx.MultiDiGraph, facility_nodes: List[int]) -> Dict[int, float]:
    """Seconds from every node to the nearest facility node: one multi-source search on the reversed graph."""
    sources = [n for n in facility_nodes if n in G]
    if not sources:
        return {}
    return dict(nx.multi_source_dijkstra_path_length(G.reverse(copy=False), sources, weight="travel_time"))


def node_states(G: nx.MultiDiGraph, G2: nx.MultiDiGraph, facility_nodes: List[int], cfg: Config = CONFIG) -> Dict[int, str]:
    base = node_times(G, facility_nodes)
    fa = node_times(G2, facility_nodes)
    states: Dict[int, str] = {}
    for n in G.nodes:
        if n not in base:
            states[n] = "baseline_disconnected"
        elif n not in fa:
            states[n] = "isolated"
        elif (fa[n] - base[n]) / 60.0 >= cfg.ISOLATION_DELAY_MIN:
            states[n] = "delayed"
        else:
            states[n] = "ok"
    return states


def grid_assignment(G: nx.MultiDiGraph, cfg: Config = CONFIG) -> Tuple[Dict[int, Tuple[int, int]], Dict[Tuple[int, int], object]]:
    """Cell (row, col) for every node and the cell polygons (metric CRS). Row 0 is the southern row."""
    ids = list(G.nodes)
    pts = gpd.GeoSeries(gpd.points_from_xy([G.nodes[n]["x"] for n in ids], [G.nodes[n]["y"] for n in ids]),
                        crs=cfg.CRS_GEO).to_crs(cfg.CRS_METRIC)
    cell = cfg.ISOLATION_FALLBACK_GRID_M
    x0, y0 = float(pts.x.min()), float(pts.y.min())
    cells: Dict[int, Tuple[int, int]] = {}
    polys: Dict[Tuple[int, int], object] = {}
    for n, x, y in zip(ids, pts.x.values, pts.y.values):
        rc = (int(math.floor((y - y0) / cell)), int(math.floor((x - x0) / cell)))
        cells[n] = rc
        if rc not in polys:
            polys[rc] = box(x0 + rc[1] * cell, y0 + rc[0] * cell, x0 + (rc[1] + 1) * cell, y0 + (rc[0] + 1) * cell)
    return cells, polys


def rank_units(df: pd.DataFrame, cfg: Config = CONFIG) -> pd.DataFrame:
    """Score and rank (Section 5.7.4). Ties: larger isolated share, then larger population, then unit_id."""
    out = df.copy()
    out["estimated_people_isolated"] = out["population"] * out["isolated_share"]
    out["priority_score"] = out["population"] * (out["isolated_share"] + cfg.ISOLATION_DELAY_WEIGHT * out["delayed_share"])
    out = out.sort_values(["priority_score", "isolated_share", "population", "unit_id"],
                          ascending=[False, False, False, True]).reset_index(drop=True)
    out["rank"] = np.arange(1, len(out) + 1)
    return out


def compute(G: nx.MultiDiGraph, G2: nx.MultiDiGraph, facility_nodes: List[int], cfg: Config = CONFIG,
            populations: Dict[str, float] | None = None, units: Dict[int, str | None] | None = None,
            unit_names: Dict[str, str] | None = None) -> Tuple[pd.DataFrame, List[str]]:
    """The Section 3.9 table for one scenario, and non-fatal warning codes.

    By default the units are the fallback grid cells with placeholder weights. Pass `units` (node ->
    unit id, None for a node outside every unit), `populations` (unit id -> people) and optionally
    `unit_names` to use wards with census populations.
    """
    warnings: List[str] = []
    states = node_states(G, G2, facility_nodes, cfg)
    if all(s == "baseline_disconnected" for s in states.values()):
        raise IsolationError("ISOLATION_NO_ELIGIBLE_NODES", "every node is disconnected in the baseline graph")
    by_unit: Dict[str, List[str]] = {}
    if units is None:
        cells, _ = grid_assignment(G, cfg)
        for n, (r, c) in cells.items():
            by_unit.setdefault(f"Zone r{r}c{c}", []).append(states[n])
    else:
        for n, uid in units.items():
            if uid is None:
                warnings.append("ISOLATION_NODE_UNASSIGNED")
            else:
                by_unit.setdefault(uid, []).append(states[n])
    rows = []
    for unit_id, st in sorted(by_unit.items()):
        eligible = [s for s in st if s != "baseline_disconnected"]
        if len(eligible) < cfg.MIN_ELIGIBLE_NODES_PER_UNIT:
            warnings.append("ISOLATION_UNIT_EMPTY")
            continue
        pop = (populations or {}).get(unit_id, PLACEHOLDER_POPULATION)
        iso, dly = eligible.count("isolated"), eligible.count("delayed")
        rows.append({"unit_id": unit_id, "unit_name": (unit_names or {}).get(unit_id, unit_id), "population": pop,
                     "population_basis": "placeholder" if populations is None else "ward_census_2011",
                     "nodes_total": len(st), "nodes_eligible": len(eligible),
                     "nodes_baseline_disconnected": len(st) - len(eligible), "nodes_isolated": iso, "nodes_delayed": dly,
                     "isolated_share": iso / len(eligible), "delayed_share": dly / len(eligible)})
    if not rows:
        raise IsolationError("UNITS_NOT_AVAILABLE", "no unit has enough eligible nodes")
    return rank_units(pd.DataFrame(rows), cfg)[COLUMNS], warnings


def cells_geojson(G: nx.MultiDiGraph, unit_ids: List[str], cfg: Config = CONFIG) -> Dict[str, object]:
    """Polygons (EPSG:4326, 5 decimals) of the grid cells that are units."""
    _, polys = grid_assignment(G, cfg)
    feats = []
    for (r, c), poly in polys.items():
        uid = f"Zone r{r}c{c}"
        if uid in unit_ids:
            geo = gpd.GeoSeries([poly], crs=cfg.CRS_METRIC).to_crs(cfg.CRS_GEO).iloc[0]
            ring = [[round(x, 5), round(y, 5)] for x, y in geo.exterior.coords]
            feats.append({"type": "Feature", "properties": {"unit_id": uid},
                          "geometry": {"type": "Polygon", "coordinates": [ring]}})
    return {"type": "FeatureCollection", "features": feats}


def wards_geojson(zone_wards: "gpd.GeoDataFrame", unit_ids: List[str], tolerance_m: float = 3.0, cfg: Config = CONFIG) -> Dict[str, object]:
    """Ward polygons clipped to the study zone (EPSG:4326, 5 decimals), keyed W<number> like the units."""
    feats = []
    metric = gpd.GeoSeries(zone_wards["geometry_in_zone"], crs=cfg.CRS_GEO).to_crs(cfg.CRS_METRIC).simplify(tolerance_m)
    geo = metric.to_crs(cfg.CRS_GEO)
    for ward_id, geom in zip(zone_wards["ward_id"], geo):
        uid = f"W{int(ward_id)}"
        if uid not in unit_ids or geom.is_empty:
            continue
        polys = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        coords = [[[[round(x, 5), round(y, 5)] for x, y in p.exterior.coords]] for p in polys if p.geom_type == "Polygon"]
        feats.append({"type": "Feature", "properties": {"unit_id": uid},
                      "geometry": {"type": "MultiPolygon", "coordinates": coords}})
    return {"type": "FeatureCollection", "features": feats}

"""Edge flood classification and the flood-modified graph (blueprint Sections 4.5 and 5.2).

An edge is classified by the share of its length inside the flood polygon: passable, at_risk (travel
time multiplied) or blocked (edge removed). The thresholds and the multiplier are assumptions
(config.py A-01 to A-03), not measured values. The input graph is never mutated.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Tuple

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import shapely
import shapely.prepared
from shapely import STRtree
from shapely.geometry import LineString, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, Config  # noqa: E402

PASSABLE, AT_RISK, BLOCKED = "passable", "at_risk", "blocked"


def flood_union_metric(flood_gdf: gpd.GeoDataFrame, cfg: Config = CONFIG) -> BaseGeometry:
    """One metric-CRS geometry for a scenario GeoDataFrame."""
    return unary_union(list(flood_gdf.to_crs(cfg.CRS_METRIC).geometry))


def edge_id(u, v, key) -> str:
    return f"{u}-{v}-{key}"


def _subdivide(flood_m: BaseGeometry, cell_m: float = 400.0):
    """Cut a large flood geometry into small disjoint pieces on a grid, so each edge is only
    intersected with the few pieces near it (intersecting 30,000 edges with the whole polygon takes minutes)."""
    minx, miny, maxx, maxy = flood_m.bounds
    prepared = shapely.prepared.prep(flood_m)
    pieces = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + cell_m, y + cell_m)
            if prepared.intersects(cell):
                part = flood_m.intersection(cell)
                if not part.is_empty:
                    pieces.append(part)
            y += cell_m
        x += cell_m
    return pieces


def _length_inside(lines, flood_m: BaseGeometry) -> np.ndarray:
    """Length of each line that lies inside the flood geometry (metric CRS)."""
    inside = np.zeros(len(lines))
    if flood_m.is_empty:
        return inside
    pieces = _subdivide(flood_m)
    tree = STRtree(pieces)
    line_idx, piece_idx = tree.query(lines, predicate="intersects")
    if len(line_idx):
        piece_arr = np.empty(len(pieces), dtype=object)
        piece_arr[:] = pieces
        lengths = shapely.length(shapely.intersection(lines[line_idx], piece_arr[piece_idx]))
        np.add.at(inside, line_idx, lengths)
    return inside


def classify_edges(G: nx.MultiDiGraph, flood_m: BaseGeometry, cfg: Config = CONFIG) -> pd.DataFrame:
    """Table of edge_id, u, v, key, length_m, flooded_fraction, class for every edge of G.

    Edges with no stored geometry use a straight line between their nodes (EDGE_GEOMETRY_MISSING);
    the count is returned in table.attrs["missing_geometry"].
    """
    rows = []
    geoms, missing = [], 0
    for u, v, key, data in G.edges(keys=True, data=True):
        geom = data.get("geometry")
        if geom is None:
            missing += 1
            geom = LineString([(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])])
        rows.append((u, v, key))
        geoms.append(geom)
    edges = gpd.GeoDataFrame(
        {"u": [r[0] for r in rows], "v": [r[1] for r in rows], "key": [r[2] for r in rows]},
        geometry=geoms,
        crs=cfg.CRS_GEO,
    ).to_crs(cfg.CRS_METRIC)
    length = edges.geometry.length
    inside = _length_inside(edges.geometry.to_numpy(), flood_m)
    with_len = length.where(length > 0)
    fraction = (inside / with_len).fillna(0.0).clip(0.0, 1.0)
    cls = pd.Series(PASSABLE, index=edges.index)
    cls[fraction >= cfg.FLOOD_FRACTION_AT_RISK] = AT_RISK
    cls[fraction >= cfg.FLOOD_FRACTION_BLOCKED] = BLOCKED
    table = pd.DataFrame(
        {
            "edge_id": [edge_id(u, v, k) for u, v, k in rows],
            "u": edges["u"].values,
            "v": edges["v"].values,
            "key": edges["key"].values,
            "length_m": length.values,
            "flooded_fraction": fraction.values,
            "class": cls.values,
        }
    )
    table.attrs["missing_geometry"] = missing
    return table


def apply_flood(G: nx.MultiDiGraph, table: pd.DataFrame, cfg: Config = CONFIG) -> nx.MultiDiGraph:
    """Copy of G with blocked edges removed and at-risk edges slowed. G itself is unchanged."""
    G2 = G.copy()
    blocked = table.loc[table["class"] == BLOCKED, ["u", "v", "key"]]
    slowed = table.loc[table["class"] == AT_RISK, ["u", "v", "key"]]
    for u, v, key in blocked.itertuples(index=False):
        if G2.has_edge(u, v, key):
            G2.remove_edge(u, v, key)
    for u, v, key in slowed.itertuples(index=False):
        if G2.has_edge(u, v, key):
            G2[u][v][key]["travel_time"] = G2[u][v][key]["travel_time"] * cfg.AT_RISK_TIME_MULTIPLIER
    return G2


def class_counts(table: pd.DataFrame) -> Dict[str, int]:
    counts = table["class"].value_counts().to_dict()
    return {c: int(counts.get(c, 0)) for c in (PASSABLE, AT_RISK, BLOCKED)}


def class_lookup(table: pd.DataFrame) -> Dict[Tuple, str]:
    return {(u, v, k): c for u, v, k, c in table[["u", "v", "key", "class"]].itertuples(index=False)}


def distance_to_flood(points, flood_m: BaseGeometry) -> np.ndarray:
    """Distance (m) from each metric-CRS point to the flood geometry (0 if inside)."""
    pieces = _subdivide(flood_m)
    tree = STRtree(pieces)
    idx, dist = tree.query_nearest(points, return_distance=True, all_matches=False)
    out = np.full(len(points), np.inf)
    out[idx[0]] = dist
    return out

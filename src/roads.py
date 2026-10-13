"""Road graph for the study zone (blueprint Section 4.3).

Builds a drivable OpenStreetMap graph for the zone in config.STUDY_BBOX, adds speeds and travel
times, caches it as GraphML, and exports a light GeoJSON outline for the web map. The roads are
TODAY's OpenStreetMap roads, not 2015 roads (standing gap 4); the app says so.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict

import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import Polygon, box

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, Config, validate_config  # noqa: E402

GRAPH_PATH = ROOT / "data" / "processed" / "roads.graphml"
MAX_EDGES = 150_000  # blueprint GRAPH_TOO_LARGE


class GraphBuildError(RuntimeError):
    code = "GRAPH_BUILD_FAILED"


class GraphTooLarge(RuntimeError):
    code = "GRAPH_TOO_LARGE"


def study_polygon(cfg: Config = CONFIG) -> Polygon:
    """The study zone as a polygon. A polygon, not a bbox tuple, because OSMnx's bbox argument order
    changed between versions (blueprint 4.3)."""
    validate_config(cfg, require_study_area=True)
    west, south, east, north = cfg.STUDY_BBOX  # type: ignore[misc]
    return box(west, south, east, north)


def _configure_osmnx() -> None:
    ox.settings.use_cache = True
    ox.settings.cache_folder = str(ROOT / "data" / "raw" / "osmnx_cache")
    ox.settings.log_console = False


def add_travel_times(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Add speed_kph and travel_time (seconds) to every edge using OSMnx's imputed speeds.

    These are free-flow speeds, not emergency-vehicle or flood-condition speeds, so results are
    comparative rather than absolute (assumption A-05).
    """
    G = ox.add_edge_speeds(G)
    return ox.add_edge_travel_times(G)


def build_graph(cfg: Config = CONFIG, path: Path = GRAPH_PATH, force: bool = False) -> nx.MultiDiGraph:
    """Return the cached graph, or download it from OpenStreetMap and cache it."""
    if path.exists() and not force:
        return load_graph(path)
    polygon = study_polygon(cfg)
    _configure_osmnx()
    try:
        G = ox.graph_from_polygon(polygon, network_type="drive", simplify=True)
    except Exception as exc:  # network, rate limit, empty area
        raise GraphBuildError(f"OpenStreetMap download failed: {type(exc).__name__}: {exc}") from exc
    if G.number_of_edges() == 0:
        raise GraphBuildError("the study zone contains no drivable roads")
    if G.number_of_edges() > MAX_EDGES:
        raise GraphTooLarge(f"{G.number_of_edges()} edges is over the {MAX_EDGES} limit; shrink STUDY_BBOX")
    G = add_travel_times(G)
    path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(G, path)
    return G


def load_graph(path: Path = GRAPH_PATH) -> nx.MultiDiGraph:
    return ox.load_graphml(path)


def summarize(G: nx.MultiDiGraph) -> Dict[str, float]:
    """Counts used in the data notes and the audit log."""
    lengths = [d.get("length", 0.0) for _, _, d in G.edges(data=True)]
    return {
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges(),
        "total_length_km": round(sum(lengths) / 1000.0, 1),
        "strongly_connected_components": nx.number_strongly_connected_components(G),
        "largest_scc_nodes": len(max(nx.strongly_connected_components(G), key=len)),
    }


def edges_geojson(G: nx.MultiDiGraph, out_path: Path, tolerance_m: float = 3.0, keep_minor: bool = True) -> int:
    """Write a light edge outline for the web map; returns the number of features.

    Each feature carries edge_id (u-v-key, the key later joined to the flood classification) and the
    highway class. Geometry is simplified (tolerance_m) and coordinates rounded to 5 decimals.
    """
    edges = ox.graph_to_gdfs(G, nodes=False).reset_index()
    edges["edge_id"] = edges["u"].astype(str) + "-" + edges["v"].astype(str) + "-" + edges["key"].astype(str)
    edges["highway"] = edges["highway"].apply(lambda h: h[0] if isinstance(h, list) else h)
    if not keep_minor:
        edges = edges[~edges["highway"].isin(["service", "living_street", "unclassified"])]
    metric = edges.to_crs(CONFIG.CRS_METRIC)
    metric["geometry"] = metric.geometry.simplify(tolerance_m, preserve_topology=False)
    light = metric[["edge_id", "highway", "geometry"]].to_crs(CONFIG.CRS_GEO)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads(light.to_json(drop_id=True))
    for feature in payload["features"]:
        feature["geometry"]["coordinates"] = _round_coords(feature["geometry"]["coordinates"])
    out_path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return len(payload["features"])


def _round_coords(coords):
    if coords and isinstance(coords[0], (int, float)):
        return [round(coords[0], 5), round(coords[1], 5)]
    return [_round_coords(c) for c in coords]


if __name__ == "__main__":
    graph = build_graph()
    print(summarize(graph))

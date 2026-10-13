"""Conventional and flood-aware routing to the nearest suitable facility (blueprint Sections 4.7 and 5.4).

Conventional = shortest travel time on the unmodified graph G. Flood-aware = the same on the
flood-modified graph G2. "Nearest" is least travel time; ties go to the better verification rank,
then facility_id. A route that cannot be found is a result with reachable=False, never an exception.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd

VERIFICATION_RANK = {"phone_verified": 0, "source_listed": 1, "unverified": 2}
UNREACHABLE_REASON = "ALL_SUITABLE_FACILITIES_UNREACHABLE"


@dataclass
class RouteResult:
    origin: int
    reachable: bool
    facility_id: Optional[str] = None
    path_nodes: List[int] = field(default_factory=list)
    time_min: Optional[float] = None
    reason: Optional[str] = None
    baseline_facility_id: Optional[str] = None
    baseline_path_nodes: List[int] = field(default_factory=list)
    baseline_time_min: Optional[float] = None
    baseline_blocked_edges: List[str] = field(default_factory=list)
    baseline_drivable: bool = False
    unreachable_facilities: List[Dict[str, str]] = field(default_factory=list)


def _pick(dist: Dict[int, float], paths: Dict[int, List[int]], facilities: pd.DataFrame
          ) -> Tuple[Optional[str], Optional[float], List[int]]:
    best = None
    for fac in facilities.itertuples(index=False):
        if fac.node_id not in dist:
            continue
        key = (dist[fac.node_id], VERIFICATION_RANK.get(fac.verification_status, 9), fac.facility_id)
        if best is None or key < best[0]:
            best = (key, fac.facility_id, fac.node_id)
    if best is None:
        return None, None, []
    return best[1], best[0][0] / 60.0, paths[best[2]]


def _cheapest_edges(G: nx.MultiDiGraph, path: List[int]):
    """The (u, v, key) actually used between consecutive path nodes: the quickest parallel edge."""
    for u, v in zip(path[:-1], path[1:]):
        key = min(G[u][v], key=lambda k: G[u][v][k].get("travel_time", float("inf")))
        yield u, v, key


def route_origin(G: nx.MultiDiGraph, G2: nx.MultiDiGraph, origin: int, facilities: pd.DataFrame,
                 classes: Dict[Tuple, str]) -> RouteResult:
    """Both routes for one origin node. `facilities` needs facility_id, node_id, verification_status."""
    res = RouteResult(origin=origin, reachable=False)
    if origin not in G or facilities.empty:
        res.reason = UNREACHABLE_REASON
        return res

    dist, paths = nx.single_source_dijkstra(G, origin, weight="travel_time")
    base_fid, base_t, base_path = _pick(dist, paths, facilities)
    res.baseline_facility_id, res.baseline_time_min, res.baseline_path_nodes = base_fid, base_t, base_path
    if base_path:
        blocked = [f"{u}-{v}-{k}" for u, v, k in _cheapest_edges(G, base_path)
                   if classes.get((u, v, k)) == "blocked"]
        res.baseline_blocked_edges = blocked
        res.baseline_drivable = not blocked

    if origin not in G2:
        res.reason = UNREACHABLE_REASON
        res.unreachable_facilities = [{"facility_id": f, "reason": "ORIGIN_CUT_OFF"} for f in facilities["facility_id"]]
        return res
    dist2, paths2 = nx.single_source_dijkstra(G2, origin, weight="travel_time")
    fid, t, path = _pick(dist2, paths2, facilities)
    res.unreachable_facilities = [
        {"facility_id": f.facility_id, "reason": "NO_PATH_AFTER_FLOODING"}
        for f in facilities.itertuples(index=False) if f.node_id not in dist2
    ]
    if fid is None:
        res.reason = UNREACHABLE_REASON
        return res
    res.reachable, res.facility_id, res.time_min, res.path_nodes = True, fid, t, path
    return res


def choose_facilities(G2: nx.MultiDiGraph, origins: List[int], facilities: pd.DataFrame) -> List[Optional[str]]:
    """Facility chosen for each origin node on graph G2, using one search per facility on the reversed
    graph (a handful of searches instead of one per origin). Same rule as route_origin: least travel
    time, then verification rank, then facility_id. None where no suitable facility is reachable."""
    R = G2.reverse(copy=False)
    dist_by_fac = {}
    for fac in facilities.itertuples(index=False):
        dist_by_fac[fac.facility_id] = nx.single_source_dijkstra_path_length(R, fac.node_id, weight="travel_time") \
            if fac.node_id in R else {}
    rank = {f.facility_id: VERIFICATION_RANK.get(f.verification_status, 9) for f in facilities.itertuples(index=False)}
    chosen: List[Optional[str]] = []
    for o in origins:
        best = None
        for fid, dist in dist_by_fac.items():
            if o in dist:
                key = (dist[o], rank[fid], fid)
                if best is None or key < best:
                    best = key
        chosen.append(None if best is None else best[2])
    return chosen


def path_coords(G: nx.MultiDiGraph, path: List[int], ndigits: int = 5) -> List[List[float]]:
    """[lon, lat] points along a node path, following each road's stored shape where it has one."""
    if not path:
        return []
    if len(path) == 1:
        return [[round(G.nodes[path[0]]["x"], ndigits), round(G.nodes[path[0]]["y"], ndigits)]]
    pts: List[List[float]] = []
    for u, v, key in _cheapest_edges(G, path):
        data = G[u][v][key]
        geom = data.get("geometry")
        if geom is not None:
            coords = list(geom.coords)
            # stored shapes run in the direction of the original way; flip if this edge is the reverse
            if (coords[0][0] - G.nodes[u]["x"]) ** 2 + (coords[0][1] - G.nodes[u]["y"]) ** 2 > \
               (coords[-1][0] - G.nodes[u]["x"]) ** 2 + (coords[-1][1] - G.nodes[u]["y"]) ** 2:
                coords.reverse()
        else:
            coords = [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
        for x, y in coords:
            p = [round(x, ndigits), round(y, ndigits)]
            if not pts or pts[-1] != p:
                pts.append(p)
    return pts


def edge_coords(G: nx.MultiDiGraph, edge_ids: List[str], ndigits: int = 5) -> List[List[List[float]]]:
    """Line segments for edge ids of the form 'u-v-key' (used to draw blocked roads)."""
    out = []
    for eid in edge_ids:
        u, v, key = (int(p) for p in eid.split("-"))
        out.append(path_coords(G, [u, v]) if G.has_edge(u, v, key) else [])
    return [seg for seg in out if seg]

"""Synthetic fixtures with hand-checkable numbers (blueprint Section 10.2)."""
import math

import networkx as nx
from shapely.geometry import LineString

# a 5 x 5 grid just inside the study zone (about 220 m between neighbours)
LON0, LAT0, STEP = 80.220, 13.030, 0.002
SPEED_KPH = 30.0


def _distance_m(lon1, lat1, lon2, lat2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def make_grid_graph(n: int = 5) -> nx.MultiDiGraph:
    """An n x n two-way grid shaped like an OSMnx graph: node x/y, edge length, speed_kph, travel_time."""
    G = nx.MultiDiGraph(crs="EPSG:4326")
    for row in range(n):
        for col in range(n):
            G.add_node(row * n + col, x=LON0 + col * STEP, y=LAT0 + row * STEP)

    def link(a, b):
        xa, ya, xb, yb = G.nodes[a]["x"], G.nodes[a]["y"], G.nodes[b]["x"], G.nodes[b]["y"]
        length = _distance_m(xa, ya, xb, yb)
        travel = length / (SPEED_KPH / 3.6)
        for u, v, (x1, y1, x2, y2) in ((a, b, (xa, ya, xb, yb)), (b, a, (xb, yb, xa, ya))):
            G.add_edge(u, v, 0, length=length, speed_kph=SPEED_KPH, travel_time=travel,
                       highway="residential", geometry=LineString([(x1, y1), (x2, y2)]))

    for row in range(n):
        for col in range(n):
            node = row * n + col
            if col + 1 < n:
                link(node, node + 1)
            if row + 1 < n:
                link(node, node + n)
    return G

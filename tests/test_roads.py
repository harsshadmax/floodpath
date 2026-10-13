"""Road graph tests (blueprint 4.3). Unit tests use the synthetic grid; the integration test uses the
cached real graph if it exists (python scripts/build_phase2.py) and is skipped otherwise."""
import json

import networkx as nx
import osmnx as ox
import pytest

from src import roads
from tests.fixtures import SPEED_KPH, make_grid_graph


def test_grid_has_expected_size_and_positive_times():
    G = make_grid_graph(5)
    assert G.number_of_nodes() == 25
    assert G.number_of_edges() == 2 * (2 * 5 * 4)  # 40 undirected links, two directions each
    assert all(d["travel_time"] > 0 for _, _, d in G.edges(data=True))


def test_shortest_path_exists_and_matches_hand_calculation():
    G = make_grid_graph(5)
    path = nx.shortest_path(G, 0, 24, weight="travel_time")
    assert path[0] == 0 and path[-1] == 24 and len(path) == 9  # 4 steps right + 4 steps up
    seconds = nx.shortest_path_length(G, 0, 24, weight="travel_time")
    one_step = G[0][1][0]["travel_time"]
    assert seconds > 8 * one_step * 0.9  # horizontal and vertical steps differ slightly in metres
    assert abs(G[0][1][0]["length"] / (SPEED_KPH / 3.6) - one_step) < 1e-9


def test_graphml_roundtrip_keeps_counts(tmp_path):
    G = make_grid_graph(4)
    path = tmp_path / "grid.graphml"
    ox.save_graphml(G, path)
    loaded = roads.load_graph(path)
    assert loaded.number_of_nodes() == G.number_of_nodes()
    assert loaded.number_of_edges() == G.number_of_edges()


def test_edges_geojson_has_unique_ids_and_light_geometry(tmp_path):
    G = make_grid_graph(4)
    out = tmp_path / "roads.geojson"
    n = roads.edges_geojson(G, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert n == len(data["features"]) == G.number_of_edges()
    ids = [f["properties"]["edge_id"] for f in data["features"]]
    assert len(set(ids)) == len(ids)
    assert all(f["properties"]["highway"] == "residential" for f in data["features"])


def test_summary_counts_components():
    s = roads.summarize(make_grid_graph(5))
    assert s["nodes"] == 25 and s["strongly_connected_components"] == 1 and s["largest_scc_nodes"] == 25


@pytest.mark.skipif(not roads.GRAPH_PATH.exists(), reason="real graph not built yet (scripts/build_phase2.py)")
def test_real_graph_is_usable():
    G = roads.load_graph()
    assert 1000 < G.number_of_edges() <= roads.MAX_EDGES
    assert all(float(d["travel_time"]) > 0 for _, _, d in G.edges(data=True))
    biggest = max(nx.strongly_connected_components(G), key=len)
    nodes = sorted(biggest)
    assert len(nodes) > 500
    assert nx.has_path(G, nodes[0], nodes[-1])

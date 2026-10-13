"""Isolation view on the synthetic grid and the Section 5.7.5 worked example (T-19 to T-26)."""
from dataclasses import replace

import pandas as pd
import pytest

from config import CONFIG
from src import isolation
from tests.fixtures import make_grid_graph


def cut_node(G, node):
    G2 = G.copy()
    G2.remove_edges_from([(u, v, k) for u, v, k in list(G2.edges(keys=True)) if node in (u, v)])
    return G2


def test_t19_states_isolated_ok_and_baseline_disconnected():
    G = make_grid_graph()
    G.add_node(99, x=80.25, y=13.05)  # no roads at all: disconnected even without flooding
    G2 = cut_node(G, 12)
    st = isolation.node_states(G, G2, [24])
    assert st[12] == "isolated" and st[0] == "ok" and st[99] == "baseline_disconnected"


def test_t20_delayed_uses_threshold():
    G = make_grid_graph()
    G2 = G.copy()
    for u, v, k in list(G2.edges(keys=True)):
        if 24 in (u, v):
            G2[u][v][k]["travel_time"] += 20 * 60  # facility access slowed by 20 minutes
    st = isolation.node_states(G, G2, [24])
    assert st[0] == "delayed"
    cfg = replace(CONFIG, ISOLATION_DELAY_MIN=30.0)
    assert isolation.node_states(G, G2, [24], cfg)[0] == "ok"


def test_t21_baseline_disconnected_never_counted_as_isolated():
    G = make_grid_graph()
    G.add_node(99, x=80.2201, y=13.0301)
    df, _ = isolation.compute(G, cut_node(G, 12), [24], replace(CONFIG, MIN_ELIGIBLE_NODES_PER_UNIT=1))
    assert df["nodes_baseline_disconnected"].sum() == 1
    assert df["nodes_isolated"].sum() == 1  # only node 12


def test_t22_worked_example_ranks_z_x_y():
    df = pd.DataFrame({"unit_id": ["X", "Y", "Z"], "population": [40000.0, 90000.0, 20000.0],
                       "isolated_share": [0.25, 0.05, 1.0], "delayed_share": [0.15, 0.0, 0.0]})
    ranked = isolation.rank_units(df)
    assert list(ranked["unit_id"]) == ["Z", "X", "Y"]
    assert list(ranked["priority_score"]) == pytest.approx([20000, 13000, 4500])
    assert list(ranked["estimated_people_isolated"]) == pytest.approx([20000, 10000, 4500])


def test_t22_full_cut_outranks_partial_and_ties_follow_order():
    df = pd.DataFrame({"unit_id": ["b", "a", "c"], "population": [10.0, 10.0, 10.0],
                       "isolated_share": [1.0, 0.5, 1.0], "delayed_share": [0.0, 0.0, 0.0]})
    ranked = isolation.rank_units(df)
    assert list(ranked["unit_id"]) == ["b", "c", "a"]  # tie b/c goes to unit_id


def test_t23_people_never_exceed_population_and_shares_bounded():
    G = make_grid_graph()
    df, _ = isolation.compute(G, cut_node(G, 12), [24], replace(CONFIG, MIN_ELIGIBLE_NODES_PER_UNIT=1))
    assert (df["estimated_people_isolated"] <= df["population"]).all()
    assert df["isolated_share"].between(0, 1).all() and df["delayed_share"].between(0, 1).all()


def test_t24_small_units_are_excluded_with_warning():
    G = make_grid_graph()
    cfg = replace(CONFIG, MIN_ELIGIBLE_NODES_PER_UNIT=10_000)
    with pytest.raises(isolation.IsolationError) as err:
        isolation.compute(G, G, [24], cfg)
    assert err.value.code == "UNITS_NOT_AVAILABLE"


def test_t25_no_flood_means_no_isolation_and_graph_unchanged():
    G = make_grid_graph()
    n_edges = G.number_of_edges()
    df, _ = isolation.compute(G, G, [24], replace(CONFIG, MIN_ELIGIBLE_NODES_PER_UNIT=1))
    assert df["nodes_isolated"].sum() == 0 and df["nodes_delayed"].sum() == 0
    assert G.number_of_edges() == n_edges


def test_t26_cells_geojson_matches_units_and_is_reproducible():
    G = make_grid_graph()
    cfg = replace(CONFIG, MIN_ELIGIBLE_NODES_PER_UNIT=1)
    df, _ = isolation.compute(G, G, [24], cfg)
    gj = isolation.cells_geojson(G, list(df["unit_id"]), cfg)
    assert {f["properties"]["unit_id"] for f in gj["features"]} == set(df["unit_id"])
    again, _ = isolation.compute(G, G, [24], cfg)
    assert df.equals(again)

"""Metrics on the synthetic grid with hand-checkable numbers (T-10, T-11, T-12)."""
from dataclasses import replace

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Point

from config import CONFIG
from src import flood, metrics
from tests.fixtures import make_grid_graph


def _facilities(nodes):
    return pd.DataFrame({"facility_id": [f"F{i + 1:02d}" for i in range(len(nodes))], "node_id": nodes,
                         "verification_status": ["unverified"] * len(nodes)})


def _origins(nodes, weights=None):
    return pd.DataFrame({"origin_id": [f"O{i + 1:02d}" for i in range(len(nodes))], "node_id": nodes,
                         "population_weight": weights or [1.0] * len(nodes)})


def _disc(G, node, r):
    p = gpd.GeoSeries([Point(G.nodes[node]["x"], G.nodes[node]["y"])], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
    return p.buffer(r)


def test_no_flood_means_no_change():
    G = make_grid_graph()
    fac, org = _facilities([24]), _origins([0, 4, 12])
    _, res = metrics.route_all(G, Point().buffer(0), org, fac)
    m = metrics.scenario_metrics(res, org, fac)
    assert m["m2_false_route_rate"] == 0
    assert m["m3_reach_any"] == 1
    assert m["m1_time_increase_min"]["mean"] == 0
    assert m["m4_coverage_difference"] == 0


def test_t10_travel_time_increase_is_difference_of_routes():
    G = make_grid_graph()
    fac, org = _facilities([24]), _origins([0])
    _, base = metrics.route_all(G, Point().buffer(0), org, fac)
    # block the centre node: origin 0 still reaches 24 around the edge, same length on a grid -> 0 extra
    _, res = metrics.route_all(G, _disc(G, 12, 300), org, fac)
    assert res[0].reachable
    m = metrics.scenario_metrics(res, org, fac)
    assert m["m1_time_increase_min"]["mean"] == pytest.approx(res[0].time_min - base[0].time_min, abs=0.01)
    assert m["m1_time_increase_min"]["n"] == 1


def test_t11_coverage_and_reachability_weights():
    G = make_grid_graph()
    fac = _facilities([24])
    org = _origins([0, 12], weights=[1.0, 3.0])
    _, res = metrics.route_all(G, _disc(G, 12, 300), org, fac)  # origin 12 (weight 3) is cut off
    m = metrics.scenario_metrics(res, org, fac)
    assert res[1].reachable is False
    assert m["m3_reach_any"] == 0.5
    assert m["m4_coverage_flood_aware"] == pytest.approx(0.25)  # only the weight-1 origin is covered
    assert m["m3_reach_by_facility"]["F01"] == 0.5


def test_t12_robustness_same_seed_same_output_and_range():
    G = make_grid_graph()
    cfg = replace(CONFIG, ROBUSTNESS_RUNS=4)
    fac, org = _facilities([24, 20]), _origins([0, 6, 12, 18])
    zone = gpd.GeoSeries([flood.zone_polygon()], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
    feats = [_disc(G, n, 60) for n in (6, 7, 8, 11, 13, 16, 17, 18)]
    ranks = flood.draw_ranks(len(feats), 1)
    geom = flood.subset_geometry(feats, ranks, 0.35, zone)
    _, central = metrics.route_all(G, geom, org, fac, cfg)
    a = metrics.robustness(G, feats, ranks, zone, central, org, fac, cfg)
    b = metrics.robustness(G, feats, ranks, zone, central, org, fac, cfg)
    assert a == b
    assert 0 <= a["overall"] <= 1 and 0 <= a["share_changed_at_least_once"] <= 1
    assert len(a["per_origin"]) == 4 and a["runs"] == 4


def test_fast_chooser_matches_full_routing():
    from src import impact, route
    G = make_grid_graph()
    fac = _facilities([24, 20])
    org = _origins([0, 6, 12, 18, 23])
    table = impact.classify_edges(G, _disc(G, 12, 300))
    G2 = impact.apply_flood(G, table)
    full = [r.facility_id for r in metrics.route_all(G, _disc(G, 12, 300), org, fac)[1]]
    fast = route.choose_facilities(G2, [int(n) for n in org["node_id"]], fac)
    assert fast == full

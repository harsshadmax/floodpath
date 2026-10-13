"""Ward join: polygon and census tables, scaling to the zone, node assignment, origin weights."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

from src import wards
from tests.fixtures import LAT0, LON0, STEP, make_grid_graph

# two wards side by side across the fixture grid (lon 80.220 to 80.228, lat 13.030 to 13.038)
MID = LON0 + 2 * STEP
POLYS = gpd.GeoDataFrame({"ward_id": [1, 2], "zone": ["1-A", "1-A"],
                          "geometry": [box(LON0 - 0.001, LAT0 - 0.001, MID, LAT0 + 5 * STEP),
                                       box(MID, LAT0 - 0.001, LON0 + 5 * STEP, LAT0 + 5 * STEP)]}, crs="EPSG:4326")
POPS = pd.DataFrame({"ward_id": [1, 2], "population": [1000.0, 3000.0]})


def test_join_all_matched_and_report():
    joined, report = wards.join(POLYS, POPS)
    assert len(joined) == 2 and report["match_rate"] == 1.0 and report["polygons_without_census"] == []
    assert list(joined["ward_name"]) == ["Ward 1", "Ward 2"]


def test_join_fails_below_threshold():
    pops = pd.DataFrame({"ward_id": [1], "population": [1000.0]})
    with pytest.raises(wards.WardDataError) as err:
        wards.join(POLYS, pops, min_rate=0.9)
    assert err.value.code == "WARD_JOIN_FAILED"


def test_census_blocks_are_summed_per_ward(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("Location Code,Name of Town,Ward Number,Enumberation Block,Total Population,SC Population,ST Population\n"
                 "1,C,1,EB1,500,1,-\n1,C,1,EB2,\"1,500\",1,-\n1,C,2,EB3,700,1,-\n1,C,Total,EBX,9999,1,-\n", encoding="utf-8")
    got = wards.load_populations(p).set_index("ward_id")["population"]
    assert got[1] == 2000 and got[2] == 700 and len(got) == 2  # non-numeric "Total" row ignored


def test_zone_scaling_uses_area_inside_the_zone():
    joined, _ = wards.join(POLYS, POPS)
    # a zone covering only the western half of ward 2 and nothing of ward 1
    from dataclasses import replace
    from config import CONFIG
    cfg = replace(CONFIG, STUDY_BBOX=(MID, LAT0 - 0.001, MID + 1.5 * STEP, LAT0 + 5 * STEP))
    scaled = wards.zone_scaled(joined, cfg)
    assert list(scaled["ward_id"]) == [2]
    assert 0.35 < scaled.loc[0, "inside_fraction"] < 0.65
    assert scaled.loc[0, "population_in_zone"] == pytest.approx(3000 * scaled.loc[0, "inside_fraction"], abs=1)


def test_nodes_are_assigned_and_origin_weights_share_ward_population():
    G = make_grid_graph()
    joined, _ = wards.join(POLYS, POPS)
    joined["inside_fraction"] = 1.0
    joined["population_in_zone"] = joined["population"]
    joined["geometry_in_zone"] = joined.geometry
    assign = wards.assign_nodes(G, joined)
    assert assign[0] == 1 and assign[4] == 2 and all(v is not None for v in assign.values())
    origins = pd.DataFrame({"origin_id": ["O1", "O2", "O3"], "node_id": [0, 1, 4]})  # two in ward 1, one in ward 2
    out = wards.attach_to_origins(origins, assign, joined)
    assert list(out["population_weight"]) == [500.0, 500.0, 3000.0]  # ward 1 pop shared by its two origins
    assert out["population_weight"].sum() == 4000.0


def test_origin_outside_every_ward_raises():
    joined, _ = wards.join(POLYS, POPS)
    joined["inside_fraction"], joined["population_in_zone"] = 1.0, joined["population"]
    with pytest.raises(wards.WardDataError):
        wards.attach_to_origins(pd.DataFrame({"origin_id": ["O1"], "node_id": [0]}), {0: None}, joined)

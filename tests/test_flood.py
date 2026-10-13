"""Flood layer tests: T-06 (scenario ordering) and T-07 (schema), plus buffering and error cases."""
import math

import geopandas as gpd
import pytest
from shapely.geometry import GeometryCollection, LineString, Point, box

from config import CONFIG
from src import flood

ZONE = flood.zone_polygon()
CX, CY = 80.2375, 13.055  # near the middle of the zone


def components():
    inund = gpd.GeoDataFrame(geometry=[box(CX - 0.004, CY - 0.004, CX + 0.004, CY + 0.004)], crs="EPSG:4326")
    stag = gpd.GeoDataFrame(geometry=[Point(CX + 0.010, CY), Point(CX - 0.010, CY)], crs="EPSG:4326")
    hot = gpd.GeoDataFrame(geometry=[Point(CX, CY + 0.012)], crs="EPSG:4326")
    lines = gpd.GeoDataFrame(geometry=[LineString([(CX - 0.012, CY - 0.012), (CX + 0.012, CY - 0.012)])], crs="EPSG:4326")
    return {"inundation": inund, "stagnation": stag, "gcc_hotspots": hot, "crowd_lines": lines}


def test_point_buffer_area_matches_circle():
    pts = gpd.GeoDataFrame(geometry=[Point(CX, CY)], crs="EPSG:4326")
    area = flood.buffer_component(pts).iloc[0].area
    assert abs(area - math.pi * CONFIG.POINT_BUFFER_M**2) / area < 0.01


def test_line_buffer_area_matches_stadium():
    line = gpd.GeoDataFrame(geometry=[LineString([(CX, CY), (CX + 0.01, CY)])], crs="EPSG:4326")
    geom = flood.buffer_component(line).iloc[0]
    metric_len = gpd.GeoSeries(line.geometry, crs="EPSG:4326").to_crs(CONFIG.CRS_METRIC).iloc[0].length
    expected = metric_len * 2 * CONFIG.LINE_BUFFER_M + math.pi * CONFIG.LINE_BUFFER_M**2
    assert abs(geom.area - expected) / expected < 0.02


def test_unsupported_geometry_raises_data_shape_unexpected():
    bad = gpd.GeoDataFrame(geometry=[GeometryCollection([Point(CX, CY)])], crs="EPSG:4326")
    with pytest.raises(flood.DataShapeUnexpected):
        flood.buffer_component(bad)


def many_reports(n=300):
    # a spread of street-level reports so seeded subsets of 10/20/35% are non-empty and distinguishable
    pts = [Point(CX - 0.025 + 0.05 * (i % 20) / 20, CY - 0.03 + 0.06 * (i // 20) / 15) for i in range(n)]
    comps = components()
    comps["stagnation"] = gpd.GeoDataFrame(geometry=pts, crs="EPSG:4326")
    return comps


def test_t06_scenario_areas_are_ordered_and_nested():
    comps = many_reports()
    composite, areas = flood.build_composite(comps, ZONE)
    scen = flood.build_scenarios(comps, composite, ZONE)
    assert set(scen) == set(flood.SCENARIO_ORDER)
    assert 0 < scen["mild"].area <= scen["moderate"].area <= scen["severe"].area
    assert scen["mild"].area < scen["severe"].area
    # nested: every scenario lies inside the next one and inside the observed composite
    assert scen["mild"].difference(scen["moderate"].buffer(0.5)).is_empty
    assert scen["moderate"].difference(scen["severe"].buffer(0.5)).is_empty
    assert scen["severe"].difference(composite.buffer(0.5)).is_empty
    assert all(a > 0 for a in areas.values())


def test_scenarios_are_reproducible_with_the_seed():
    comps = many_reports()
    composite, _ = flood.build_composite(comps, ZONE)
    a = flood.build_scenarios(comps, composite, ZONE)
    b = flood.build_scenarios(comps, composite, ZONE)
    assert all(a[k].equals(b[k]) for k in a)


def test_scenarios_stay_inside_the_zone():
    comps = many_reports()
    composite, _ = flood.build_composite(comps, ZONE)
    zone_m = gpd.GeoSeries([ZONE], crs="EPSG:4326").to_crs(CONFIG.CRS_METRIC).iloc[0]
    for geom in flood.build_scenarios(comps, composite, ZONE).values():
        assert geom.difference(zone_m.buffer(0.5)).is_empty


def test_t07_schema_and_labels():
    comps = many_reports()
    composite, _ = flood.build_composite(comps, ZONE)
    for name, geom in flood.build_scenarios(comps, composite, ZONE).items():
        gdf = flood.to_gdf(geom, name)
        flood.validate_flood_gdf(gdf)
        assert gdf.crs.to_string() == "EPSG:4326"
        expected = "composite" if name == "observed" else "simulated"
        assert gdf.loc[0, "kind"] == expected
        assert gdf.loc[0, "date"] == flood.DATE_TEXT
        assert gdf.loc[0, "source"] == "D1"


def test_validate_rejects_bad_labels():
    composite, _ = flood.build_composite(components(), ZONE)
    gdf = flood.to_gdf(composite, "observed")
    gdf["kind"] = "real"
    with pytest.raises(flood.DataShapeUnexpected):
        flood.validate_flood_gdf(gdf)
    with pytest.raises(flood.DataShapeUnexpected):
        flood.validate_flood_gdf(gdf.drop(columns=["date"]))


def test_no_flood_data_inside_zone_raises():
    far = gpd.GeoDataFrame(geometry=[Point(80.0, 12.7)], crs="EPSG:4326")
    with pytest.raises(flood.NoFloodData):
        flood.build_composite({"stagnation": far}, ZONE)


@pytest.mark.skipif(
    not all((flood.PROCESSED / f"flood_{s}.geojson").exists() for s in flood.SCENARIO_ORDER),
    reason="real layers not built yet (scripts/build_phase2.py)",
)
def test_real_layers_satisfy_t06_and_t07():
    areas = {}
    for s in flood.SCENARIO_ORDER:
        gdf = gpd.read_file(flood.PROCESSED / f"flood_{s}.geojson")
        flood.validate_flood_gdf(gdf)
        areas[s] = gdf.to_crs(CONFIG.CRS_METRIC).geometry.area.sum()
    assert areas["observed"] > areas["severe"] >= areas["moderate"] >= areas["mild"] > 0

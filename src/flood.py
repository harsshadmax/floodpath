"""Flood layers, the composite observed layer, and the simulated scenarios (blueprint Section 4.4).

What the sources really are (found in PHASE 1, see docs/DATA_LIMITS.md):
  * inundation zone: MultiPolygons from NRSC via OpenCity, far wider than Chennai, no date;
  * GCC stagnation points and GCC hotspot points;
  * crowd-sourced flooding: LINES (flooded street segments), not points;
  * none of the files carries a date.
The "observed" scenario is therefore a COMPOSITE of these layers, not a single observation, and it
is NOT the 1-4 Dec 2015 peak (standing gap 3). Mild, moderate and severe are SIMULATED by buffering
the composite. All buffers are assumptions (config.py).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, box, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, Config, validate_config  # noqa: E402

RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# component name -> (raw file, confidence). Crowd-sourced and buffered point layers are low confidence;
# the NRSC polygons are medium (blueprint 3.2). The three district hotspot files are not used: they
# contain stray points far outside Chennai (docs/DATA_LIMITS.md).
SOURCES: Dict[str, Tuple[str, str]] = {
    "inundation": ("D1__Chennai_2015_Floods_Inundation_Zone.kml", "medium"),
    "stagnation": ("D1__GCC_Stagnation_Locations_in_2015.kml", "low"),
    "gcc_hotspots": ("D1__Chennai_2015_GCC_Area_Flood_Hotspots.kml", "low"),
    "crowd_lines": ("D1__Chennai_2015_Crowd-sourced_Flooding_Locations.kml", "low"),
}
DATE_TEXT = "2015 event (day unknown)"
SCENARIO_ORDER = ("observed", "mild", "moderate", "severe")
REQUIRED_COLUMNS = ("geometry", "source", "date", "confidence", "kind", "scenario")


class NoFloodData(RuntimeError):
    code = "NO_FLOOD_DATA_FOR_AREA"


class DataShapeUnexpected(RuntimeError):
    code = "DATA_SHAPE_UNEXPECTED"


def zone_polygon(cfg: Config = CONFIG) -> Polygon:
    validate_config(cfg, require_study_area=True)
    w, s, e, n = cfg.STUDY_BBOX  # type: ignore[misc]
    return box(w, s, e, n)


def load_source(name: str, raw_dir: Path = RAW) -> gpd.GeoDataFrame:
    path = raw_dir / SOURCES[name][0]
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing; run python src/fetch_data.py")
    return gpd.read_file(path, driver="KML")[["geometry"]]


def buffer_component(gdf: gpd.GeoDataFrame, cfg: Config = CONFIG) -> gpd.GeoSeries:
    """Turn raw geometries into flooded areas, in the metric CRS.

    Points get POINT_BUFFER_M, lines get LINE_BUFFER_M, polygons are used as given. Any other
    geometry type raises DATA_SHAPE_UNEXPECTED (blueprint DATA-6); nothing is guessed.
    """
    metric = gdf.to_crs(cfg.CRS_METRIC).geometry
    out: List[BaseGeometry] = []
    for geom in metric:
        if geom is None or geom.is_empty:
            continue
        kind = geom.geom_type
        if kind in ("Point", "MultiPoint"):
            out.append(geom.buffer(cfg.POINT_BUFFER_M))
        elif kind in ("LineString", "MultiLineString"):
            out.append(geom.buffer(cfg.LINE_BUFFER_M))
        elif kind in ("Polygon", "MultiPolygon"):
            out.append(geom if geom.is_valid else geom.buffer(0))
        else:
            raise DataShapeUnexpected(f"unsupported geometry type {kind}")
    return gpd.GeoSeries(out, crs=cfg.CRS_METRIC)


def build_composite(
    components: Dict[str, gpd.GeoDataFrame], zone_geo: Polygon, cfg: Config = CONFIG
) -> Tuple[BaseGeometry, Dict[str, float]]:
    """Union of all buffered components clipped to the zone, plus each component's area (km2) in the zone."""
    zone_m = gpd.GeoSeries([zone_geo], crs=cfg.CRS_GEO).to_crs(cfg.CRS_METRIC).iloc[0]
    parts: List[BaseGeometry] = []
    areas: Dict[str, float] = {}
    for name, gdf in components.items():
        buffered = buffer_component(gdf, cfg)
        if buffered.empty:
            areas[name] = 0.0
            continue
        clipped = unary_union(list(buffered)).intersection(zone_m)
        areas[name] = round(clipped.area / 1e6, 3) if not clipped.is_empty else 0.0
        if not clipped.is_empty:
            parts.append(clipped)
    if not parts:
        raise NoFloodData("no flood feature intersects the study zone")
    return unary_union(parts), areas


STREET_LEVEL = ("stagnation", "gcc_hotspots", "crowd_lines")


def street_features(components: Dict[str, gpd.GeoDataFrame], cfg: Config = CONFIG) -> List[BaseGeometry]:
    """Buffered street-level flood reports (metric CRS), in a fixed order, one geometry per report."""
    feats: List[BaseGeometry] = []
    for name in STREET_LEVEL:
        if name in components:
            feats.extend(g for g in buffer_component(components[name], cfg) if not g.is_empty)
    return feats


def draw_ranks(n: int, seed: int) -> np.ndarray:
    """One uniform number per report. A report is kept when its number is below the scenario share, so
    scenarios built from the same ranks are nested (mild inside moderate inside severe)."""
    return np.random.default_rng(seed).random(n)


def subset_geometry(features: List[BaseGeometry], ranks: np.ndarray, share: float, zone_m: BaseGeometry) -> BaseGeometry:
    kept = [f for f, r in zip(features, ranks) if r < share]
    if not kept:
        return Polygon()
    return unary_union(kept).intersection(zone_m)


def build_scenarios(
    components: Dict[str, gpd.GeoDataFrame], composite: BaseGeometry, zone_geo: Polygon, cfg: Config = CONFIG
) -> Dict[str, BaseGeometry]:
    """The observed composite plus mild, moderate and severe: seeded nested subsets of street-level reports."""
    zone_m = gpd.GeoSeries([zone_geo], crs=cfg.CRS_GEO).to_crs(cfg.CRS_METRIC).iloc[0]
    feats = street_features(components, cfg)
    ranks = draw_ranks(len(feats), cfg.RANDOM_SEED)
    out: Dict[str, BaseGeometry] = {"observed": composite}
    for name, share in cfg.SCENARIO_FEATURE_SHARE:
        out[name] = subset_geometry(feats, ranks, share, zone_m)
    return out


def to_gdf(geom_m: BaseGeometry, scenario: str, cfg: Config = CONFIG) -> gpd.GeoDataFrame:
    """One-row GeoDataFrame with the blueprint 3.2 provenance columns, in EPSG:4326."""
    kind = "composite" if scenario == "observed" else "simulated"
    gdf = gpd.GeoDataFrame(
        {
            "source": ["D1"],
            "date": [DATE_TEXT],
            "confidence": ["low"],  # the weakest component sets the confidence of the composite
            "kind": [kind],
            "scenario": [scenario],
        },
        geometry=[geom_m],
        crs=cfg.CRS_METRIC,
    )
    return gdf.to_crs(cfg.CRS_GEO)


def validate_flood_gdf(gdf: gpd.GeoDataFrame) -> None:
    """Blueprint test T-07: columns, enum values, valid non-empty geometry."""
    missing = [c for c in REQUIRED_COLUMNS if c not in gdf.columns]
    if missing:
        raise DataShapeUnexpected(f"flood layer missing columns {missing}")
    if not set(gdf["confidence"]) <= {"low", "medium", "high"}:
        raise DataShapeUnexpected("bad confidence value")
    if not set(gdf["kind"]) <= {"observed", "composite", "simulated"}:
        raise DataShapeUnexpected("bad kind value")
    if not set(gdf["scenario"]) <= set(SCENARIO_ORDER):
        raise DataShapeUnexpected("bad scenario value")
    if gdf.geometry.is_empty.any() or (~gdf.geometry.is_valid).any():
        raise DataShapeUnexpected("empty or invalid geometry")


def build_all(cfg: Config = CONFIG, raw_dir: Path = RAW, out_dir: Path = PROCESSED) -> Dict[str, object]:
    """Load sources, build composite and scenarios, write data/processed/flood_<scenario>.geojson."""
    validate_config(cfg, require_study_area=True)
    zone = zone_polygon(cfg)
    components = {}
    for name in SOURCES:
        gdf = load_source(name, raw_dir)
        # keep only features that touch the zone (speeds up buffering; the clip happens later)
        components[name] = gdf[gdf.intersects(zone)]
    composite, component_areas = build_composite(components, zone, cfg)
    scenarios = build_scenarios(components, composite, zone, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    stats: Dict[str, object] = {"component_area_km2_in_zone": component_areas, "scenario_area_km2": {}}
    zone_area_km2 = gpd.GeoSeries([zone], crs=cfg.CRS_GEO).to_crs(cfg.CRS_METRIC).iloc[0].area / 1e6
    stats["zone_area_km2"] = round(zone_area_km2, 1)
    stats["feature_counts_in_zone"] = {k: int(len(v)) for k, v in components.items()}
    for scenario, geom in scenarios.items():
        gdf = to_gdf(geom, scenario, cfg)
        validate_flood_gdf(gdf)
        gdf.to_file(out_dir / f"flood_{scenario}.geojson", driver="GeoJSON")
        stats["scenario_area_km2"][scenario] = round(geom.area / 1e6, 2)
    return stats


def export_web(cfg: Config = CONFIG, out_dir: Path = ROOT / "web" / "public" / "data", tolerance_m: float = 4.0) -> Dict[str, int]:
    """Light copies of the scenario layers for the map: simplified, coordinates rounded to 5 decimals."""
    out_dir.mkdir(parents=True, exist_ok=True)
    sizes: Dict[str, int] = {}
    for scenario in SCENARIO_ORDER:
        gdf = gpd.read_file(PROCESSED / f"flood_{scenario}.geojson")
        metric = gdf.to_crs(cfg.CRS_METRIC)
        metric["geometry"] = metric.geometry.simplify(tolerance_m, preserve_topology=True)
        light = metric.to_crs(cfg.CRS_GEO)
        payload = json.loads(light.to_json(drop_id=True))
        for feature in payload["features"]:
            feature["geometry"]["coordinates"] = _round(feature["geometry"]["coordinates"])
        text = json.dumps(payload, separators=(",", ":"))
        (out_dir / f"flood_{scenario}.geojson").write_text(text, encoding="utf-8")
        sizes[scenario] = len(text)
    return sizes


def _round(coords):
    if coords and isinstance(coords[0], (int, float)):
        return [round(coords[0], 5), round(coords[1], 5)]
    return [_round(c) for c in coords]


if __name__ == "__main__":
    print(json.dumps(build_all(), indent=2))

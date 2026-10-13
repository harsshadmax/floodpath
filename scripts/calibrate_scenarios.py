"""Show how the flooded area responds to the scenario buffer, to choose sensible mild/severe values.

Read-only. The observed composite comes from data/processed/flood_observed.geojson.
Usage: python scripts/calibrate_scenarios.py
"""
import sys
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG  # noqa: E402
from src import flood  # noqa: E402

zone_m = gpd.GeoSeries([flood.zone_polygon()], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
obs = gpd.read_file(ROOT / "data" / "processed" / "flood_observed.geojson").to_crs(CONFIG.CRS_METRIC).geometry.union_all()
base = obs.area
print(f"zone {zone_m.area / 1e6:.1f} km2 | observed composite {base / 1e6:.1f} km2 ({base / zone_m.area:.0%} of the zone)")
print(f"{'buffer m':>9} {'area km2':>9} {'% of zone':>10} {'x observed':>11} {'parts':>6}")
for b in (-100, -75, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 75, 100, 150):
    g = (obs.buffer(b) if b else obs).intersection(zone_m)
    parts = len(g.geoms) if hasattr(g, "geoms") else (0 if g.is_empty else 1)
    print(f"{b:>9} {g.area / 1e6:>9.1f} {g.area / zone_m.area:>10.0%} {g.area / base:>11.2f} {parts:>6}")

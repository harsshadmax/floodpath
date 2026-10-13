"""Inspect every KML in data/raw: driver, feature count, geometry types, columns, bounds, validity.

Blueprint DATA-6: log what each source file really contains; never assume.
Usage: python scripts/inspect_kml.py
"""
from pathlib import Path

import geopandas as gpd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

for path in sorted(RAW.glob("*.kml")):
    try:
        gdf = gpd.read_file(path, driver="KML")
    except Exception as exc:  # report and continue, never hide
        print(f"{path.name}: READ FAILED ({type(exc).__name__}: {str(exc)[:120]})")
        continue
    geom_types = gdf.geometry.geom_type.value_counts().to_dict() if len(gdf) else {}
    invalid = int((~gdf.geometry.is_valid).sum()) if len(gdf) else 0
    empty = int(gdf.geometry.is_empty.sum()) if len(gdf) else 0
    bounds = [round(float(v), 4) for v in gdf.total_bounds] if len(gdf) else None
    cols = [c for c in gdf.columns if c != "geometry"]
    print(f"{path.name}")
    print(f"   features={len(gdf)} crs={gdf.crs} geom={geom_types} invalid={invalid} empty={empty}")
    print(f"   bounds(w,s,e,n)={bounds}")
    print(f"   columns={cols[:10]}")

"""Find where the maternity point names live in the KML and score two compact central zones."""
import re
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
M = "EPSG:32644"

xml = (RAW / "D5__Chennai_Maternity_Hospitals_Map.kml").read_text(encoding="utf-8")
print("== raw maternity KML (first 1500 chars)")
print(xml[:1500])
print("... tags used:", sorted(set(re.findall(r"<(\w+)[ >]", xml)))[:30])

fac = gpd.read_file(RAW / "D5__Chennai_Maternity_Hospitals_Map.kml", driver="KML")
print("\n== all columns:", list(fac.columns))
for col in fac.columns:
    if col != "geometry":
        print(f"  {col}: {fac[col].tolist()}")

layers = {
    "stag": gpd.read_file(RAW / "D1__GCC_Stagnation_Locations_in_2015.kml", driver="KML"),
    "hot": gpd.read_file(RAW / "D1__Chennai_2015_GCC_Area_Flood_Hotspots.kml", driver="KML"),
    "crowd": gpd.read_file(RAW / "D1__Chennai_2015_Crowd-sourced_Flooding_Locations.kml", driver="KML"),
    "inund": gpd.read_file(RAW / "D1__Chennai_2015_Floods_Inundation_Zone.kml", driver="KML"),
}
union = layers["inund"].to_crs(M).geometry.union_all()
print("\n== compact central candidates")
for name, (w, s, e, n) in {
    "F central compact": (80.205, 13.010, 80.270, 13.100),
    "G central tight": (80.210, 13.012, 80.265, 13.095),
}.items():
    bb = gpd.GeoSeries([box(w, s, e, n)], crs="EPSG:4326")
    bbm = bb.to_crs(M).iloc[0]
    print(
        f"{name}: fac={int(fac.within(bb.iloc[0]).sum())} stag={int(layers['stag'].within(bb.iloc[0]).sum())} "
        f"hot={int(layers['hot'].within(bb.iloc[0]).sum())} crowd={int(layers['crowd'].intersects(bb.iloc[0]).sum())} "
        f"inund={union.intersection(bbm).area / bbm.area * 100:.1f}% area={bbm.area / 1e6:.0f} km2"
    )

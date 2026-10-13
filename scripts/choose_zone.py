"""Look inside the downloaded layers and score candidate study zones (blueprint Section 16.5, item 1).

Prints: the 5 maternity points, sample names/descriptions and date fields per flood layer, then for
each candidate bounding box: facilities inside, flood features inside, share of the zone covered by
the NRSC inundation polygons, and the zone area. Read-only; changes nothing.
"""
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
M = "EPSG:32644"


def load(name):
    return gpd.read_file(RAW / name, driver="KML")


fac = load("D5__Chennai_Maternity_Hospitals_Map.kml")
print("== maternity points")
for _, r in fac.iterrows():
    print(f"  {r['Name']!s:45.45} lon={r.geometry.x:.4f} lat={r.geometry.y:.4f}")

layers = {
    "stagnation": load("D1__GCC_Stagnation_Locations_in_2015.kml"),
    "gcc_hotspots": load("D1__Chennai_2015_GCC_Area_Flood_Hotspots.kml"),
    "crowd_lines": load("D1__Chennai_2015_Crowd-sourced_Flooding_Locations.kml"),
    "inundation": load("D1__Chennai_2015_Floods_Inundation_Zone.kml"),
}
print("\n== sample fields")
for key, g in layers.items():
    sample = g.iloc[0]
    print(f"  {key}: Name={str(sample['Name'])[:40]!r} description={str(sample['description'])[:90]!r}")
    print(f"      timestamp non-null={int(g['timestamp'].notna().sum())}/{len(g)} begin non-null={int(g['begin'].notna().sum())}")

inund = layers["inundation"].to_crs(M)
inund_union = inund.geometry.union_all()

candidates = {
    "A south corridor (Saidapet-Thoraipakkam-Mugalivakkam)": (80.150, 12.930, 80.270, 13.060),
    "B central (Saidapet-Purasaiwalkam-Shenoy Nagar)": (80.170, 13.000, 80.270, 13.110),
    "C compact south (Saidapet-Velachery-Thoraipakkam)": (80.200, 12.940, 80.260, 13.040),
    "D south-west (Mugalivakkam-Saidapet)": (80.140, 12.960, 80.240, 13.050),
    "E whole facility span": (80.150, 12.930, 80.270, 13.110),
}
print("\n== candidate zones")
print(f"{'zone':56} {'fac':>3} {'stag':>5} {'hot':>4} {'crowd':>6} {'inund%':>7} {'km2':>6}")
for name, (w, s, e, n) in candidates.items():
    bb = gpd.GeoSeries([box(w, s, e, n)], crs="EPSG:4326")
    bbm = bb.to_crs(M).iloc[0]
    area_km2 = bbm.area / 1e6
    n_fac = int(fac.within(bb.iloc[0]).sum())
    n_stag = int(layers["stagnation"].within(bb.iloc[0]).sum())
    n_hot = int(layers["gcc_hotspots"].within(bb.iloc[0]).sum())
    n_crowd = int(layers["crowd_lines"].intersects(bb.iloc[0]).sum())
    cover = inund_union.intersection(bbm).area / bbm.area * 100
    print(f"{name:56} {n_fac:>3} {n_stag:>5} {n_hot:>4} {n_crowd:>6} {cover:>6.1f}% {area_km2:>6.0f}")

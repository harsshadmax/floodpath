"""PHASE 9: both routes and explanation text for every simulated start and sample origin, per scenario.

Usage: python scripts/build_routes.py   (after build_phase2.py and build_phase3.py)
Writes web/public/data/routes.json. Observed composite is not routed on (see docs/DATA_LIMITS.md).
All starts are simulated; no real 108 data is used.
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import CONFIG  # noqa: E402
from src import explain, flood, impact, roads, route  # noqa: E402
from src import facilities as fac  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
WEB_DATA = ROOT / "web" / "public" / "data"
LANGS = ("en", "ta", "hi")


def main() -> None:
    t0 = time.time()
    G = roads.load_graph()
    suitable, excluded = fac.suitable_facilities(fac.load_facilities(), G)
    facilities = {f.facility_id: {"name": f.name, "verification": f.verification_status} for f in suitable.itertuples()}
    starts = fac.load_ambulance_starts()
    start_nodes, _ = fac.snap(G, starts["longitude"].values, starts["latitude"].values)
    origins = pd.read_csv(PROCESSED / "origins.csv")
    points = [{"id": s.start_id, "group": "start", "lat": s.latitude, "lon": s.longitude, "node": n}
              for s, n in zip(starts.itertuples(), start_nodes)]
    points += [{"id": o.origin_id, "group": "origin", "lat": o.latitude, "lon": o.longitude, "node": int(o.node_id)}
               for o in origins.itertuples()]

    zone = flood.zone_polygon()
    zone_m = gpd.GeoSeries([zone], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
    components = {}
    for name in flood.SOURCES:
        g = flood.load_source(name)
        components[name] = g[g.intersects(zone)]
    features = flood.street_features(components)
    ranks = flood.draw_ranks(len(features), CONFIG.RANDOM_SEED)

    out = {
        "generated_on": date.today().isoformat(),
        "facilities": [{"id": f.facility_id, "name": f.name, "lat": f.latitude, "lon": f.longitude,
                        "verification": f.verification_status, "tier": f.tier} for f in suitable.itertuples()],
        "excluded_facilities": excluded,
        "points": [{k: v for k, v in p.items() if k != "node"} | {"label": "simulated"} for p in points],
        "scenarios": {},
    }
    for scenario, share in CONFIG.SCENARIO_FEATURE_SHARE:
        geom = flood.subset_geometry(features, ranks, share, zone_m)
        table = impact.classify_edges(G, geom)
        G2 = impact.apply_flood(G, table)
        classes = impact.class_lookup(table)
        per_point = {}
        for p in points:
            r = route.route_origin(G, G2, p["node"], suitable, classes)
            result = {
                "reachable": r.reachable, "facility_id": r.facility_id,
                "time_min": None if r.time_min is None else round(r.time_min, 2),
                "baseline_facility_id": r.baseline_facility_id,
                "baseline_time_min": None if r.baseline_time_min is None else round(r.baseline_time_min, 2),
                "baseline_drivable": r.baseline_drivable, "n_blocked": len(r.baseline_blocked_edges),
                "blocked_edge_ids": r.baseline_blocked_edges,
                "unreachable": r.unreachable_facilities,
            }
            per_point[p["id"]] = result | {
                "path": route.path_coords(G2, r.path_nodes),
                "baseline_path": route.path_coords(G, r.baseline_path_nodes),
                "blocked_segments": route.edge_coords(G, r.baseline_blocked_edges),
                "explain": {lang: explain.explain(result, scenario, "simulated", "D1 (OpenCity, GCC)", facilities, lang)
                            for lang in LANGS},
            }
        out["scenarios"][scenario] = per_point
        print(scenario, "reachable", sum(v["reachable"] for v in per_point.values()), "of", len(per_point), flush=True)

    WEB_DATA.mkdir(parents=True, exist_ok=True)
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    (WEB_DATA / "routes.json").write_text(text, encoding="utf-8")
    print(f"routes.json {len(text) / 1024:.0f} KB in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()

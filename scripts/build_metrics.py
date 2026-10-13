"""PHASE 7: metrics and robustness per scenario, written for the dashboard.

Usage: python scripts/build_metrics.py   (after build_phase2.py and build_phase3.py)
Writes web/public/data/metrics.json and data/processed/metrics.json.
The observed composite is not routed on (it isolates every facility, see docs/DATA_LIMITS.md); only
the simulated scenarios mild, moderate and severe get metrics.
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
from src import facilities as fac  # noqa: E402
from src import flood, impact, metrics, roads  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
WEB_DATA = ROOT / "web" / "public" / "data"


def main() -> dict:
    t0 = time.time()
    G = roads.load_graph()
    df = fac.load_facilities()
    suitable, excluded = fac.suitable_facilities(df, G)
    origins = pd.read_csv(PROCESSED / "origins.csv")
    zone = flood.zone_polygon()
    zone_m = gpd.GeoSeries([zone], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
    components = {}
    for name in flood.SOURCES:
        g = flood.load_source(name)
        components[name] = g[g.intersects(zone)]
    features = flood.street_features(components)
    ranks = flood.draw_ranks(len(features), CONFIG.RANDOM_SEED)

    out = {"generated_on": date.today().isoformat(), "n_origins": len(origins), "n_reports": len(features),
           "facilities": [], "origins": [], "scenarios": {}}
    for f in suitable.itertuples():
        out["facilities"].append({"id": f.facility_id, "name": f.name, "lat": f.latitude, "lon": f.longitude,
                                  "verification": f.verification_status, "tier": f.tier, "snap_m": round(f.snap_m, 1)})
    out["excluded_facilities"] = excluded
    for o in origins.itertuples():
        out["origins"].append({"id": o.origin_id, "lat": round(o.latitude, 5), "lon": round(o.longitude, 5)})

    for name, share in CONFIG.SCENARIO_FEATURE_SHARE:
        geom = flood.subset_geometry(features, ranks, share, zone_m)
        table, results = metrics.route_all(G, geom, origins, suitable)
        m = metrics.scenario_metrics(results, origins, suitable)
        m["share_of_reports"] = share
        m["edge_classes"] = impact.class_counts(table)
        m["origins"] = [
            {"id": o.origin_id, "facility": r.facility_id, "reachable": r.reachable,
             "baseline_drivable": r.baseline_drivable, "time_min": None if r.time_min is None else round(r.time_min, 2),
             "baseline_time_min": None if r.baseline_time_min is None else round(r.baseline_time_min, 2),
             "blocked_on_baseline": len(r.baseline_blocked_edges)}
            for o, r in zip(origins.itertuples(), results)
        ]
        t1 = time.time()
        m["robustness"] = metrics.robustness(G, features, ranks, zone_m, results, origins, suitable)
        print(f"{name}: {json.dumps({k: v for k, v in m.items() if k.startswith('m')}, default=str)[:400]}")
        print(f"   robustness {m['robustness']['overall']} in {time.time() - t1:.0f}s", flush=True)
        out["scenarios"][name] = m

    text = json.dumps(out, indent=1)
    (PROCESSED / "metrics.json").write_text(text, encoding="utf-8")
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    (WEB_DATA / "metrics.json").write_text(text, encoding="utf-8")
    print(f"done in {time.time() - t0:.0f}s")
    return out


if __name__ == "__main__":
    main()

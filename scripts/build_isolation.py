"""PHASE 8: isolation priority tables for the simulated scenarios.

Usage: python scripts/build_isolation.py   (after build_phase2.py and build_phase3.py)
Writes data/processed/isolation_<scenario>.csv and web/public/data/isolation.json.
Units are 1 km grid cells with placeholder population 1.0 (ward join not loaded). Indicative only.
"""
import json
import sys
from datetime import date
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import CONFIG  # noqa: E402
from src import facilities as fac  # noqa: E402
from src import flood, impact, isolation, roads  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
WEB = ROOT / "web" / "public" / "data"


def main() -> None:
    G = roads.load_graph()
    suitable, _ = fac.suitable_facilities(fac.load_facilities(), G)
    nodes = [int(n) for n in suitable["node_id"]]
    zone = flood.zone_polygon()
    zone_m = gpd.GeoSeries([zone], crs=CONFIG.CRS_GEO).to_crs(CONFIG.CRS_METRIC).iloc[0]
    components = {}
    for name in flood.SOURCES:
        g = flood.load_source(name)
        components[name] = g[g.intersects(zone)]
    features = flood.street_features(components)
    ranks = flood.draw_ranks(len(features), CONFIG.RANDOM_SEED)

    out = {"generated_on": date.today().isoformat(), "grid_m": CONFIG.ISOLATION_FALLBACK_GRID_M,
           "delay_min": CONFIG.ISOLATION_DELAY_MIN, "delay_weight": CONFIG.ISOLATION_DELAY_WEIGHT,
           "top_k": CONFIG.ISOLATION_TOP_K, "population_basis": "placeholder", "scenarios": {}}
    unit_ids = set()
    for scenario, share in CONFIG.SCENARIO_FEATURE_SHARE:
        geom = flood.subset_geometry(features, ranks, share, zone_m)
        G2 = impact.apply_flood(G, impact.classify_edges(G, geom))
        df, warns = isolation.compute(G, G2, nodes)
        df.to_csv(PROCESSED / f"isolation_{scenario}.csv", index=False)
        unit_ids |= set(df["unit_id"])
        out["scenarios"][scenario] = {"units": json.loads(df.to_json(orient="records")),
                                      "warnings": sorted(set(warns)),
                                      "nodes_baseline_disconnected": int(df["nodes_baseline_disconnected"].sum()),
                                      "units_with_isolation": int((df["nodes_isolated"] > 0).sum())}
        top = df.head(3)[["unit_id", "isolated_share", "delayed_share", "priority_score"]].round(3).to_dict("records")
        print(scenario, "units", len(df), "with isolation", out["scenarios"][scenario]["units_with_isolation"], "top", top)
    out["cells"] = isolation.cells_geojson(G, sorted(unit_ids))
    (WEB / "isolation.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("isolation.json", round((WEB / "isolation.json").stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()

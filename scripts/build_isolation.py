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
from src import flood, impact, isolation, roads, wards  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
WEB = ROOT / "web" / "public" / "data"


def main() -> None:
    G = roads.load_graph()
    suitable, _ = fac.suitable_facilities(fac.load_facilities(), G)
    nodes = [int(n) for n in suitable["node_id"]]
    _, _, _, geoms = flood.routed_scenarios()

    # ward units with Census 2011 populations when the ward join works, else the 1 km grid with placeholders
    unit_kwargs, zone_wards = {}, None
    try:
        zone_wards, _ = wards.load_zone_wards()
        assign = wards.assign_nodes(G, zone_wards)
        pop = zone_wards.set_index("ward_id")["population_in_zone"]
        unit_kwargs = {
            "units": {n: (None if w is None else f"W{w}") for n, w in assign.items()},
            "populations": {f"W{w}": float(p) for w, p in pop.items()},
            "unit_names": {f"W{w}": f"Ward {w}" for w in pop.index},
        }
        print("units: wards with Census 2011 populations")
    except wards.WardDataError as exc:
        print("units: 1 km grid with placeholder weights (", exc, ")")
    out = {"generated_on": date.today().isoformat(), "grid_m": CONFIG.ISOLATION_FALLBACK_GRID_M,
           "delay_min": CONFIG.ISOLATION_DELAY_MIN, "delay_weight": CONFIG.ISOLATION_DELAY_WEIGHT,
           "top_k": CONFIG.ISOLATION_TOP_K,
           "population_basis": "ward_census_2011" if unit_kwargs else "placeholder", "scenarios": {}}
    unit_ids = set()
    for scenario, geom in geoms.items():
        G2 = impact.apply_flood(G, impact.classify_edges(G, geom))
        df, warns = isolation.compute(G, G2, nodes, **unit_kwargs)
        df.to_csv(PROCESSED / f"isolation_{scenario}.csv", index=False)
        unit_ids |= set(df["unit_id"])
        out["scenarios"][scenario] = {"units": json.loads(df.to_json(orient="records")),
                                      "warnings": sorted(set(warns)),
                                      "nodes_baseline_disconnected": int(df["nodes_baseline_disconnected"].sum()),
                                      "units_with_isolation": int((df["nodes_isolated"] > 0).sum())}
        top = df.head(3)[["unit_id", "isolated_share", "delayed_share", "priority_score"]].round(3).to_dict("records")
        print(scenario, "units", len(df), "with isolation", out["scenarios"][scenario]["units_with_isolation"], "top", top)
    out["cells"] = (isolation.wards_geojson(zone_wards, unit_ids) if unit_kwargs else isolation.cells_geojson(G, sorted(unit_ids)))
    (WEB / "isolation.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("isolation.json", round((WEB / "isolation.json").stat().st_size / 1024), "KB")


if __name__ == "__main__":
    main()

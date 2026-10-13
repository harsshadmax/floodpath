"""PHASE 8b: ward join. Checks the match, writes data/wards_population.csv and a join report.

Usage: python scripts/build_wards.py   (needs data/raw/wards/Wards-2008.geojson and census2011_ward.csv)
Then re-run build_phase3.py, build_metrics.py, build_routes.py, build_isolation.py, build_audit.py so the
sample origins, metrics and isolation view use ward populations instead of placeholder weights.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import wards  # noqa: E402


def main() -> None:
    joined, report = wards.load_joined()
    wards.write_population_csv(joined)
    zone_wards = wards.zone_scaled(joined)
    report["wards_touching_zone"] = int(len(zone_wards))
    report["zone_population_estimate"] = int(zone_wards["population_in_zone"].sum())
    report["wards_mostly_outside_zone"] = int((zone_wards["inside_fraction"] < 0.25).sum())
    out = ROOT / "data" / "processed" / "ward_join_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

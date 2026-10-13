"""PHASE 9: one audit document per scenario and start, for the Download audit log button.

Usage: python scripts/build_audit.py   (after build_routes.py and build_metrics.py)
Writes web/public/data/audit.json as {scenario: {point_id: document}}. The browser adds generated_at and
ui_language when the user downloads a document.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import audit, flood, roads  # noqa: E402
from src import facilities as fac  # noqa: E402

WEB = ROOT / "web" / "public" / "data"
RESULT_DROP = ("path", "baseline_path", "blocked_segments", "explain")


def main() -> None:
    routes = json.loads((WEB / "routes.json").read_text(encoding="utf-8"))
    metrics = json.loads((WEB / "metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((WEB / "manifest.json").read_text(encoding="utf-8"))
    G = roads.load_graph()
    suitable, excluded = fac.suitable_facilities(fac.load_facilities(), G)
    rows = json.loads(suitable.to_json(orient="records"))
    out = {}
    for scenario in flood.SCENARIO_ORDER:
        m = metrics["scenarios"].get(scenario)
        info = audit.flood_layer_info(scenario, manifest, m, metrics["n_reports"])
        out[scenario] = {}
        for p in routes["points"]:
            res = routes["scenarios"].get(scenario, {}).get(p["id"])
            res = None if res is None else {k: v for k, v in res.items() if k not in RESULT_DROP}
            out[scenario][p["id"]] = audit.build_audit(scenario, p, res, m, info, rows, excluded, population_basis=metrics.get("population_basis", "placeholder"))
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    (WEB / "audit.json").write_text(text, encoding="utf-8")
    print(f"audit.json {len(text) / 1024:.0f} KB, {sum(len(v) for v in out.values())} documents")


if __name__ == "__main__":
    main()

"""Write web/src/data/config.json: the assumptions in effect, the study zone and the dataset list.

The Data and limits page reads this file, so the web app always shows the same assumptions as the
Python analysis (blueprint Section 6.9). Run: python scripts/export_web_config.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, validate_config  # noqa: E402

validate_config(CONFIG)

payload = {
    "study": {"name": CONFIG.STUDY_AREA, "bbox": list(CONFIG.STUDY_BBOX) if CONFIG.STUDY_BBOX else None},
    "assumptions": [
        {"name": "FLOOD_FRACTION_AT_RISK", "value": CONFIG.FLOOD_FRACTION_AT_RISK},
        {"name": "FLOOD_FRACTION_BLOCKED", "value": CONFIG.FLOOD_FRACTION_BLOCKED},
        {"name": "AT_RISK_TIME_MULTIPLIER", "value": CONFIG.AT_RISK_TIME_MULTIPLIER},
        {"name": "POINT_BUFFER_M", "value": CONFIG.POINT_BUFFER_M},
        {"name": "LINE_BUFFER_M", "value": CONFIG.LINE_BUFFER_M},
        {"name": "SCENARIO_BUFFER_M", "value": dict(CONFIG.SCENARIO_BUFFER_M)},
        {"name": "COVERAGE_THRESHOLD_MIN", "value": CONFIG.COVERAGE_THRESHOLD_MIN},
        {"name": "N_ORIGINS", "value": CONFIG.N_ORIGINS},
        {"name": "ROBUSTNESS_RUNS", "value": CONFIG.ROBUSTNESS_RUNS},
        {"name": "RANDOM_SEED", "value": CONFIG.RANDOM_SEED},
    ],
    "datasets": [
        {
            "id": "D1",
            "name": "OpenCity Chennai Floods 2015 (7 KML files)",
            "typeKey": "badge.composite",
            "licence": "Dataset tagged Public Domain; portal says CC BY-NC-SA 4.0 and ODbL (conflict)",
        },
        {
            "id": "D5",
            "name": "OpenCity Chennai Maternity Hospitals Map (5 points)",
            "typeKey": None,
            "licence": "Public Domain tag; same portal-level conflict",
        },
        {
            "id": "D4",
            "name": "OpenStreetMap roads (PHASE 2)",
            "typeKey": None,
            "licence": "ODbL: credit OpenStreetMap contributors",
        },
    ],
}

out = ROOT / "web" / "src" / "data" / "config.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("wrote", out)

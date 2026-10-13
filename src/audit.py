"""Audit log for one selection (blueprint Section 7.2).

One JSON document answers: what was selected, which assumptions and datasets were in effect, what the
flood layer and facility list were, what the result and metrics were, and what the limits are. The
files are language-neutral (English keys and English limit text); the browser adds `generated_at` and
`ui_language` when the user downloads one. Nothing here is invented: every value is read from the
pipeline outputs written by build_phase2/3, build_metrics and build_routes.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from config import CONFIG, Config  # noqa: E402
from src import flood  # noqa: E402
from src.i18n import load_dictionary, t  # noqa: E402

APP_VERSION = "FloodPath-Care prototype (blueprint v3.x), PHASE 9"
SERVICE = "emergency_obstetric"
REQUIRED_FIELDS = ("generated_at", "app_version", "ui_language", "selection", "config", "datasets", "flood_layer",
                   "facilities", "result", "metrics", "limits", "warnings")

EXTRA_LIMITS = [
    "Facilities are a hand-checked proxy list of 5 GCC emergency obstetric units; only those on the road graph are routed on, and none is phone-verified.",
    "Mild, moderate and severe are seeded nested subsets (10%, 20%, 35%) of street-level flood reports. They are arbitrary sensitivity settings, not physical flood models and not predictions.",
    "The observed layer is a composite of OpenCity layers with no dates; it is not the 1-4 December 2015 peak and is not routed on.",
    "Edge thresholds (10% and 50% of length flooded), the 3x at-risk time multiplier and the 30-minute coverage threshold are assumptions, not standards.",
    "Travel times use free-flow speeds from OpenStreetMap, so they are comparative, not real response times.",
    "Population weights are placeholders (equal weights); coverage is a share of sample points, not of people.",
    "Sample origins are seeded graph nodes in the largest connected road component; all are near flooded areas.",
    "Tamil and Hindi interface text are draft translations until reviewed by fluent speakers.",
]


def config_dict(cfg: Config = CONFIG) -> Dict[str, object]:
    return json.loads(json.dumps(dataclasses.asdict(cfg)))


def datasets(raw_manifest: Path = ROOT / "data" / "raw" / "manifest.json", roads: Path = ROOT / "data" / "processed" / "roads.graphml") -> List[Dict[str, object]]:
    """Datasets actually used, with URL, licence, access date (file download date) and kind."""
    rows: List[Dict[str, object]] = []
    accessed = datetime.fromtimestamp(raw_manifest.stat().st_mtime, timezone.utc).date().isoformat() if raw_manifest.exists() else None
    used = {Path(v[0]).name for v in flood.SOURCES.values()} | {"D5__Chennai_Maternity_Hospitals_Map.kml"}
    if raw_manifest.exists():
        for m in json.loads(raw_manifest.read_text(encoding="utf-8")):
            if m["file"] in used:
                kind = "composite component" if m["dataset"] == "D1" else "facility list proxy"
                rows.append({"id": m["dataset"], "name": m["resource_name"], "url": m["url"], "file": m["file"],
                             "licence": "Dataset tagged Public Domain; portal says CC BY-NC-SA 4.0 and ODbL (conflict, see docs/SOURCES.md)",
                             "accessed": accessed, "kind": kind})
    osm_date = datetime.fromtimestamp(roads.stat().st_mtime, timezone.utc).date().isoformat() if roads.exists() else None
    rows.append({"id": "OSM", "name": "OpenStreetMap drivable roads (today's roads, not 2015)", "url": "https://www.openstreetmap.org/copyright",
                 "file": "roads.graphml", "licence": "ODbL", "accessed": osm_date, "kind": "road network"})
    return rows


def limits() -> Dict[str, object]:
    en = load_dictionary("en")
    return {"standing_gaps": [t(k, "en") for k in ("gap.facility_list", "gap.ambulance", "gap.peak", "gap.roads") if k in en],
            "additional": EXTRA_LIMITS,
            "translation_status": {"ta": load_dictionary("ta")["_meta"]["status"], "hi": load_dictionary("hi")["_meta"]["status"]}}


def flood_layer_info(scenario: str, manifest: Dict[str, object], metrics: Optional[Dict[str, object]], n_reports: int) -> Dict[str, object]:
    stats = manifest["flood"]["stats"]  # type: ignore[index]
    info: Dict[str, object] = {
        "scenario": scenario,
        "kind": "composite" if scenario == "observed" else "simulated",
        "date": flood.DATE_TEXT,
        "area_km2": stats["scenario_area_km2"][scenario],
        "zone_area_km2": stats["zone_area_km2"],
        "sources": [{"component": k, "file": v[0], "confidence": v[1]} for k, v in flood.SOURCES.items()],
        "feature_counts_in_zone": stats["feature_counts_in_zone"],
    }
    if scenario == "observed":
        info["routed"] = False
        info["note"] = "Union of all four components; shown on the map, not routed on."
    else:
        info["routed"] = True
        info["method"] = "seeded nested subset of street-level reports (stagnation points, GCC hotspots, crowd-sourced flooded segments)"
        info["share_of_reports"] = metrics["share_of_reports"] if metrics else None  # type: ignore[index]
        info["reports_total"] = n_reports
    return info


def build_audit(scenario: str, point: Dict[str, object], result: Optional[Dict[str, object]], metrics: Optional[Dict[str, object]],
                flood_info: Dict[str, object], facility_rows: List[Dict[str, object]], excluded: List[Dict[str, str]],
                cfg: Config = CONFIG) -> Dict[str, object]:
    """One audit document, without generated_at and ui_language (the browser fills those in)."""
    summary = None
    if metrics is not None:
        summary = {k: v for k, v in metrics.items() if k not in ("origins",)}
        summary["robustness"] = {k: v for k, v in metrics["robustness"].items() if k != "per_origin"}  # type: ignore[union-attr]
    return {
        "generated_at": None,
        "app_version": APP_VERSION,
        "ui_language": None,
        "selection": {"scenario": scenario, "origin_id": point["id"], "origin_group": point["group"], "latitude": point["lat"],
                      "longitude": point["lon"], "origin_label": "simulated", "service": SERVICE,
                      "include_unverified_facilities": cfg.INCLUDE_UNVERIFIED_FACILITIES},
        "config": config_dict(cfg),
        "datasets": datasets(),
        "flood_layer": flood_info,
        "facilities": {"used": facility_rows, "excluded": excluded},
        "result": result,
        "metrics": summary,
        "limits": limits(),
        "warnings": [],
    }

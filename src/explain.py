"""Explanation text for one route result (blueprint Section 7.1).

Template-based and built only from computed facts: every number or name in a sentence comes from the
result dictionary, nothing is generated freely and no language model is involved. The templates are
the `expl.*` keys of the three dictionaries; Tamil and Hindi are drafts until reviewed. Facility names
are never translated. Service, scenario, status and flood-layer kind are looked up by key.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.i18n import t  # noqa: E402

FACILITY_STATUS_KEY = {
    "phone_verified": "facility.verified",
    "source_listed": "facility.source_listed",
    "unverified": "facility.unverified",
}


def _minutes(x: float) -> str:
    return f"{x:.1f}"


def explain(result: Dict[str, object], scenario: str, kind: str, source: str, facilities: Dict[str, Dict[str, str]],
            lang: str, service: str = "emergency_obstetric") -> List[str]:
    """Sentences for one result.

    `result` keys used: reachable, facility_id, time_min, baseline_facility_id, baseline_time_min,
    baseline_drivable, n_blocked, unreachable (list of {facility_id, reason}).
    `facilities` maps facility_id to {name, verification}. `kind` is composite or simulated.
    """
    scen = t(f"scenario.{scenario}", lang)
    svc = t(f"service.{service}", lang)
    out: List[str] = []

    base_id = result.get("baseline_facility_id")
    if base_id and not result.get("baseline_drivable"):
        out.append(t("expl.baseline_blocked", lang, baseline_facility=facilities[base_id]["name"],
                     n_blocked=int(result["n_blocked"]), scenario=scen))  # type: ignore[arg-type]

    chosen = result.get("facility_id")
    if result.get("reachable") and chosen:
        name = facilities[chosen]["name"]  # type: ignore[index]
        time_min = float(result["time_min"])  # type: ignore[arg-type]
        if base_id is not None and result.get("baseline_time_min") is not None:
            delta = time_min - float(result["baseline_time_min"])  # type: ignore[arg-type]
            if round(abs(delta), 1) == 0:
                out.append(t("expl.reachable_same", lang, service=svc, facility=name, time=_minutes(time_min)))
            else:
                key = "expl.reachable_longer" if delta > 0 else "expl.reachable_shorter"
                out.append(t(key, lang, service=svc, facility=name, time=_minutes(time_min), delta=_minutes(abs(delta))))

    unreachable = result.get("unreachable") or []
    if unreachable:
        names = "; ".join(
            f"{facilities[u['facility_id']]['name']} ({t('reason.' + u['reason'], lang)})"  # type: ignore[index]
            for u in unreachable  # type: ignore[union-attr]
        )
        out.append(t("expl.unreachable_facilities", lang, k=len(unreachable), names=names))  # type: ignore[arg-type]

    shown = chosen or base_id
    status_key = FACILITY_STATUS_KEY.get(facilities[shown]["verification"], "facility.unverified") if shown else "facility.unverified"  # type: ignore[index]
    out.append(t("expl.status", lang, status=t(status_key, lang), kind=t(f"badge.{kind}", lang), source=source))

    if not result.get("reachable"):
        out.append(t("expl.unreachable_all", lang, scenario=scen))
    return out

"""Internationalisation helpers (blueprint Section 4.12, 6A).

English, Tamil and Hindi dictionaries live in i18n/{lang}.json. Tamil and Hindi strings are DRAFT
translations until a fluent reviewer signs them off in docs/TRANSLATION_REVIEW.md.

Functions
- t(key, lang, **params)   translated string with {placeholders} filled
- fmt_int(n)               Indian digit grouping with Western digits (12,34,567)
- fmt_pct(x)               a fraction as NN.N%
- escape_html(s)           escape a data string before placing it in custom HTML
- drain_warnings()         non-fatal codes raised since the last call (I18N_KEY_MISSING, ...)
"""
from __future__ import annotations

import html
import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List

SUPPORTED_LANGUAGES = ("en", "ta", "hi")
DEFAULT_LANGUAGE = "en"
I18N_DIR = Path(__file__).resolve().parent.parent / "i18n"
PLACEHOLDER = re.compile(r"\{(\w+)\}")

# Keys that must be reviewed by a fluent speaker before the demo is recorded (blueprint 6A.4).
# Widened in PHASE 8 to cover every text that carries a claim or a limit (a mistranslation that drops
# "simulated", "indicative", "not a prediction" or "placeholder" breaks the claims policy, blueprint 0.5).
CRITICAL_PREFIXES = ("gap.", "expl.", "reason.", "iso.limit")
CRITICAL_KEYS = (
    "banner.simulation",
    "note.indicative",
    "note.indicative_metrics",
    "label.placeholder_weights",
    "result.unreachable",
    "scenario.mild",
    "scenario.moderate",
    "scenario.severe",
    "kpi.not_routed",
    "kpi.note_feasibility",
    "iso.units_note",
    "iso.excluded_baseline",
    "metrics.note",
    "export.intro",
    "map.roads_note",
    "route.audit_hint",
    "chart.cut_off",
    "state.planned_not_built",
)

log = logging.getLogger("floodpath.i18n")
_warnings: List[str] = []


class I18NParamError(KeyError):
    """A placeholder in a translation had no matching keyword argument."""


@lru_cache(maxsize=None)
def load_dictionary(lang: str) -> Dict[str, str]:
    """Load one dictionary file. The _meta block is returned under the key '_meta'."""
    path = I18N_DIR / f"{lang}.json"
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def normalize_language(lang: str | None) -> str:
    """Return a supported language code, or English with an I18N_LANGUAGE_UNSUPPORTED warning."""
    if lang in SUPPORTED_LANGUAGES:
        return lang  # type: ignore[return-value]
    if lang is not None:
        _warn("I18N_LANGUAGE_UNSUPPORTED", f"unsupported language {lang!r}, using English")
    return DEFAULT_LANGUAGE


def _warn(code: str, message: str) -> None:
    _warnings.append(code)
    log.warning("%s: %s", code, message)


def drain_warnings() -> List[str]:
    """Return and clear the non-fatal warning codes collected so far."""
    out = list(_warnings)
    _warnings.clear()
    return out


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER.findall(text))


def t(key: str, lang: str = DEFAULT_LANGUAGE, **params: object) -> str:
    """Translate `key` into `lang`, falling back to English, then to the key itself.

    A fallback logs I18N_KEY_MISSING. A placeholder with no matching keyword argument raises
    I18NParamError, so a blank never reaches the screen.
    """
    lang = normalize_language(lang)
    text = load_dictionary(lang).get(key)
    if text is None or key == "_meta":
        _warn("I18N_KEY_MISSING", f"{key!r} missing in {lang}")
        text = load_dictionary(DEFAULT_LANGUAGE).get(key)
        if text is None or key == "_meta":
            _warn("I18N_KEY_MISSING", f"{key!r} missing in English")
            return key
    needed = placeholders(text)
    missing = needed - set(params)
    if missing:
        raise I18NParamError(f"{key}: missing parameter(s) {sorted(missing)}")
    return PLACEHOLDER.sub(lambda m: str(params[m.group(1)]), text)


def fmt_int(n: float) -> str:
    """Format a whole number with Indian digit grouping and Western digits (assumption A-18)."""
    value = int(round(n))
    sign = "-" if value < 0 else ""
    digits = str(abs(value))
    if len(digits) <= 3:
        return sign + digits
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while head:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return sign + ",".join(groups + [tail])


def fmt_pct(x: float) -> str:
    """Format a fraction (0.1234) as NN.N% (12.3%)."""
    return f"{x * 100:.1f}%"


def escape_html(value: object) -> str:
    """Escape a data string (facility name, ward name, file text) before use in HTML (I18N-14)."""
    return html.escape(str(value), quote=True)

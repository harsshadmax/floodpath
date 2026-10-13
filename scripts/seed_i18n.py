"""Seed i18n/en.json, ta.json, hi.json from the Section 6A.3 table of blueprint.md.

Usage: python scripts/seed_i18n.py <path to blueprint.md>

All Tamil and Hindi strings start as `draft` (blueprint I18N-13). Run once in PHASE 0;
afterwards edit the JSON files directly and keep the three key sets identical.
"""
import json
import re
import sys
from pathlib import Path

ROW = re.compile(r"^\|\s*`([a-z0-9_.]+)`\s*\|(.*)\|\s*$")


def parse(blueprint_text: str) -> dict:
    start = blueprint_text.index("### 6A.3 Initial Dictionary")
    end = blueprint_text.index("### 6A.4 Critical Keys")
    rows = {"en": {}, "ta": {}, "hi": {}}
    for line in blueprint_text[start:end].splitlines():
        m = ROW.match(line)
        if not m:
            continue
        key, rest = m.group(1), m.group(2)
        cells = [c.strip() for c in rest.split("|")]
        if len(cells) != 3:
            raise ValueError(f"Row for {key} has {len(cells)} cells, expected 3")
        for lang, value in zip(("en", "ta", "hi"), cells):
            if not value:
                raise ValueError(f"Empty {lang} string for {key}")
            rows[lang][key] = value
    return rows


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    rows = parse(text)
    out_dir = Path(__file__).resolve().parent.parent / "i18n"
    out_dir.mkdir(exist_ok=True)
    for lang, entries in rows.items():
        data = {
            "_meta": {
                "language": lang,
                "status": "draft" if lang != "en" else "reviewed",
                "reviewed_by": "" if lang != "en" else "source language",
                "reviewed_on": "",
            }
        }
        data.update(entries)
        (out_dir / f"{lang}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{lang}: {len(entries)} keys")


if __name__ == "__main__":
    main()

"""Copy i18n/{en,ta,hi}.json into web/src/i18n/ so Python and Next.js share one dictionary.

Run after any change to the dictionaries: python scripts/export_web_i18n.py
The Python tests (T-27 to T-29) guarantee key and placeholder parity; this script just copies.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "i18n"
DST = ROOT / "web" / "src" / "i18n"

DST.mkdir(parents=True, exist_ok=True)
keys = {}
for lang in ("en", "ta", "hi"):
    shutil.copyfile(SRC / f"{lang}.json", DST / f"{lang}.json")
    keys[lang] = len(json.loads((SRC / f"{lang}.json").read_text(encoding="utf-8"))) - 1
print("copied", keys, "->", DST)

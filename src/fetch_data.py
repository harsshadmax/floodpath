"""PHASE 1: download the small OpenCity files (D1 flood layers, D5 maternity KML).

Rules (blueprint DATA-3, DATA-4): raw files go to data/raw/ (gitignored); a single download over
MAX_DOWNLOAD_MB aborts; nothing is fetched from UNOSAT or the OSM PBF here. Resource lists are read
from the OpenCity CKAN API, so no download URL is hard-coded.
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List

import certifi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import CONFIG  # noqa: E402

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
API = "https://data.opencity.in/api/3/action/package_show?id={id}"
USER_AGENT = "FloodPath-Care/0.1 (student project; read-only research)"

# OpenCity dataset id -> blueprint dataset ID
DATASETS: Dict[str, str] = {
    "chennai-floods-2015-data": "D1",
    "chennai-healthcare-uphcs-and-uchcs": "D5",
}


class DownloadTooLarge(RuntimeError):
    code = "DOWNLOAD_TOO_LARGE"


def _context() -> ssl.SSLContext:
    return ssl.create_default_context(cafile=certifi.where())


def _open(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=60, context=_context())


def list_resources(dataset_id: str) -> List[dict]:
    with _open(API.format(id=dataset_id)) as resp:
        payload = json.load(resp)
    if not payload.get("success"):
        raise RuntimeError(f"CKAN API failed for {dataset_id}")
    return payload["result"]["resources"]


def safe_name(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return name or "resource"


def download(url: str, dest: Path, max_mb: int = CONFIG.MAX_DOWNLOAD_MB) -> int:
    """Download one file, aborting if it exceeds max_mb (checked on the header and while reading)."""
    limit = max_mb * 1024 * 1024
    with _open(url) as resp:
        length = resp.headers.get("Content-Length")
        if length and int(length) > limit:
            raise DownloadTooLarge(f"{url} is {int(length) / 1e6:.1f} MB, over the {max_mb} MB limit")
        data = bytearray()
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            data.extend(chunk)
            if len(data) > limit:
                raise DownloadTooLarge(f"{url} exceeded the {max_mb} MB limit while downloading")
    dest.write_bytes(data)
    return len(data)


def fetch_all() -> List[dict]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest: List[dict] = []
    for dataset_id, short_id in DATASETS.items():
        for res in list_resources(dataset_id):
            url = res.get("url", "")
            fmt = (res.get("format") or "").lower()
            if not url.lower().endswith(".kml") and fmt != "kml":
                continue  # only KML geodata in this phase
            fname = f"{short_id}__{safe_name(res.get('name') or Path(url).name)}.kml"
            dest = RAW_DIR / fname
            size = download(url, dest)
            manifest.append(
                {
                    "dataset": short_id,
                    "opencity_dataset_id": dataset_id,
                    "resource_name": res.get("name"),
                    "url": url,
                    "file": fname,
                    "bytes": size,
                }
            )
            print(f"{fname}: {size / 1e3:.0f} KB")
    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    total = sum(m["bytes"] for m in manifest)
    print(f"total: {total / 1e6:.2f} MB in {len(manifest)} files")
    return manifest


if __name__ == "__main__":
    fetch_all()

"""PHASE 2 pipeline: road graph + flood layers + scenarios, and the JSON the web map reads.

Usage: python scripts/build_phase2.py [--force-graph]
Writes: data/processed/roads.graphml, data/processed/flood_<scenario>.geojson,
        web/public/data/roads.geojson, web/public/data/flood_<scenario>.geojson, web/public/data/manifest.json
The first run downloads roads from OpenStreetMap (needs internet) and caches them.
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import CONFIG  # noqa: E402
from src import flood, roads  # noqa: E402

WEB_DATA = ROOT / "web" / "public" / "data"


def main(force_graph: bool = False) -> None:
    t0 = time.time()
    print("1/3 road graph ...")
    G = roads.build_graph(force=force_graph)
    graph_summary = roads.summarize(G)
    print("   ", graph_summary, f"({time.time() - t0:.0f}s)")

    print("2/3 flood layers and scenarios ...")
    stats = flood.build_all()
    print("   ", json.dumps(stats))

    print("3/3 web data ...")
    WEB_DATA.mkdir(parents=True, exist_ok=True)
    n_edges = roads.edges_geojson(G, WEB_DATA / "roads.geojson")
    sizes = flood.export_web()
    roads_kb = (WEB_DATA / "roads.geojson").stat().st_size / 1024
    manifest = {
        "generated_on": date.today().isoformat(),
        "study": {"name": CONFIG.STUDY_AREA, "bbox": list(CONFIG.STUDY_BBOX)},
        "roads": {"file": "roads.geojson", "features": n_edges, "kb": round(roads_kb), **graph_summary,
                  "note": "Current OpenStreetMap roads, not 2015 roads (standing gap 4)."},
        "flood": {
            "files": {s: f"flood_{s}.geojson" for s in flood.SCENARIO_ORDER},
            "kb": {s: round(v / 1024) for s, v in sizes.items()},
            "kinds": {"observed": "composite", "mild": "simulated", "moderate": "simulated", "severe": "simulated"},
            "date": flood.DATE_TEXT,
            "stats": stats,
            "note": "The observed layer is a composite of OpenCity layers, not the 1-4 Dec 2015 peak (standing gap 3).",
        },
        "assumptions": {
            "POINT_BUFFER_M": CONFIG.POINT_BUFFER_M,
            "LINE_BUFFER_M": CONFIG.LINE_BUFFER_M,
            "SCENARIO_BUFFER_M": dict(CONFIG.SCENARIO_BUFFER_M),
        },
    }
    (WEB_DATA / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"done in {time.time() - t0:.0f}s; roads.geojson {roads_kb:.0f} KB, flood kb {manifest['flood']['kb']}")


if __name__ == "__main__":
    main(force_graph="--force-graph" in sys.argv)

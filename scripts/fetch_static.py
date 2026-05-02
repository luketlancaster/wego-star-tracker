#!/usr/bin/env python3
"""Download the WeGo static GTFS zip and extract it into ./data/.

Also runs a cheap sanity check: route 90 (WeGo Star) should still exist and
should still serve 7 stops. Warns (does not fail) if either changes — that's
a signal to re-verify the constants in src/wego_metroboard/stations.py.
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

import requests

from wego_metroboard.feeds import GTFS_STATIC, WEGO_STAR_ROUTE_ID

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def download_and_extract() -> Path:
    print(f"GET {GTFS_STATIC}")
    resp = requests.get(GTFS_STATIC, timeout=30)
    resp.raise_for_status()
    print(f"  → {len(resp.content):,} bytes")

    DATA_DIR.mkdir(exist_ok=True)
    zip_path = DATA_DIR / "google_transit.zip"
    zip_path.write_bytes(resp.content)

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        zf.extractall(DATA_DIR)
    print(f"extracted to {DATA_DIR}")
    return DATA_DIR


def verify(data_dir: Path) -> None:
    routes_path = data_dir / "routes.txt"
    trips_path = data_dir / "trips.txt"
    stop_times_path = data_dir / "stop_times.txt"

    with routes_path.open() as f:
        route_ids = {row["route_id"] for row in csv.DictReader(f)}
    if WEGO_STAR_ROUTE_ID not in route_ids:
        print(
            f"WARN: route_id={WEGO_STAR_ROUTE_ID} not found in routes.txt "
            f"(found {sorted(route_ids)})"
        )
        return

    with trips_path.open() as f:
        star_trip_ids = {
            row["trip_id"] for row in csv.DictReader(f) if row["route_id"] == WEGO_STAR_ROUTE_ID
        }

    with stop_times_path.open() as f:
        star_stops = {
            row["stop_id"] for row in csv.DictReader(f) if row["trip_id"] in star_trip_ids
        }

    print(f"route 90 trips: {len(star_trip_ids)}, distinct stops: {len(star_stops)}")
    if len(star_stops) != 7:
        print(f"WARN: expected 7 stops on route 90, got {len(star_stops)}: {sorted(star_stops)}")


def main() -> int:
    data_dir = download_and_extract()
    verify(data_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())

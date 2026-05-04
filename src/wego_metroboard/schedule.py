"""Schedule-driven station lighting from static GTFS.

WeGo's GTFS-realtime feed does not include the WeGo Star (verified by
inspection of vehiclepositions.pb, tripupdates.pb, and the combined
trapezerealtimefeed.pb — only buses appear). So Phase 2 isn't a fallback,
it's the primary mechanism: load static GTFS at startup, figure out which
stations should currently have a train per schedule, light those LEDs.

The static feed gives arrival_time == departure_time at every stop (zero
modeled dwell). To produce a visible window, we pad each scheduled time
by DWELL_HALF_S seconds on each side.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from wego_metroboard.feeds import WEGO_STAR_ROUTE_ID

# Pad each scheduled time by this many seconds before/after to produce a
# visible "train at station" window. 60 s on each side ≈ a typical commuter
# rail dwell at an intermediate stop.
DWELL_HALF_S = 60

_WEEKDAY_COLS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


@dataclass(frozen=True)
class StopWindow:
    """A station "is occupied" between start_s and end_s, seconds since local midnight."""

    stop_id: str
    start_s: int
    end_s: int
    trip_id: str
    direction_id: int


def parse_gtfs_time(s: str) -> int:
    """GTFS time as seconds since local midnight. Handles leading whitespace
    and HH > 23 (e.g., 25:30:00 for trips that span midnight)."""
    h, m, sec = s.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(sec)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def active_service_ids(data_dir: Path, today: date) -> set[str]:
    """service_ids running on `today`, per calendar.txt + calendar_dates.txt."""
    weekday_col = _WEEKDAY_COLS[today.weekday()]
    today_str = today.strftime("%Y%m%d")

    services: set[str] = set()
    for row in _read_csv(data_dir / "calendar.txt"):
        if row[weekday_col] != "1":
            continue
        if row["start_date"] <= today_str <= row["end_date"]:
            services.add(row["service_id"])

    cd_path = data_dir / "calendar_dates.txt"
    if cd_path.exists():
        for row in _read_csv(cd_path):
            if row["date"] != today_str:
                continue
            if row["exception_type"] == "1":
                services.add(row["service_id"])
            elif row["exception_type"] == "2":
                services.discard(row["service_id"])
    return services


def windows_for_today(
    data_dir: Path,
    today: date,
    *,
    route_id: str = WEGO_STAR_ROUTE_ID,
    valid_stop_ids: set[str] | None = None,
    dwell_half_s: int = DWELL_HALF_S,
) -> list[StopWindow]:
    """Build the day's stop-occupied windows for the given route.

    `valid_stop_ids`, if provided, restricts output to those stops (typically
    the 7 wired stations).
    """
    services = active_service_ids(data_dir, today)
    if not services:
        return []

    trip_directions: dict[str, int] = {}
    for row in _read_csv(data_dir / "trips.txt"):
        if row["route_id"] == route_id and row["service_id"] in services:
            trip_directions[row["trip_id"]] = int(row["direction_id"])
    if not trip_directions:
        return []

    windows: list[StopWindow] = []
    for row in _read_csv(data_dir / "stop_times.txt"):
        trip_id = row["trip_id"]
        if trip_id not in trip_directions:
            continue
        stop_id = row["stop_id"]
        if valid_stop_ids is not None and stop_id not in valid_stop_ids:
            continue
        arr = parse_gtfs_time(row["arrival_time"])
        dep = parse_gtfs_time(row["departure_time"])
        windows.append(
            StopWindow(
                stop_id=stop_id,
                start_s=arr - dwell_half_s,
                end_s=dep + dwell_half_s,
                trip_id=trip_id,
                direction_id=trip_directions[trip_id],
            )
        )
    return windows


def active_stops_at(windows: list[StopWindow], now: datetime) -> set[str]:
    """stop_ids whose window contains `now` (interpreted in the agency's local time)."""
    now_s = now.hour * 3600 + now.minute * 60 + now.second
    return {w.stop_id for w in windows if w.start_s <= now_s <= w.end_s}

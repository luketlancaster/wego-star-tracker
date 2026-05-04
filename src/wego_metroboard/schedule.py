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


def active_stops_at(windows: list[StopWindow], now: datetime) -> dict[str, set[int]]:
    """stop_id → set of direction_ids whose window contains `now`.

    A station with both an inbound and outbound train scheduled simultaneously
    will appear with `{0, 1}`; the LED layer uses that to pick a "both
    directions" visual. Empty dict means board goes dark.
    """
    now_s = now.hour * 3600 + now.minute * 60 + now.second
    active: dict[str, set[int]] = {}
    for w in windows:
        if w.start_s <= now_s <= w.end_s:
            active.setdefault(w.stop_id, set()).add(w.direction_id)
    return active


def outbound_direction_id(
    data_dir: Path,
    *,
    route_id: str = WEGO_STAR_ROUTE_ID,
    services: set[str] | None = None,
    origin_stop_id: str = "MCSRVRF",
) -> int:
    """The GTFS direction_id for trips that originate at `origin_stop_id`.

    For WeGo Star, trips starting at Riverfront are the eastbound (outbound)
    trips. We infer rather than hardcode so the board stays correct if WeGo
    ever flips the 0/1 assignment. Short-turn outbounds (Riverfront → Mt.
    Juliet) still originate at Riverfront, so the outbound side is
    unambiguous; inbound trips may originate at Lebanon *or* Mt. Juliet.

    Raises ValueError if no direction (or more than one) has trips starting
    at `origin_stop_id` — that would indicate a feed change worth eyeballing.
    """
    trip_directions: dict[str, int] = {}
    for row in _read_csv(data_dir / "trips.txt"):
        if row["route_id"] != route_id:
            continue
        if services is not None and row["service_id"] not in services:
            continue
        trip_directions[row["trip_id"]] = int(row["direction_id"])

    first_stop: dict[str, tuple[int, str]] = {}
    for row in _read_csv(data_dir / "stop_times.txt"):
        trip_id = row["trip_id"]
        if trip_id not in trip_directions:
            continue
        seq = int(row["stop_sequence"])
        prev = first_stop.get(trip_id)
        if prev is None or seq < prev[0]:
            first_stop[trip_id] = (seq, row["stop_id"])

    direction_origins: dict[int, set[str]] = {}
    for trip_id, dir_id in trip_directions.items():
        seq_stop = first_stop.get(trip_id)
        if seq_stop is not None:
            direction_origins.setdefault(dir_id, set()).add(seq_stop[1])

    candidates = [d for d, origins in direction_origins.items() if origin_stop_id in origins]
    if len(candidates) != 1:
        raise ValueError(
            f"cannot determine outbound direction_id: trips originating at "
            f"{origin_stop_id!r} map to direction_ids {candidates}"
        )
    return candidates[0]

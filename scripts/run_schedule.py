#!/usr/bin/env python3
"""Phase 2: schedule-driven Metroboard.

WeGo's GTFS-realtime feed does not include the WeGo Star, so this is the
primary driver — not a fallback. Each cycle:

  1. Compute today's stop-occupied windows from static GTFS (rebuilt when
     the date rolls over).
  2. For each window containing `now`, light its station with a state
     that encodes direction:
       - solid on   = outbound (eastbound) only
       - slow blink = inbound (westbound) only
       - soft pulse = both directions overlapping
  3. Log a one-line summary.

SIGINT clears the board and exits cleanly. Run scripts/fetch_static.py
once to populate ./data/ before the first run; rerun periodically (or
schedule it) to pick up timetable changes.
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from datetime import date, datetime
from pathlib import Path
from types import FrameType
from zoneinfo import ZoneInfo

from wego_metroboard.gpio import configure_pin_factory
from wego_metroboard.schedule import (
    StopWindow,
    active_service_ids,
    active_stops_at,
    outbound_direction_id,
    windows_for_today,
)
from wego_metroboard.stations import BY_STOP_ID, STATIONS

configure_pin_factory()  # must run before importing PWMLED

from wego_metroboard.leds import StationLeds  # noqa: E402

POLL_S = 30.0
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AGENCY_TZ = ZoneInfo("America/Chicago")

log = logging.getLogger("metroboard")


def _format_active(active: dict[str, set[int]], outbound_id: int) -> str:
    if not active:
        return "(none)"
    parts: list[str] = []
    for s in STATIONS:
        dirs = active.get(s.stop_id)
        if not dirs:
            continue
        has_out = outbound_id in dirs
        has_in = any(d != outbound_id for d in dirs)
        tag = "↑↓" if has_out and has_in else ("↓" if has_out else "↑")
        parts.append(f"{s.name}({tag})")
    return ", ".join(parts)


def _load_today(today: date) -> tuple[list[StopWindow], int]:
    services = active_service_ids(DATA_DIR, today)
    windows = windows_for_today(DATA_DIR, today, valid_stop_ids=set(BY_STOP_ID))
    if not services or not windows:
        # No service today; outbound_id is unused but we still return something
        # consistent so the loop can short-circuit on an empty windows list.
        return windows, 0
    out_id = outbound_direction_id(DATA_DIR, services=services)
    return windows, out_id


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    if not (DATA_DIR / "stop_times.txt").exists():
        log.error("GTFS data not found in %s — run scripts/fetch_static.py first", DATA_DIR)
        return 1

    leds = StationLeds(STATIONS)

    def handle_sigint(_signum: int, _frame: FrameType | None) -> None:
        leds.all_off()
        log.info("interrupted; all LEDs off")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    log.info("schedule-driven mode, polling every %.0f s (Ctrl-C to stop)", POLL_S)

    current_date: date | None = None
    windows: list[StopWindow] = []
    outbound_id: int = 0

    try:
        while True:
            now = datetime.now(AGENCY_TZ)
            if now.date() != current_date:
                current_date = now.date()
                windows, outbound_id = _load_today(current_date)
                log.info(
                    "loaded %d stop-windows for %s (outbound direction_id=%d)",
                    len(windows),
                    current_date,
                    outbound_id,
                )

            active = active_stops_at(windows, now)
            leds.update(active, outbound_id)
            log.info("active = %s", _format_active(active, outbound_id))

            time.sleep(POLL_S)
    finally:
        leds.all_off()
    return 0


if __name__ == "__main__":
    sys.exit(main())

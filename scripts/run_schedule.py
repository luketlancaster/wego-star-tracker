#!/usr/bin/env python3
"""Phase 2: schedule-driven Metroboard.

WeGo's GTFS-realtime feed does not include the WeGo Star, so this is the
primary driver — not a fallback. Each cycle:

  1. Compute today's stop-occupied windows from static GTFS (rebuilt when
     the date rolls over).
  2. For each window containing `now`, light its station.
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
from wego_metroboard.schedule import StopWindow, active_stops_at, windows_for_today
from wego_metroboard.stations import BY_STOP_ID, STATIONS

configure_pin_factory()  # must run before importing LED

from gpiozero import LED  # noqa: E402

POLL_S = 30.0
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AGENCY_TZ = ZoneInfo("America/Chicago")

log = logging.getLogger("metroboard")


def _format_active(stop_ids: set[str]) -> str:
    if not stop_ids:
        return "(none)"
    return ", ".join(s.name for s in STATIONS if s.stop_id in stop_ids)


def _update_leds(leds: dict[str, LED], active: set[str]) -> None:
    for stop_id, led in leds.items():
        if stop_id in active:
            led.on()
        else:
            led.off()


def _load_today(today: date) -> list[StopWindow]:
    return windows_for_today(DATA_DIR, today, valid_stop_ids=set(BY_STOP_ID))


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    if not (DATA_DIR / "stop_times.txt").exists():
        log.error("GTFS data not found in %s — run scripts/fetch_static.py first", DATA_DIR)
        return 1

    leds = {s.stop_id: LED(s.gpio) for s in STATIONS}

    def handle_sigint(_signum: int, _frame: FrameType | None) -> None:
        for led in leds.values():
            led.off()
        log.info("interrupted; all LEDs off")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    log.info("schedule-driven mode, polling every %.0f s (Ctrl-C to stop)", POLL_S)

    current_date: date | None = None
    windows: list[StopWindow] = []

    try:
        while True:
            now = datetime.now(AGENCY_TZ)
            if now.date() != current_date:
                current_date = now.date()
                windows = _load_today(current_date)
                log.info("loaded %d stop-windows for %s", len(windows), current_date)

            active = active_stops_at(windows, now)
            _update_leds(leds, active)
            log.info("active = %s", _format_active(active))

            time.sleep(POLL_S)
    finally:
        for led in leds.values():
            led.off()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Phase 1: 30 s polling loop driving the Metroboard from the WeGo realtime feed.

Each cycle:
  1. GET vehiclepositions.pb
  2. Filter to route 90 + STOPPED_AT
  3. Light LEDs for matching stops, turn the rest off
  4. Log a one-line summary

Network errors are logged and the loop continues on the next tick. SIGINT
turns every LED off and exits cleanly. WeGo Star runs Mon–Fri only — at
nights/weekends/holidays expect "active = (none)".
"""

from __future__ import annotations

import logging
import signal
import sys
import time
from types import FrameType

import requests

from wego_metroboard.feeds import fetch_vehicle_positions
from wego_metroboard.gpio import configure_pin_factory
from wego_metroboard.realtime import active_stop_ids
from wego_metroboard.stations import STATIONS

configure_pin_factory()  # must run before importing LED

from gpiozero import LED  # noqa: E402

POLL_S = 30.0
HTTP_TIMEOUT_S = 10.0

log = logging.getLogger("metroboard")


def _format_active(stop_ids: set[str]) -> str:
    if not stop_ids:
        return "(none)"
    # render in geographic order (west → east) regardless of set iteration
    return ", ".join(s.name for s in STATIONS if s.stop_id in stop_ids)


def _update_leds(leds: dict[str, LED], active: set[str]) -> None:
    for stop_id, led in leds.items():
        if stop_id in active:
            led.on()
        else:
            led.off()


def main() -> int:
    logging.basicConfig(
        format="%(asctime)s | %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )
    leds = {s.stop_id: LED(s.gpio) for s in STATIONS}

    def handle_sigint(_signum: int, _frame: FrameType | None) -> None:
        for led in leds.values():
            led.off()
        log.info("interrupted; all LEDs off")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)
    log.info("polling vehiclepositions.pb every %.0f s (Ctrl-C to stop)", POLL_S)

    try:
        while True:
            try:
                feed = fetch_vehicle_positions(timeout=HTTP_TIMEOUT_S)
                active = active_stop_ids(feed)
                _update_leds(leds, active)
                log.info("active = %s", _format_active(active))
            except requests.RequestException as e:
                log.warning("fetch failed: %s", e)
            except Exception as e:  # noqa: BLE001
                log.exception("unexpected error: %s", e)

            time.sleep(POLL_S)
    finally:
        for led in leds.values():
            led.off()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Phase 0 partial: blink the first N station LEDs.

Use this when you only have part of the board wired. Same gestures as
hello_leds.py (west→east, east→west, Larson scan, all-on) but limited to
the first N stations from STATIONS.

Default N=3 covers Riverfront / Donelson / Hermitage — the first three
column-pairs in docs/WIRING.md (cols 2/3, 5/6, 8/9). Bump N as you wire
more LEDs; once all 7 are in, switch to scripts/hello_leds.py.
"""

from __future__ import annotations

import signal
import sys
import time
from types import FrameType

from wego_metroboard.gpio import configure_pin_factory
from wego_metroboard.stations import STATIONS

configure_pin_factory()  # must run before importing LED

from gpiozero import LED  # noqa: E402

N = 3
SUBSET = STATIONS[:N]

STEP_S = 0.4
SCAN_S = 0.08
SCAN_CYCLES = 5
ALL_ON_S = 2.0


def _all_off(leds: list[LED]) -> None:
    for led in leds:
        led.off()


def _west_to_east(leds: list[LED]) -> None:
    for led, station in zip(leds, SUBSET, strict=True):
        print(f"[w→e] {station.name} (GPIO {station.gpio})")
        led.on()
        time.sleep(STEP_S)
        led.off()


def _east_to_west(leds: list[LED]) -> None:
    for led, station in zip(reversed(leds), reversed(SUBSET), strict=True):
        print(f"[e→w] {station.name} (GPIO {station.gpio})")
        led.on()
        time.sleep(STEP_S)
        led.off()


def _knight_rider(leds: list[LED], cycles: int) -> None:
    n = len(leds)
    if n < 2:
        return  # scan needs at least 2 LEDs
    path = list(range(n)) + list(range(n - 2, 0, -1))
    print(f"[scan] {cycles} cycles")
    for _ in range(cycles):
        for i in path:
            leds[i].on()
            time.sleep(SCAN_S)
            leds[i].off()


def main() -> int:
    print(f"testing {N} stations: {', '.join(s.name for s in SUBSET)}")
    leds = [LED(s.gpio) for s in SUBSET]

    def handle_sigint(_signum: int, _frame: FrameType | None) -> None:
        _all_off(leds)
        print("\ninterrupted; all LEDs off")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        _west_to_east(leds)
        _east_to_west(leds)
        _knight_rider(leds, SCAN_CYCLES)
        print("[all] on")
        for led in leds:
            led.on()
        time.sleep(ALL_ON_S)
        _all_off(leds)
        print("done")
    finally:
        _all_off(leds)
    return 0


if __name__ == "__main__":
    sys.exit(main())

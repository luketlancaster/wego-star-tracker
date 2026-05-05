#!/usr/bin/env python3
"""Phase 0: blink the seven station LEDs to confirm wiring.

Wiring (per station, see docs/WIRING.md):
  GPIO pin → 220–330 Ω resistor → LED anode (+, longer leg)
  LED cathode (–) → GND rail (shared across all 7 LEDs)

On a non-Pi system (no /sys/class/gpio), gpiozero's mock pin factory is used
automatically; LED state changes print to stdout so you can sanity-check the
pin order without hardware.

Sequence:
  1. west → east, 0.4 s each
  2. east → west, 0.4 s each
  3. "knight rider" Larson scanner, 5 cycles
  4. all on (solid) for 2 s — outbound state
  5. all blink for 4 s — inbound state
  6. all pulse for 4 s — BOTH-directions state
  7. all off
"""

from __future__ import annotations

import signal
import sys
import time
from types import FrameType

from wego_metroboard.gpio import configure_pin_factory
from wego_metroboard.leds import BLINK_OFF_S, BLINK_ON_S, PULSE_FADE_S
from wego_metroboard.stations import STATIONS

configure_pin_factory()  # must run before importing PWMLED

from gpiozero import PWMLED  # noqa: E402

STEP_S = 0.4
SCAN_S = 0.08
SCAN_CYCLES = 5
ALL_ON_S = 2.0
BLINK_DEMO_S = 4.0
PULSE_DEMO_S = 4.0


def _all_off(leds: list[PWMLED]) -> None:
    for led in leds:
        led.off()


def _west_to_east(leds: list[PWMLED]) -> None:
    for led, station in zip(leds, STATIONS, strict=True):
        print(f"[w→e] {station.name} (GPIO {station.gpio})")
        led.on()
        time.sleep(STEP_S)
        led.off()


def _east_to_west(leds: list[PWMLED]) -> None:
    for led, station in zip(reversed(leds), reversed(STATIONS), strict=True):
        print(f"[e→w] {station.name} (GPIO {station.gpio})")
        led.on()
        time.sleep(STEP_S)
        led.off()


def _knight_rider(leds: list[PWMLED], cycles: int) -> None:
    n = len(leds)
    # one cycle = forward sweep + reverse sweep, single LED at a time
    path = list(range(n)) + list(range(n - 2, 0, -1))
    print(f"[scan] {cycles} cycles")
    for _ in range(cycles):
        for i in path:
            leds[i].on()
            time.sleep(SCAN_S)
            leds[i].off()


def _all_blink(leds: list[PWMLED], duration_s: float) -> None:
    print(f"[all] blink for {duration_s:.0f}s (inbound state)")
    for led in leds:
        led.blink(on_time=BLINK_ON_S, off_time=BLINK_OFF_S)
    time.sleep(duration_s)
    _all_off(leds)


def _all_pulse(leds: list[PWMLED], duration_s: float) -> None:
    print(f"[all] pulse for {duration_s:.0f}s (both-directions state)")
    for led in leds:
        led.pulse(fade_in_time=PULSE_FADE_S, fade_out_time=PULSE_FADE_S)
    time.sleep(duration_s)
    _all_off(leds)


def main() -> int:
    leds = [PWMLED(s.gpio) for s in STATIONS]

    def handle_sigint(_signum: int, _frame: FrameType | None) -> None:
        _all_off(leds)
        print("\ninterrupted; all LEDs off")
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        _west_to_east(leds)
        _east_to_west(leds)
        _knight_rider(leds, SCAN_CYCLES)
        print(f"[all] solid on for {ALL_ON_S:.0f}s (outbound state)")
        for led in leds:
            led.on()
        time.sleep(ALL_ON_S)
        _all_off(leds)
        _all_blink(leds, BLINK_DEMO_S)
        _all_pulse(leds, PULSE_DEMO_S)
        print("done")
    finally:
        _all_off(leds)
    return 0


if __name__ == "__main__":
    sys.exit(main())

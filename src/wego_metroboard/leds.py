"""LED state controller for direction-aware station lighting.

Four steady states per LED:

- OFF      — no train at the station
- OUTBOUND — solid on (eastbound, away from Riverfront)
- INBOUND  — slow hard blink (westbound, toward Riverfront)
- BOTH     — soft pulse / "breathing" (a rush-hour overlap, both directions
             present at the same station)

PWMLED is used (rather than plain LED) so the BOTH state can fade in/out
via .pulse(). Software PWM is provided by gpiozero's lgpio backend on the
Pi and works on every GPIO this project uses; on dev machines the mock
factory just logs state changes.

Caller must invoke ``wego_metroboard.gpio.configure_pin_factory()`` before
constructing ``StationLeds`` so gpiozero picks the right backend.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import StrEnum
from typing import TYPE_CHECKING

from wego_metroboard.stations import Station

if TYPE_CHECKING:
    from gpiozero import PWMLED

BLINK_ON_S = 0.6
BLINK_OFF_S = 0.6
PULSE_FADE_S = 0.8


class LedState(StrEnum):
    OFF = "off"
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    BOTH = "both"


def state_for(directions: set[int], outbound_id: int) -> LedState:
    """Resolve a single station's LED state from its active direction_ids."""
    if not directions:
        return LedState.OFF
    has_out = outbound_id in directions
    has_in = any(d != outbound_id for d in directions)
    if has_out and has_in:
        return LedState.BOTH
    return LedState.OUTBOUND if has_out else LedState.INBOUND


class StationLeds:
    """Owns one PWMLED per station and applies LedState transitions.

    Caches state and only touches hardware on changes — gpiozero's blink()
    and pulse() restart their pattern from the beginning on each call, so
    naively re-driving the same state every poll cycle would mean the LED
    never visibly cycles.
    """

    def __init__(self, stations: Sequence[Station]) -> None:
        from gpiozero import PWMLED  # deferred: configure_pin_factory() must run first

        self._leds: dict[str, PWMLED] = {s.stop_id: PWMLED(s.gpio) for s in stations}
        self._state: dict[str, LedState] = dict.fromkeys(self._leds, LedState.OFF)

    def update(self, directions: dict[str, set[int]], outbound_id: int) -> None:
        for stop_id, led in self._leds.items():
            new_state = state_for(directions.get(stop_id, set()), outbound_id)
            if new_state == self._state[stop_id]:
                continue
            self._state[stop_id] = new_state
            _apply(led, new_state)

    def all_off(self) -> None:
        for stop_id, led in self._leds.items():
            led.off()
            self._state[stop_id] = LedState.OFF

    def state(self, stop_id: str) -> LedState:
        return self._state[stop_id]


def _apply(led: PWMLED, new_state: LedState) -> None:
    if new_state is LedState.OFF:
        led.off()
    elif new_state is LedState.OUTBOUND:
        led.on()
    elif new_state is LedState.INBOUND:
        led.blink(on_time=BLINK_ON_S, off_time=BLINK_OFF_S)
    elif new_state is LedState.BOTH:
        led.pulse(fade_in_time=PULSE_FADE_S, fade_out_time=PULSE_FADE_S)

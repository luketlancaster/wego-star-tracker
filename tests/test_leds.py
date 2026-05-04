"""Tests for the LED state-resolution layer.

Only ``state_for`` is exercised here. ``StationLeds`` is a thin wrapper
around gpiozero.PWMLED whose behavior is timing-based and best verified
by eye on the Pi (or in mock mode via run_schedule.py).
"""

from __future__ import annotations

from wego_metroboard.leds import LedState, state_for


def test_state_for_empty_set_is_off() -> None:
    assert state_for(set(), outbound_id=0) == LedState.OFF


def test_state_for_outbound_only() -> None:
    assert state_for({0}, outbound_id=0) == LedState.OUTBOUND


def test_state_for_inbound_only() -> None:
    assert state_for({1}, outbound_id=0) == LedState.INBOUND


def test_state_for_both_directions() -> None:
    assert state_for({0, 1}, outbound_id=0) == LedState.BOTH


def test_state_for_handles_flipped_outbound_id() -> None:
    # If the agency ever flips direction_ids, the same logic should hold.
    assert state_for({1}, outbound_id=1) == LedState.OUTBOUND
    assert state_for({0}, outbound_id=1) == LedState.INBOUND
    assert state_for({0, 1}, outbound_id=1) == LedState.BOTH

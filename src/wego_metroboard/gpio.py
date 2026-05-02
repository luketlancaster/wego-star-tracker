"""gpiozero pin-factory helpers.

On a Raspberry Pi, gpiozero auto-selects a real factory (lgpio / RPi.GPIO).
On a dev laptop there is no /sys/class/gpio, so we fall back to the mock
factory, which prints LED state changes instead of toggling hardware.
"""

from __future__ import annotations

import os
from pathlib import Path


def configure_pin_factory() -> str:
    """Set GPIOZERO_PIN_FACTORY=mock on non-Pi systems if not already set.

    Must be called before importing ``gpiozero.LED`` (or any pin-using class)
    for the env var to take effect. Returns the factory name in use.
    """
    existing = os.environ.get("GPIOZERO_PIN_FACTORY")
    if existing:
        return existing
    if not Path("/sys/class/gpio").exists():
        os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
        return "mock"
    return "default"

"""gpiozero pin-factory helpers.

On a Raspberry Pi, gpiozero auto-selects a real factory (lgpio / RPi.GPIO).
On a dev laptop there is no /sys/class/gpio, so we fall back to a mock
factory configured with MockPWMPin — a superset of MockPin that supports
both digital on/off and PWM (pulse), so PWMLED works in mock mode too.
"""

from __future__ import annotations

import os
from pathlib import Path


def _install_mock_pwm_factory() -> None:
    # Importing gpiozero is safe before construction; the env-var-driven
    # path uses MockPin which lacks PWM, so we set the factory directly.
    from gpiozero import Device
    from gpiozero.pins.mock import MockFactory, MockPWMPin

    Device.pin_factory = MockFactory(pin_class=MockPWMPin)


def configure_pin_factory() -> str:
    """Pick a gpiozero pin factory.

    Must be called before constructing any LED / PWMLED. Returns a short
    name describing the factory in use.
    """
    existing = os.environ.get("GPIOZERO_PIN_FACTORY")
    if existing == "mock":
        _install_mock_pwm_factory()
        return "mock"
    if existing:
        return existing
    if not Path("/sys/class/gpio").exists():
        os.environ["GPIOZERO_PIN_FACTORY"] = "mock"
        _install_mock_pwm_factory()
        return "mock"
    return "default"

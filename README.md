# WeGo Metroboard

A physical Metroboard — inspired by [designrules.co](https://www.designrules.co)
— for Nashville's **WeGo Star** commuter rail. A wall-mounted board with one
LED per station; an LED lights up when a train is at that station, driven by
Nashville MTA's GTFS feeds.

**Current phase:** Phase 0 — wiring sanity check. See [`docs/PHASES.md`](docs/PHASES.md).

## Hardware

- Raspberry Pi 4 (target deployment)
- Half-size breadboard
- 7× standard LEDs
- 7× 220–330 Ω resistors
- Jumper wires
- (An Arduino Uno is in the parts box for Phase 3 / addressable LEDs — not
  used yet.)

Pin map and breadboard layout: [`docs/WIRING.md`](docs/WIRING.md).

## Running

This project targets **Python 3.11+**. Two flavors of setup:

### With `uv` (preferred)

```sh
uv venv
uv pip install -e ".[dev]"
uv run python scripts/hello_leds.py
```

### With plain `pip` / `venv`

```sh
python3.13 -m venv .venv          # or any Python ≥ 3.11
source .venv/bin/activate
pip install -e ".[dev]"
python scripts/hello_leds.py
```

### On a dev machine (no Pi)

The scripts auto-detect the absence of `/sys/class/gpio` and use gpiozero's
mock pin factory, so you can run them on macOS/Linux laptops. Output looks
like:

```
[w→e] Riverfront (GPIO 17)
[w→e] Donelson (GPIO 27)
...
```

To force mock mode explicitly:

```sh
GPIOZERO_PIN_FACTORY=mock python scripts/hello_leds.py
```

### On the Raspberry Pi

See [`docs/PI_SETUP.md`](docs/PI_SETUP.md) for the full headless setup walkthrough
(imaging the SD card, SSH key auth, OS update, installing `lgpio`, cloning and
running). [`docs/WIRING.md`](docs/WIRING.md) has the breadboard layout and
step-by-step wiring instructions.

## Layout

```
src/wego_metroboard/   library code (stations, GPIO helpers, feed URLs)
scripts/               runnable entry points (hello_leds.py, fetch_static.py)
docs/                  PHASES.md, WIRING.md, PI_SETUP.md
data/                  GTFS zip + extracted CSVs (gitignored, populated by fetch_static.py)
tests/                 (empty for now)
```

## Credits

- Concept inspired by [designrules.co](https://www.designrules.co)'s metro
  boards.
- Data: [WeGo Public Transit](https://www.wegotransit.com/) GTFS static and
  realtime feeds.

## License

MIT — see [`LICENSE`](LICENSE).

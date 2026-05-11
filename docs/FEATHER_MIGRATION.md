# Migration: Raspberry Pi 4 → Adafruit Feather ESP32-S3 (5477)

Plan for moving the Phase 2 schedule-driven board off the Pi and onto an
Adafruit ESP32-S3 Feather. Realtime polling is not in scope (WeGo's
GTFS-realtime feed has no rail data — see `README.md`), so this migration
covers Phase 2 only. Phase 3 (addressable LEDs) lands later on the same MCU.

## Settled decisions

- **Firmware:** CircuitPython.
- **Schedule source:** pre-computed on a host laptop, copied to the device
  as a compact JSON pack. No on-device CSV parsing, no GTFS-realtime.
- **Schedule refresh:** manual — run the host build step, drag the pack
  onto the `CIRCUITPY` drive over USB. No OTA.
- **Phase 3 / NeoPixel:** out of scope for this migration. Pick pins for
  the 7 station LEDs only; don't pre-reserve anything for later.

## Target pin map

Proposal — verify against the official 5477 pinout when wiring:

| stop_id   | Station          | Feather label | ESP32-S3 GPIO |
|-----------|------------------|---------------|---------------|
| MCSRVRF   | Riverfront       | A0            | 17            |
| MCSDONEL  | Donelson         | A1            | 18            |
| MCSHERM   | Hermitage        | A2            | 14            |
| MCSMJ     | Mt. Juliet       | A3            | 12            |
| MCSMS     | Martha           | A4            | 6             |
| MCSHAM    | Hamilton Springs | A5            | 5             |
| MCSLB     | Lebanon          | D10           | 10            |

Avoids the onboard LED on D13/GPIO13, the I²C bus, SPI, and UART so they
remain available for later. Every pin listed supports `pwmio.PWMOut` on
ESP32-S3, so the existing four LED states (off / solid / blink / pulse)
all carry over without change.

Wiring topology is unchanged from the Pi: GPIO → 220–330 Ω → LED anode,
cathode to a shared ground rail, ground rail to a Feather GND pin.

## Repo layout after migration

```
firmware/                      ← NEW; this is what gets copied to CIRCUITPY
  code.py                      schedule loop
  boot.py                      Wi-Fi + NTP bring-up
  settings.toml.example        committed; settings.toml is gitignored
  lib/                         vendored CircuitPython libs (adafruit_ntp, etc.)
  schedule/
    schedule.json              compact pack produced by build_schedule.py
src/wego_metroboard/           host-side library (kept; powers the build step)
  feeds.py                     unchanged
  schedule.py                  unchanged
  stations.py                  drop the `gpio` field (Pi-specific)
  gpio.py                      DELETED (gpiozero pin-factory helper)
  leds.py                      DELETED (PWMLED wrapper) — re-implemented in firmware/
scripts/
  build_schedule.py            NEW; emits firmware/schedule/schedule.json
  fetch_static.py              unchanged
  hello_leds.py                DELETED (replaced by a CircuitPython equivalent in firmware/)
  run_schedule.py              DELETED (replaced by firmware/code.py)
  run_realtime.py              DELETED (no realtime data exists for this route)
deploy/                        DELETED (no more systemd)
docs/
  FEATHER_SETUP.md             NEW; replaces PI_SETUP.md
  WIRING.md                    rewritten for the Feather pin map
  PHASES.md                    Phase 2 status updated; Pi references removed
  PI_SETUP.md                  DELETED
```

## Migration phases

### M1 — Firmware bring-up (no transit data)

Goal: prove the wiring and the four LED states on the Feather, equivalent
to the old `hello_leds.py`.

1. Create `firmware/` with `code.py`, `boot.py`, `settings.toml.example`,
   and an empty `lib/`.
2. Wire 7 LEDs per the pin-map table above on a fresh breadboard.
3. Write a `firmware/code.py` smoke-test mode that runs the same sequence
   as the old `hello_leds.py`: west→east sweep, east→west, Larson scan,
   then demos of solid / blink / pulse states. PWM via `pwmio.PWMOut`.
   Blink is a tick-loop toggle; pulse is a sine-driven duty cycle (no
   `gpiozero.pulse()` equivalent in CircuitPython, but it's ~10 lines).
4. Rewrite `docs/WIRING.md` end-to-end for the Feather. Details below in
   "Wiring documentation updates" — this is more than a pin-table swap;
   the doc currently references Pi physical pins, `lgpio`, `journalctl`,
   and a `python scripts/hello_leds.py` smoke test, all of which change.

**Exit criteria:** human verifies LEDs light in geographic order and all
four states render visually.

### M2 — Time + Wi-Fi

Goal: the Feather knows the current local time after boot.

1. `settings.toml` holds `CIRCUITPY_WIFI_SSID` / `CIRCUITPY_WIFI_PASSWORD`.
   Commit only `settings.toml.example`; gitignore `settings.toml`.
2. `boot.py` (or early in `code.py`): connect Wi-Fi, run `adafruit_ntp` to
   set the RTC, compute the `America/Chicago` UTC offset.
3. Time-zone strategy: CircuitPython has no `zoneinfo`. Hard-code a small
   DST transition table (second Sunday of March → first Sunday of November,
   computed for the next ~5 years) generated by the host build step and
   shipped alongside the schedule pack. Documented assumption: refresh the
   pack at least once every 4 years.
4. Wrap the main loop with the ESP32 watchdog so a Wi-Fi flake or NTP
   timeout self-recovers via reset.

**Exit criteria:** Feather logs the correct local time over USB serial
within ~10 s of power-on, and recovers from a manual Wi-Fi outage.

### M3 — Compact schedule + on-device playback

Goal: the board lights the right stations at the right times, end to end.

1. New `scripts/build_schedule.py` (host-side):
   - Calls `wego_metroboard.schedule.windows_for_today` and
     `outbound_direction_id` for each of the next N days (default 14).
   - Emits `firmware/schedule/schedule.json`:
     ```json
     {
       "generated_at": "2026-05-08T12:00:00-05:00",
       "outbound_direction_id": 0,
       "dst_transitions": [["2026-03-08T02:00", -300], ["2026-11-01T02:00", -360], ...],
       "days": {
         "2026-05-08": [["MCSRVRF", 0, 21300, 21540], ["MCSDONEL", 0, 21660, 21900], ...],
         "2026-05-09": [...]
       }
     }
     ```
   - Keys: `stop_id`, `direction_id`, `start_s`, `end_s` (seconds since
     local midnight). Empty list = no service that day, board goes dark.
2. Port `state_for(...)` from `src/wego_metroboard/leds.py` verbatim into
   `firmware/code.py` — it's a pure function.
3. `firmware/code.py` schedule loop:
   - On boot, load `schedule.json` into RAM.
   - Every 30 s, compute current local `now_s`, scan today's window list
     for matches, build a `dict[stop_id, set[direction_id]]`, hand to a
     CircuitPython `StationLeds`-equivalent class that mirrors the
     existing transition-cache behavior (only touch hardware on changes).
   - On local-midnight rollover, switch to the next day's list.
   - If the date isn't in the pack, board goes dark and the onboard
     NeoPixel does a slow heartbeat — visible "I'm alive but I have no
     schedule" signal that distinguishes from "I'm crashed."
4. Vendor needed CircuitPython libs into `firmware/lib/`: at minimum
   `adafruit_ntp`, `adafruit_connection_manager`. List exact versions in
   `docs/FEATHER_SETUP.md`.

**Exit criteria:** board shows the correct station states for a known
trip (e.g., the 5:05 PM inbound is the easiest to verify visually — it's
also the rush-hour overlap window for the BOTH-direction pulse state).

### M4 — Maintenance + cleanup

Goal: documented manual refresh loop; no dead Pi-era files in the repo.

1. Document the refresh loop in `docs/FEATHER_SETUP.md`:
   ```sh
   uv run python scripts/fetch_static.py        # refresh GTFS zip
   uv run python scripts/build_schedule.py      # regenerate firmware/schedule/schedule.json
   # plug Feather, drag firmware/* onto CIRCUITPY drive
   ```
   Cadence: whenever WeGo updates the timetable, or every ~2 weeks.
2. Delete `deploy/`, `docs/PI_SETUP.md`, `scripts/run_schedule.py`,
   `scripts/run_realtime.py`, `scripts/hello_leds.py`,
   `src/wego_metroboard/gpio.py`, `src/wego_metroboard/leds.py`.
3. `pyproject.toml`: drop `gpiozero` from runtime deps. Keep `requests`
   and `gtfs-realtime-bindings` (still used by `fetch_static.py`).
4. Drop the `gpio` field from `Station`; the firmware owns its own pin
   map now and the host library doesn't need it.
5. `docs/PHASES.md`: rewrite Phase 2 to describe the Feather setup; remove
   "Pi + systemd" framing. Note that Phase 3 is now in scope on the same
   board.
6. `README.md`: update the Hardware section, the Running section (Pi
   walkthrough → Feather flashing walkthrough), and the Layout section to
   match the post-migration tree.

**Exit criteria:** fresh clone of the repo + a fresh Feather can be
brought up to a working board following only `docs/FEATHER_SETUP.md` and
`docs/WIRING.md`.

## Wiring documentation updates

Detailed checklist for the `docs/WIRING.md` rewrite (M1, step 4) and the
matching adjustments elsewhere in the docs. Calling these out explicitly
because the current doc is Pi-shaped throughout, not only in the pin
table.

### `docs/WIRING.md`

- **Intro.** Drop "Phase 0" framing — wiring is no longer phase-gated;
  it's a one-time setup for the Feather build.
- **"What you'll need".** Replace M-to-F "Pi header to breadboard"
  jumpers with M-to-M "Feather header to breadboard" jumpers (the
  Feather is breadboard-friendly so it can sit on the same breadboard,
  unlike the Pi). Either soldered headers + jumper wires, or socket
  headers + breadboard-direct mount — call out both options.
- **Pin map table.** Replace the BCM-and-Pi-physical-pin columns with
  Feather-label-and-ESP32-S3-GPIO columns (per the table in this doc).
  Drop the GND-physical-pin row; any of the Feather's GND pins works,
  callout the one nearest the LiPo connector for short jumper runs.
- **"Why these GPIOs".** Rewrite for the Feather: avoiding D13/GPIO13
  (onboard red LED), the I²C bus (SDA/SCL), SPI (SCK/MOSI/MISO), UART
  (RX/TX), the onboard NeoPixel (GPIO33), and the strapping pins
  (0/45/46) so they remain available later.
- **Breadboard ASCII diagram.** The 7-LED column layout stays. Update
  the top-row callouts from "Pi GPIO jumper" to "Feather pin jumper"
  and adjust the legend.
- **Per-station column assignments table.** Replace the "Pi pin" column
  with "Feather pin" (`A0`, `A1`, ... `A5`, `D10`); GPIO column updates
  to ESP32-S3 numbers.
- **Power-off warning.** Replace "Unplug the USB-C cable from the Pi
  before wiring" with the Feather equivalent — unplug USB-C *and*
  disconnect the LiPo if one is attached. Hot-plugging GPIO can still
  damage the MCU.
- **Step-by-step wiring.** Step 5 ("Wire `–` rail to Pi GND") becomes
  "Wire `–` rail to Feather GND". Step 6's Pi-physical-pin → breadboard
  table becomes a Feather-label → breadboard table. Steps that
  reference "the Pi" reference "the Feather" instead.
- **Smoke test section.** Replace the Pi-specific shell snippet
  (`source .venv/bin/activate; python scripts/hello_leds.py`) with the
  Feather equivalent: copy `firmware/code.py` (with `MODE = "smoke"` or
  similar) onto the `CIRCUITPY` drive and watch it run automatically on
  next reset. Document how to view USB serial output (`screen
  /dev/tty.usbmodem* 115200` on macOS, `tio` on Linux).
- **Troubleshooting.** Drop the `lgpio` venv troubleshooting and the
  `GPIOZERO_PIN_FACTORY=mock` mock-mode entry. Add Feather-specific
  failure modes:
  - `CIRCUITPY` drive doesn't appear → double-tap reset to enter
    bootloader mode.
  - LEDs all dark and no serial output → check `boot_out.txt` on the
    `CIRCUITPY` drive for a CircuitPython traceback.
  - LEDs flicker faintly when "off" → likely a pin shared with the
    onboard LED or NeoPixel; cross-check the pin map.
  - LEDs work but Wi-Fi fails → `settings.toml` not present or
    misnamed (case-sensitive).

### `docs/PHASES.md`

- Phase 0 description is currently a sequence run by `hello_leds.py`.
  Re-anchor it as the firmware smoke-test mode in `firmware/code.py`,
  but the human-verified exit criteria stay the same.
- Phase 2 description: replace "running on a Raspberry Pi 4 as a systemd
  service" with the Feather + CircuitPython setup; link to
  `FEATHER_SETUP.md` and `FEATHER_MIGRATION.md`.

### `README.md`

- Hardware list: Raspberry Pi 4 → Adafruit ESP32-S3 Feather (5477).
  Drop the "Arduino Uno in the parts box" line — the Feather covers
  Phase 3 too.
- "Running" section: replace the `uv` / `pip` / mock-mode walkthroughs
  with a short pointer to `docs/FEATHER_SETUP.md`. The host-side build
  step (`scripts/build_schedule.py`) keeps a small `uv` snippet.
- Layout section: refresh to match the post-migration tree.

## Risks / open items

- **DST table maintenance.** The hard-coded approach is simple but does
  silently drift if the schedule pack isn't refreshed for years. The
  `generated_at` stamp + a startup log of "DST table covers through
  YYYY-MM-DD" mitigates this.
- **Memory headroom.** A 14-day pack for 7 stations × ~30 trips/day ×
  ~30 bytes per window is ~90 KB — well within the Feather's RAM, but
  worth measuring once the format is locked.
- **CircuitPython library versions.** `adafruit_ntp` in particular has
  changed APIs across CP releases. Pin to a specific CP version (current
  stable at migration time) and record it in `docs/FEATHER_SETUP.md`.
- **No remote observability.** The Pi gave us `journalctl`. The Feather
  gives us USB serial only. Acceptable for a personal board, but worth a
  follow-up: optional UDP-syslog-to-laptop for debugging from across the
  room.

# Phase plan

## Phase 0 — hello LEDs (current)

Confirm wiring works before any network code exists.

`scripts/hello_leds.py`:

1. Instantiate a `gpiozero.LED` for each of the 7 stations.
2. Auto-detect non-Pi environments and fall back to gpiozero's `MockFactory`
   (so the script runs on a laptop and prints `LED 17 ON / OFF` etc.).
3. Light each LED in sequence, west → east, 0.4 s each.
4. Then east → west.
5. Then a "knight rider" sweep for 5 cycles.
6. Then "all on" for 2 s, all off, clean exit.
7. SIGINT handler so Ctrl-C never leaves an LED stuck on.

**Exit criteria:** human verifies LEDs light in geographic order.

## Phase 1 — realtime polling

30 s polling loop. Fetch `vehiclepositions.pb`, filter to route 90, light any
station whose `stop_id` matches a vehicle with `current_status == STOPPED_AT`.
Console log every cycle. No schedule fallback yet.

## Phase 2 — schedule fallback

Use static GTFS so the board does something interesting outside service hours:
compute "where would a train be right now if running on schedule?" Optional
"demo mode" replays the day at 10× speed when realtime is empty.

Respect `calendar_dates.txt` (holidays remove service — board goes dark).

Three short-turn trips don't serve all 7 stations:

- 6:53 AM and 4:20 PM outbounds: Riverfront → Mt. Juliet only
- 7:45 AM and 5:05 PM inbounds: Mt. Juliet → Riverfront only

## Phase 3 — addressable in-transit LEDs

WS2812B strips along inter-station segments to show in-transit position.
Interpolate vehicle lat/lon along the four `shapes.txt` shapes (19270 / 19271
/ 19272 / 19273) to get fractional position along each segment. Likely where
the Arduino Uno earns its keep as a dedicated pixel driver.

## Out of scope (for now)

- Web UI / mobile app
- Star Downtown Shuttle (route 64), West End Shuttle (route 93)
- Service Alerts feed
- Production enclosure / wood frame

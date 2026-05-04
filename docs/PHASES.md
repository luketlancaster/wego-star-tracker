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

## Phase 2 — schedule-driven (current primary driver)

WeGo's GTFS-realtime feed doesn't include the WeGo Star, so the static
schedule *is* the driver — not a fallback. Each cycle the loop computes
"where would a train be right now if running on schedule?" and lights the
matching station LEDs.

Respect `calendar_dates.txt` (holidays remove service — board goes dark).

### LED state encoding

Each station LED has four states, set via gpiozero.PWMLED:

| state    | meaning                                  | hardware                 |
|----------|------------------------------------------|--------------------------|
| off      | no train at the station                  | `pwmled.off()`           |
| solid on | outbound (eastbound) only                | `pwmled.on()`            |
| slow blink | inbound (westbound) only               | `pwmled.blink(0.6, 0.6)` |
| soft pulse | both directions overlapping at this stop | `pwmled.pulse(0.8, 0.8)` |

The "outbound" direction_id is inferred at startup from `trips.txt` —
whichever direction has trips originating at Riverfront (`MCSRVRF`) is the
eastbound direction. This stays correct even if WeGo flips the GTFS 0/1
assignment.

### Short-turn trips

Three trips don't serve all 7 stations and are worth knowing about when
debugging unexpected dark stations:

- 6:53 AM and 4:20 PM outbounds: Riverfront → Mt. Juliet only
- 7:45 AM and 5:05 PM inbounds: Mt. Juliet → Riverfront only

The 5:05 PM inbound is also the most reliable rush-hour overlap window
for verifying the "soft pulse" both-directions state.

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

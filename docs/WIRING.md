# Wiring

How to physically build the breadboard for Phase 0. The end state: 7 LEDs
arranged in a row, each driven by a different GPIO pin on the Pi, all sharing
a common ground.

## What you'll need

- Half-size solderless breadboard (the 30-column kind with two power rails)
- 7× standard 5 mm LEDs (any color; pick one per station if you want)
- 7× 220–330 Ω resistors (color bands red-red-brown for 220 Ω, orange-orange-brown
  for 330 Ω). Anything in that range is fine for a typical 3.3 V GPIO driving
  a 2 V LED at ~10 mA.
- Jumper wires:
  - 7× M-to-M for GPIO → breadboard (or M-to-F if you're going Pi header
    straight to board)
  - 1× M-to-F for Pi GND → breadboard `–` rail
  - 7× short M-to-M (or just bits of solid-core wire) for each LED cathode
    column → `–` rail

You do **not** need to solder anything for Phase 0.

## Per-station circuit (one LED, repeated 7×)

```
   Pi GPIO pin ──[ 220–330 Ω resistor ]──┬── LED anode (+, longer leg)
                                         │
                                         └── LED cathode (–, shorter leg) ── – rail ── Pi GND
```

The resistor can sit on either side of the LED — high side (between GPIO and
anode) is what we'll use here.

## Pin map (BCM)

Geographic order, west → east:

| stop_id   | Station          | GPIO (BCM) | Pi physical pin |
|-----------|------------------|------------|-----------------|
| MCSRVRF   | Riverfront       | 17         | 11              |
| MCSDONEL  | Donelson         | 27         | 13              |
| MCSHERM   | Hermitage        | 22         | 15              |
| MCSMJ     | Mt. Juliet       | 23         | 16              |
| MCSMS     | Martha           | 24         | 18              |
| MCSHAM    | Hamilton Springs | 25         | 22              |
| MCSLB     | Lebanon          |  5         | 29              |

Plus one ground connection:

| Signal | Pi physical pin |
|--------|-----------------|
| GND    | 6               |

(Any GND pin works — 6, 9, 14, 20, 25, 30, 34, 39 are all interchangeable.
Pin 6 is the closest one to the front of the header so the jumper run is
short.)

### Why these GPIOs

- All clean BCM numbers, none shared with the I²C (2/3), SPI (7/8/9/10/11),
  or 1-Wire (4) defaults.
- Avoids GPIO 14/15 (UART) so a serial console stays usable for debugging.

## Breadboard layout

A half-size breadboard has 30 columns (numbered 1–30 here). Each column has 5
holes in the top half (rows `a`–`e`) connected vertically, and 5 in the bottom
half (`f`–`j`) connected vertically. The top and bottom halves are isolated
by the center channel — that's where the LEDs bridge across. The two long
power rails run along the outside edges.

We'll use seven adjacent column-pairs spaced 3 columns apart, leaving plenty
of breathing room:

```
                          col:    2  3      5  6      8  9     11 12     14 15     17 18     20 21
                                  ↓  ↓      ↓  ↓      ↓  ↓      ↓  ↓      ↓  ↓      ↓  ↓      ↓  ↓
   + rail  ── (unused) ─────────────────────────────────────────────────────────────────────────────
                            a  ·  J  ·  ·   J  ·  ·   J  ·  ·   J  ·  ·   J  ·  ·   J  ·  ·   J  ·  ·
                            b  ·  ╞══╡  ·   ╞══╡  ·   ╞══╡  ·   ╞══╡  ·   ╞══╡  ·   ╞══╡  ·   ╞══╡  ·   ← 220 Ω resistor
                            c  ·  ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·
                            d  ·  ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·   ·  ·  ·
                            e  ·  ·  +  ·   ·  +  ·   ·  +  ·   ·  +  ·   ·  +  ·   ·  +  ·   ·  +  ·   ← LED anode (long leg)
   ─────── center channel ─── (LEDs bridge from row e to row f within the same column) ───
                            f  ·  ·  −  ·   ·  −  ·   ·  −  ·   ·  −  ·   ·  −  ·   ·  −  ·   ·  −  ·   ← LED cathode (short leg)
                            g  ·  ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·
                            h  ·  ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·
                            i  ·  ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·   ·  │  ·
                            j  ·  ·  K  ·   ·  K  ·   ·  K  ·   ·  K  ·   ·  K  ·   ·  K  ·   ·  K  ·
   – rail  ── to Pi GND ────┴──┴──┴──┴───┴──┴──┴───┴──┴──┴───┴──┴──┴───┴──┴──┴───┴──┴──┴───┴──┴──┴───┴──
                                                                                                Riverfront → Lebanon →
```

Legend:
- `J` — GPIO jumper from Pi (top of the column)
- `╞══╡` — resistor laid horizontally, legs bridging two adjacent columns
- `+` — LED anode (long leg)
- `−` — LED cathode (short leg, same column as anode but bottom half)
- `K` — short jumper from cathode column to the `–` rail

### Per-station column assignments

| Station          | GPIO | Pi pin | GPIO jumper into | Resistor between | LED anode at | LED cathode at | Cathode → `–` rail jumper |
|------------------|------|--------|------------------|------------------|--------------|----------------|---------------------------|
| Riverfront       |  17  |  11    | col 2, row a     | cols 2 ↔ 3, row b | col 3, row e | col 3, row f   | col 3, row j → `–` rail   |
| Donelson         |  27  |  13    | col 5, row a     | cols 5 ↔ 6, row b | col 6, row e | col 6, row f   | col 6, row j → `–` rail   |
| Hermitage        |  22  |  15    | col 8, row a     | cols 8 ↔ 9, row b | col 9, row e | col 9, row f   | col 9, row j → `–` rail   |
| Mt. Juliet       |  23  |  16    | col 11, row a    | cols 11 ↔ 12, row b | col 12, row e | col 12, row f | col 12, row j → `–` rail  |
| Martha           |  24  |  18    | col 14, row a    | cols 14 ↔ 15, row b | col 15, row e | col 15, row f | col 15, row j → `–` rail  |
| Hamilton Springs |  25  |  22    | col 17, row a    | cols 17 ↔ 18, row b | col 18, row e | col 18, row f | col 18, row j → `–` rail  |
| Lebanon          |   5  |  29    | col 20, row a    | cols 20 ↔ 21, row b | col 21, row e | col 21, row f | col 21, row j → `–` rail  |

Plus one jumper from any hole on the `–` rail to Pi pin 6 (GND).

## Step-by-step wiring

> **Power off the Pi before you wire anything.** Unplug the USB-C cable. Don't
> rely on a soft shutdown — physically remove power. Hot-plugging GPIO is how
> you brick a Pi.

1. **Lay the breadboard flat.** Orient it so column 1 is on your left and
   column 30 is on your right, with the `+` rail at the top and `–` rail at
   the bottom. (Most boards label them; the red stripe is `+`, the blue/black
   stripe is `–`.)
2. **Insert the 7 resistors.** For each station, push one resistor leg into
   row `b` of the listed left column, the other leg into row `b` of the
   adjacent column. Bend legs as needed so the resistor lies flat. Trim long
   legs if they bother you, but it's not required.
3. **Insert the 7 LEDs.** For each station's right column (the one with the
   resistor's right leg), push the **long leg (anode, `+`)** into row `e`
   and the **short leg (cathode, `–`)** into row `f`. The LED bridges the
   center channel. Double-check polarity — backwards LEDs simply don't light.
4. **Wire the cathode columns to the `–` rail.** For each LED, take a short
   jumper (or a snipped piece of solid-core wire) and connect from row `j`
   of that LED's column down to the nearest hole on the `–` rail. 7 jumpers
   total.
5. **Wire `–` rail to Pi GND.** One M-to-F jumper from any hole on the `–`
   rail to **physical pin 6** on the Pi GPIO header.
6. **Wire each GPIO to its column.** Seven M-to-F (or M-to-M, with a header
   adapter) jumpers, each running from a Pi physical pin to row `a` of the
   listed column. Do these one at a time, double-checking the table above:

   | Pi pin | Breadboard column |
   |--------|-------------------|
   |   11   |  2  |
   |   13   |  5  |
   |   15   |  8  |
   |   16   | 11  |
   |   18   | 14  |
   |   22   | 17  |
   |   29   | 20  |

7. **Visual sanity check.**
   - 7 resistors, each in row `b`, each spanning two columns. ✓
   - 7 LEDs, all with the long leg in row `e` and short leg in row `f`. ✓
   - 7 cathode-to-`–`-rail jumpers. ✓
   - 1 `–`-rail-to-Pi-pin-6 jumper. ✓
   - 7 GPIO-to-column jumpers, going to the right Pi pins. ✓
8. **Plug the Pi back in.** Wait for it to boot, SSH in.

## Smoke test

```sh
cd ~/wego-star-tracker
source .venv/bin/activate
python scripts/hello_leds.py
```

You should see, in this order:

1. Riverfront → Donelson → Hermitage → Mt. Juliet → Martha → Hamilton Springs
   → Lebanon, each on for 0.4 s.
2. The reverse, Lebanon back to Riverfront.
3. A back-and-forth Larson sweep, 5 cycles.
4. All 7 on for 2 s, then dark.

If the order matches the row of LEDs reading left-to-right on your breadboard,
the wiring is correct and Phase 0 is done.

## Troubleshooting

**One LED never lights, the others are fine.**
Almost always polarity. Pull the LED out and reseat it with the long leg in
row `e`. Second most likely: a leg isn't fully seated.

**The wrong LED lights for a given station name.**
Either the GPIO jumper is in the wrong column or the LEDs are seated in the
wrong order. Cross-check the column assignment table above.

**All LEDs are very dim.**
You probably forgot the cathode-to-`–`-rail jumper for one or more columns,
or the `–` rail isn't connected to GND. Without a complete return path the
LED can still glow faintly via leakage paths.

**All LEDs flash on but never turn off (or vice versa).**
Most likely the GPIO jumpers are touching each other, or one is in the wrong
row (e.g. row `f` instead of row `a`). Re-seat them.

**Nothing lights at all and the script also doesn't print anything.**
The script crashed before reaching the LED loop. Re-run with the output
visible (don't pipe to `tail`) and read the traceback. The most common cause
is the venv missing `lgpio` — see `PI_SETUP.md` troubleshooting.

**The script prints `LED 17 ON` etc. but no LEDs light.**
You're in mock mode. Either `GPIOZERO_PIN_FACTORY=mock` is set in your shell,
or `/sys/class/gpio` doesn't exist (you're not actually running on a Pi).
Run `unset GPIOZERO_PIN_FACTORY` and try again.

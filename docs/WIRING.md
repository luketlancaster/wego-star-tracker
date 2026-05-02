# Wiring

## Per-station LED circuit

```
RPi GPIO pin ──[ 220–330 Ω resistor ]──┬── LED anode (+, longer leg)
                                        │
                                        └── LED cathode (–) ── GND rail
```

The resistor can sit on either side of the LED; on the high side is fine.

## GPIO pin map (BCM)

Geographic order, west → east:

| stop_id   | Station          | GPIO (BCM) | Physical pin |
|-----------|------------------|------------|--------------|
| MCSRVRF   | Riverfront       | 17         | 11           |
| MCSDONEL  | Donelson         | 27         | 13           |
| MCSHERM   | Hermitage        | 22         | 15           |
| MCSMJ     | Mt. Juliet       | 23         | 16           |
| MCSMS     | Martha           | 24         | 18           |
| MCSHAM    | Hamilton Springs | 25         | 22           |
| MCSLB     | Lebanon          |  5         | 29           |

All seven cathodes share the same GND rail (any GND pin on the Pi: physical
pins 6, 9, 14, 20, 25, 30, 34, 39 all work).

## Why these pins

- All clean BCM numbers, none shared with the I²C (2/3), SPI (7/8/9/10/11),
  or 1-Wire (4) defaults.
- Avoids GPIO 14/15 (UART) so a serial console stays usable for debugging.

## Half-size breadboard layout (sketch)

```
  ┌────────────────────────── + rail (unused; LEDs are sourced from GPIOs)
  │
  │   [R] [R] [R] [R] [R] [R] [R]   ← 7 resistors, one per station
  │    │   │   │   │   │   │   │
  │   (L) (L) (L) (L) (L) (L) (L)   ← 7 LEDs, anodes to resistors
  │    │   │   │   │   │   │   │
  └────┴───┴───┴───┴───┴───┴───┴── – rail → Pi GND
```

Each resistor's free leg goes to its assigned GPIO pin via a jumper.

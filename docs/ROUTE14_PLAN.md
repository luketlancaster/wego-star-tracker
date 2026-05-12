# Route 14 — 118-LED Bus Tracker

Plan for a second Metroboard tracking WeGo Route 14 (Whites Creek / North
Nashville via Buena Vista) with one individual LED per stop on both legs
of the route, driven by real-time vehicle positions.

## Route overview

Route 14 runs a loop between Music City Central (downtown, Bay 8) and
North Nashville Transit Center, via Dickerson Pike, Baptist World Center
Dr, Whites Creek Pike, Buena Vista, and Clarksville Pike. Two trip
patterns, one per direction:

| Direction | Headsign                         | Stops | Trips/day |
|-----------|----------------------------------|-------|-----------|
| 0         | NORTH NASHVILLE VIA BUENA VISTA  | 58    | ~89       |
| 1         | DOWNTOWN VIA BUENA VISTA         | 60    | ~93       |

6 timepoints per direction (the scheduled checkpoints), ~38 minutes
end to end. 117 unique stop_ids across both directions — only `MCC5_8`
(Music City Central) is shared.

### Why real-time works here

Unlike the WeGo Star, Route 14 buses **appear in the GTFS-RT vehicle
positions feed**. This means we get live lat/lon every ~15 s instead of
relying on schedule windows with synthetic dwell padding. The schedule
remains useful as a fallback for feed outages.

## Board layout — the loop

The outbound and inbound legs use almost entirely different stop_ids
(opposite sides of the street, different bays at the transit centers).
Every stop gets its own LED. The board traces the full loop as two
parallel rows:

```
  OUTBOUND (58 LEDs, left → right)
  ┌─────────────────────────────────────────────────────────────────────┐
  │ 1       2       3    ...   24*       ...    47*      ...    58     │
  │ Central Union   1st        Whites Ck        Clarksville    NNTC   │
  │ (MCC)                      & Moormans       & Fairview     Bay 9  │
  └───────────────────────────────────────────────────────────────────┬┘
                                                                     │ turnaround
  ┌───────────────────────────────────────────────────────────────────┘
  │ 59      60      61   ...   92*       ...    114*     ...   117 118│
  │ NNTC    Rosa    Cliff      Whites Ck        1st &          Union  │
  │ Bay 10  Parks              & Moormans       Spring         Central│
  │                                                            (MCC)  │
  └─────────────────────────────────────────────────────────────────────┘
  INBOUND (60 LEDs, left → right)
                                                          * = timepoint
```

A bus departs Music City Central (LED 1), crawls across the top row to
N Nashville TC (LED 58), wraps to the inbound row (LED 59), and crawls
back to Music City Central (LED 118). At typical headways you'll see
1–3 lit dots tracing the loop simultaneously.

`MCC5_8` appears at positions 1 and 118 — two physical LEDs for the
same stop_id. When a bus is at Music City Central, both light up (or
just the one matching the trip's direction_id, depending on whether the
RT feed distinguishes).

### Full stop map

**Outbound leg (direction 0, trip 367950)**

| LED | stop_id      | Name                                           | TP |
|-----|--------------|------------------------------------------------|----|
| 1   | MCC5_8       | Central 5th Ave – Bay 8                        | *  |
| 2   | UNI2AEF      | Union St & 2nd Ave EB                          |    |
| 3   | 1SWOONM      | S 1st St & Woodland St NB                      |    |
| 4   | 1SJAMNM      | N 1st St & James Robertson Pkwy NB             |    |
| 5   | N1SOLDNM     | N 1st St & Oldham St NB                        | *  |
| 6   | DICGRANN     | Dickerson Pike & Grace St NB                   |    |
| 7   | DICHANNN     | N Dickerson Pike & Hancock St NB               |    |
| 8   | DICCLENN     | N Dickerson Pike & Cleveland St NB             |    |
| 9   | DICEVANN     | Dickerson Pike & Evanston Ave NB               |    |
| 10  | DICRICNN     | Dickerson Pike & Richardson Ave NB             |    |
| 11  | FERBRIWN     | Fern Ave & Brick Church Pk WB                  |    |
| 12  | BAPVASWN     | Baptist World Center Dr & Vashti St WB         |    |
| 13  | BAPWEANN     | Baptist World Center Dr & Weakley Ave NB       |    |
| 14  | BAPLOCNM     | Baptist World Center Dr & Lock Rd NB           |    |
| 15  | BAPSEMNF     | Baptist World Center Dr & Seminary St NB       |    |
| 16  | BAPHAYN      | Baptist World Center Dr & Haynes Meade Cir NB  |    |
| 17  | BAPMEANM     | Baptist World Center Dr & Meade Ave NB         |    |
| 18  | BAPTRINN     | Baptist World Center Dr & Trinity Ln NB        |    |
| 19  | WHITONWN     | Whites Creek Pike & Toney Rd WB                |    |
| 20  | WHILUZNF     | Whites Creek Pike & Luzon St NB                |    |
| 21  | WHINOCWN     | Whites Creek Pike & E Nocturne Dr NB           |    |
| 22  | WHIAVANN     | Whites Creek Pike & Avalon Dr NB               |    |
| 23  | WHIFRANN     | Whites Creek Pike & Francis St NB              |    |
| 24  | WHIMOONN     | Whites Creek Pike & Moormans Arm Rd            | *  |
| 25  | REVWHIWF     | Revels Dr & Whites Creek Pk WB                 |    |
| 26  | REVROWWN     | Revels Dr & Rowan Dr WB                        |    |
| 27  | ROWCARWN     | Rowan Dr & Carvath Dr WB                       |    |
| 28  | ROWBONWN     | Rowan Dr & Bontemps Dr WB                      |    |
| 29  | ROWCROWN     | Rowan Dr & Crouch Dr WB                        |    |
| 30  | ROWBUESN     | Rowan Dr & Buena Vista Pike SB                 |    |
| 31  | BUEHUMNN     | Buena Vista Pike & Hummingbird Dr NB           |    |
| 32  | BUEKINNN     | Buena Vista Pike & Kings Ln NB                 |    |
| 33  | BUEKINNM     | Buena Vista Pike & Kings Ln NB                 |    |
| 34  | BUEBUEWF     | Buenaview Blvd & Buena Vista Pike WB           |    |
| 35  | BOYBUESF     | Boyd Dr & Buenaview Blvd SB                    | *  |
| 36  | BOYFARSF     | Boyd Dr & Farmview Dr SB                       |    |
| 37  | LYTBOYSF     | Lytle Dr & Boyd Dr SB                          |    |
| 38  | MEALYTSN     | Meadow Hill Dr & Lytle Dr SB                   |    |
| 39  | KINMEAWF     | Kings Ln & Meadow Hill Dr WB                   |    |
| 40  | KINBOYWN     | Kings Ln & Boyd Dr WB                          |    |
| 41  | KINHAYWN     | Kings Ln & Haynes Park Dr WB                   |    |
| 42  | KINCLAW      | Kings Ln & Clarksville Pk WB                   |    |
| 43  | KINTIMWN     | Kings Ln & Timothy Dr WB                       |    |
| 44  | CRECRESN     | Creekwood & Creekland Ct SB                    |    |
| 45  | CRECRWSN     | Creekwood & Creekway Ct SB                     |    |
| 46  | TIMFAISN     | Timothy Dr & Fairview Dr SB                    |    |
| 47  | CLAFAISF     | Clarksville Pike & Fairview Dr SB              | *  |
| 48  | CLAWHASN     | Clarksville Pike & W Hamilton Ave SB           |    |
| 49  | CLAABESN     | Clarksville Pike & Abernathy Rd SB             |    |
| 50  | CLALAWSN     | Clarksville Pike & Lawrence SB                 |    |
| 51  | CLAASHSN     | Clarksville Pike & Ashland City Hwy SB         |    |
| 52  | CLAMANSF     | Clarksville Pike & Manchester Ave S            |    |
| 53  | CLASHASN     | Clarksville Pike & S Hamilton Rd SB            |    |
| 54  | CLASHASF     | Clarksville Pike & S Hamilton Rd SB            |    |
| 55  | CLACLISN     | Clarksville Pike & Cliff Dr SB                 |    |
| 56  | CLAEDTSN     | Clarksville Pike & Ed Temple Blvd S            |    |
| 57  | CLAEDSM      | Clarksville Pike & Ed Temple Blvd S            |    |
| 58  | NNTC_9       | N Nashville TC Bay 9                           | *  |

**Inbound leg (direction 1, trip 367995)**

| LED | stop_id      | Name                                           | TP |
|-----|--------------|------------------------------------------------|----|
| 59  | NNTC_10      | N Nashville TC Bay 10                          | *  |
| 60  | CLAROSNN     | Clarksville Pike & Rosa Parks Blvd NB          |    |
| 61  | CLACLINN     | Clarksville Pike & Cliff Dr NB                 |    |
| 62  | CLASHANF     | Clarksville Pike & S Hamilton Rd NB            |    |
| 63  | CLAMANNN     | Clarksville Pike & Manchester Ave S NB         |    |
| 64  | CLAASHNF     | Clarksville Pike & Ashland City Hwy NB         |    |
| 65  | CLALAWNF     | Clarksville Pike & Lawrence NB                 |    |
| 66  | CLAABENN     | Clarksville Pike & Abernathy Rd NB             |    |
| 67  | CLAFAINM     | Clarksville Pike & E Fairview Dr NB            | *  |
| 68  | FAICLAWF     | Fairview Dr & Clarksville Pk WB                |    |
| 69  | TIMFAINF     | Timothy Dr & Fairview Dr NB                    |    |
| 70  | CRECREWN     | Creekway Ct & Creekwood WB                     |    |
| 71  | CRECRENF     | Creekwood & Creekland Ct NB                    |    |
| 72  | KINTIMEF     | Kings Ln & Timothy Dr EB                       |    |
| 73  | KINCLAEN     | Kings Ln & Clarksville Pk EB                   |    |
| 74  | KINHAYEN     | Kings Ln & Haynes Park Dr EB                   |    |
| 75  | KINBOYEN     | Kings Ln & Boyd Dr EB                          |    |
| 76  | KINMEAEN     | Kings Ln & Meadow Hill Dr EB                   |    |
| 77  | MEALYTNN     | Meadow Hill Dr & Lytle Dr NB                   |    |
| 78  | LYTBOYNN     | Lytle Dr & Boyd Dr NB                          |    |
| 79  | BOYFARNN     | Boyd Dr & Farmview Dr NB                       |    |
| 80  | BOYBUENN     | Boyd Dr & Buenaview Blvd NB                    | *  |
| 81  | BUEBUEEM     | Buenaview Blvd & Buena Vista Pike E            |    |
| 82  | BUEBUESM     | Buena Vista Pike & Kings Ln SB                 |    |
| 83  | BUEKINSN     | Buena Vista Pike & Kings Ln SB                 |    |
| 84  | BUEHUMSN     | Buena Vista Pike & Hummingbird Dr S            |    |
| 85  | BUEWHASN     | Buena Vista Pike & W Hamilton Ave              |    |
| 86  | ROWBUENN     | Rowan Dr & Buena Vista Pike NB                 |    |
| 87  | ROWCRONN     | Rowan Dr & Crouch Dr NB                        |    |
| 88  | ROWBONEF     | Rowan Dr & Bontemps Dr EB                      |    |
| 89  | ROWCRAEN     | Rowan Dr & Cravath Dr EB                       |    |
| 90  | REVROWEF     | Revels Dr & Rowan Dr EB                        |    |
| 91  | REVWHIEN     | Revels Dr & Whites Creek Pike EB               |    |
| 92  | WHIMOOSN     | Whites Creek Pike & Moormans Arm Rd            | *  |
| 93  | WHIMALSF     | Whites Creek Pike & Malta Dr SB                |    |
| 94  | WHIPIESN     | Whites Creek Pike & Pierpoint Dr SB            |    |
| 95  | WHIAVASN     | Whites Creek Pike & Avalon Dr SB               |    |
| 96  | WHIWNSF      | Whites Creek Pike & W Nocturne Dr SB           |    |
| 97  | WHILUZSN     | Whites Creek Pike & Luzon St SB                |    |
| 98  | WHITONSN     | Whites Creek Pike & Toney Rd SB                |    |
| 99  | WHIWTRSN     | Whites Creek Pike & W Trinity Ln SB            |    |
| 100 | BAPGOOSN     | Baptist World Center Dr & Gooch St SB          |    |
| 101 | BATMEASN     | Baptist World Center Dr & Meade Dr SB          |    |
| 102 | BAPHAYSF     | Baptist World Center Dr & Haynes Meade Cr SB   |    |
| 103 | BAPSEMSN     | Baptist World Center & Seminary SB             |    |
| 104 | BAPLOCSM     | Baptist World Center Dr & Lock Dr SB           |    |
| 105 | BAPWEASN     | Baptist World Center Dr & Weakley Ave SB       |    |
| 106 | BAPUNNSM     | Baptist World Center Dr & Unnamed St SB        |    |
| 107 | BAPWILEN     | Baptist World Center Dr & Willis St EB         |    |
| 108 | BRKFERNN     | Brick Church Pike & Fern Ave NB                |    |
| 109 | DICLIGSF     | Dickerson Pike & Ligon Ave SB                  |    |
| 110 | DICRICSF     | Dickerson Pike & Richardson Ave SB             |    |
| 111 | DICEVASF     | Dickerson Pike & Evanston Rd SB                |    |
| 112 | DICCLESN     | N Dickerson Pike & Cleveland St SB             |    |
| 113 | DICGRASN     | N Dickerson Pike & Grace St SB                 |    |
| 114 | 1SSPRSM      | N 1st St & Spring St SB                        | *  |
| 115 | 1SOLDSM      | N 1st St & Oldham St SB                        |    |
| 116 | WOON1SWF     | Woodland St & N 1st St WB                      |    |
| 117 | UNI2AWN      | Union St & 2nd Ave WB                          |    |
| 118 | MCC5_8       | Central 5th Ave – Bay 8                        | *  |

## Hardware

### The problem: 118 LEDs, ~26 usable GPIO pins

A Raspberry Pi 4 has roughly 26 GPIO pins available after reserving I²C,
SPI, UART, and 1-Wire defaults. 118 LEDs need GPIO expansion.

### Approach: PCA9685 PWM LED drivers over I²C

The PCA9685 is a 16-channel, 12-bit PWM driver on an I²C bus. Eight
boards give 128 channels — enough for 118 LEDs with 10 spare.

| What                  | Detail                                      |
|-----------------------|---------------------------------------------|
| Boards                | 8× Adafruit PCA9685 breakout (product 815)  |
| Channels              | 128 (118 used, 10 spare)                    |
| Pi GPIO pins consumed | 2 (SDA on GPIO 2, SCL on GPIO 3)            |
| I²C addresses         | 0x40–0x47 (solder jumper A0–A2 on breakouts)|
| LED current           | PCA9685 can sink 25 mA per channel           |
| PWM resolution        | 12-bit (4096 steps) at configurable freq     |

Why PCA9685 over the alternatives:

- **vs. 74HC595 shift registers:** Shift registers are cheaper (~$8 for
  16 chips vs ~$120 for 8 PCA9685 breakouts) but only do on/off. The
  pulse "breathing" effect needs PWM — either hardware PWM on the driver
  or CPU-intensive bit-banging at high frequency across 118 channels.
  PCA9685 gives 12-bit hardware PWM on every channel.
- **vs. MCP23017 I²C GPIO expanders:** Same I²C bus simplicity, but no
  hardware PWM — you'd be toggling pins in software for pulse/blink.
- **vs. Charlieplexing:** 12 pins → 132 LEDs, but only one LED is truly
  on at a time (persistence of vision). No PWM per LED, wiring is a
  nightmare at 118 LEDs, and debugging is worse.

### Per-LED circuit

Same topology as the Star board — the GPIO source is a PCA9685 output
channel instead of a Pi pin:

```
PCA9685 channel ──[ 220 Ω ]──┬── LED anode (+)
                              └── LED cathode (−) ── GND rail
```

### Power budget

At ~10 mA per LED, worst case (all 118 on simultaneously) is ~1.2 A.
In practice, 1–3 buses means 1–3 LEDs lit, so typical draw is under
50 mA. The PCA9685 breakouts accept an external V+ supply separate from
the logic supply, so the LEDs can be powered from a dedicated 5V rail
(a 2A USB supply or bench PSU) rather than drawing through the Pi.

### Board address assignment

| Board | I²C addr | Solder jumpers | Channels | LEDs        | Segment                         |
|-------|----------|----------------|----------|-------------|---------------------------------|
| 0     | 0x40     | (none)         | 0–15     | 1–16        | Central → Baptist/Haynes (out)  |
| 1     | 0x41     | A0             | 0–15     | 17–32       | Baptist/Meade → BV/Kings (out)  |
| 2     | 0x42     | A1             | 0–15     | 33–48       | BV/Kings → Clarksville/Ham (out)|
| 3     | 0x43     | A0+A1          | 0–9      | 49–58       | Clarksville/Aber → NNTC (out)   |
| 4     | 0x44     | A2             | 0–15     | 59–74       | NNTC → Kings/Haynes (in)        |
| 5     | 0x45     | A0+A2          | 0–15     | 75–90       | Kings/Meadow → Revels (in)      |
| 6     | 0x46     | A1+A2          | 0–15     | 91–106      | Whites Ck/Moormans → BWC (in)   |
| 7     | 0x47     | A0+A1+A2       | 0–11     | 107–118     | BWC/Willis → Central (in)       |

### Physical layout

Two parallel rows of breadboards, one per leg of the route.

**Top row (outbound):** 4 half-size breadboards end to end (120 columns),
LEDs 1–58 left to right. At 2 columns per LED (resistor + LED), 58 LEDs
use 116 columns — fits with 4 columns to spare.

**Bottom row (inbound):** 4 half-size breadboards end to end, LEDs
59–118 left to right. 60 LEDs use 120 columns — exact fit.

The right edge of the board is the turnaround at N Nashville Transit
Center (LEDs 58–59). The left edge has Music City Central at both
corners (LED 1 top, LED 118 bottom).

PCA9685 breakouts sit behind or between the breadboard rows, daisy-
chained on the I²C bus.

Total breadboards: 8 half-size (or 4 full-size).

## Wiring

How to physically build the 118-LED board. The end state: two parallel
rows of LEDs (outbound on top, inbound on bottom), each driven by a
PCA9685 PWM channel, all sharing a common ground rail.

### Per-LED circuit (repeated 118×)

```
PCA9685 output pin ──[ 220 Ω ]──┬── LED anode (+, longer leg)
                                │
                                └── LED cathode (–, shorter leg) ── – rail ── GND
```

Identical to the Star board's circuit, except the source is a PCA9685
output channel (5V open-drain, sinks up to 25 mA) rather than a Pi GPIO
pin (3.3V).

### I²C bus — Pi to PCA9685 chain

All 8 PCA9685 boards share a single I²C bus. They daisy-chain: the Pi
connects to board 0, board 0 connects to board 1, and so on.

```
Pi GPIO header                Board 0         Board 1                Board 7
 ┌──────────┐                ┌────────┐      ┌────────┐            ┌────────┐
 │ pin 3 SDA├───────────────►│SDA  SDA├─────►│SDA  SDA├── ··· ───►│SDA     │
 │ pin 5 SCL├───────────────►│SCL  SCL├─────►│SCL  SCL├── ··· ───►│SCL     │
 │ pin 2  5V├───────────────►│VCC  VCC├─────►│VCC  VCC├── ··· ───►│VCC     │
 │ pin 6 GND├───────────────►│GND  GND├─────►│GND  GND├── ··· ───►│GND     │
 └──────────┘                └────────┘      └────────┘            └────────┘
                              addr 0x40       addr 0x41             addr 0x47
```

The Adafruit PCA9685 breakout has input headers on the left and matching
output headers on the right for exactly this daisy-chain pattern. Four
wires hop between each adjacent pair: SDA, SCL, VCC, GND.

**External LED power (V+):** The PCA9685 breakout has a separate V+
terminal block for the LED supply rail. If using a dedicated 5V supply
for the LEDs, connect it to V+ and GND on any one board — V+ is also
daisy-chained across boards. If powering from the Pi's 5V pin, the VCC
connection above already supplies V+ (a solder jumper on the breakout
bridges VCC to V+ by default).

### I²C address configuration

Each PCA9685 has 3 solder jumper pads: A0, A1, A2. The base address is
0x40; bridging a pad adds its bit:

| Board | Address | A2 | A1 | A0 | Solder pads to bridge |
|-------|---------|----|----|----|-----------------------|
| 0     | 0x40    | 0  | 0  | 0  | (none)                |
| 1     | 0x41    | 0  | 0  | 1  | A0                    |
| 2     | 0x42    | 0  | 1  | 0  | A1                    |
| 3     | 0x43    | 0  | 1  | 1  | A0 + A1               |
| 4     | 0x44    | 1  | 0  | 0  | A2                    |
| 5     | 0x45    | 1  | 0  | 1  | A0 + A2               |
| 6     | 0x46    | 1  | 1  | 0  | A1 + A2               |
| 7     | 0x47    | 1  | 1  | 1  | A0 + A1 + A2          |

Bridge the pads with a blob of solder before mounting the headers.
Verify with `i2cdetect -y 1` on the Pi — you should see all 8
addresses.

### Breadboard layout

Each LED occupies 2 breadboard columns (one for the resistor landing,
one for the LED). At 2 columns per LED:

- **Outbound row (58 LEDs):** 116 columns → 4 half-size breadboards
  (4 × 30 = 120 columns, 4 spare at the right end).
- **Inbound row (60 LEDs):** 120 columns → 4 half-size breadboards
  (exact fit).

```
                        OUTBOUND ROW (top)
   board 0 (ch 0–15)    board 1 (ch 0–15)    board 2 (ch 0–15)    board 3 (ch 0–9)
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │ BB-A: LEDs 1–16  │  │ BB-B: LEDs 17–32 │  │ BB-C: LEDs 33–48 │  │ BB-D: LEDs 49–58 │
  │ (16 LEDs)        │  │ (16 LEDs)        │  │ (16 LEDs)        │  │ (10 LEDs + 4 col │
  │                  │  │                  │  │                  │  │  spare)           │
  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
    Central → Haynes      Meade → BV/Kings     BV/Kings → Cville     Cville → NNTC

                                                                      ↕ turnaround

   board 4 (ch 0–15)    board 5 (ch 0–15)    board 6 (ch 0–15)    board 7 (ch 0–11)
  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
  │ BB-E: LEDs 59–74 │  │ BB-F: LEDs 75–90 │  │ BB-G: LEDs 91–106│  │ BB-H: LEDs 107–118
  │ (16 LEDs)        │  │ (16 LEDs)        │  │ (16 LEDs)        │  │ (12 LEDs + 6 col │
  │                  │  │                  │  │                  │  │  spare)           │
  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘
    NNTC → Kings/Hay      Kings → Revels       Moormans → BWC        BWC → Central

                        INBOUND ROW (bottom)
```

Each PCA9685 board sits behind or between its breadboard. Jumper wires
run from the board's output channels (0–15) to the resistor columns on
the breadboard.

### Single-breadboard detail (one PCA9685 + 16 LEDs)

This pattern repeats for each of the 8 board/breadboard pairs. Shown
for board 0 driving LEDs 1–16 on breadboard BB-A:

```
         col:  1  2    3  4    5  6    7  8   ...  29 30
               ↓  ↓    ↓  ↓    ↓  ↓    ↓  ↓       ↓  ↓
  + rail  ── (V+ from PCA9685 if needed) ──────────────────────
  row a    ·  W  ·  ·  W  ·  ·  W  ·  ·  W  · ... ·  ·  ·   ← PCA9685 output wire
  row b    ·  ╞══╡  ·  ╞══╡  ·  ╞══╡  ·  ╞══╡ ... ·  ·  ·   ← 220 Ω resistor
  row c    ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  · ... ·  ·  ·
  row d    ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  · ... ·  ·  ·
  row e    ·  ·  +  ·  ·  +  ·  ·  +  ·  ·  + ... ·  ·  ·   ← LED anode (long leg)
  ═════════════ center channel ═══════════════════════════════
  row f    ·  ·  −  ·  ·  −  ·  ·  −  ·  ·  − ... ·  ·  ·   ← LED cathode (short leg)
  row g    ·  ·  │  ·  ·  │  ·  ·  │  ·  ·  │ ... ·  ·  ·
  row h    ·  ·  │  ·  ·  │  ·  ·  │  ·  ·  │ ... ·  ·  ·
  row i    ·  ·  │  ·  ·  │  ·  ·  │  ·  ·  │ ... ·  ·  ·
  row j    ·  ·  K  ·  ·  K  ·  ·  K  ·  ·  K ... ·  ·  ·
  – rail  ── to PCA9685 GND / shared GND bus ──────────────────
             LED1     LED2     LED3     LED4       LED15 LED16
```

Legend:
- `W` — wire from PCA9685 output channel to resistor column
- `╞══╡` — 220 Ω resistor bridging two adjacent columns
- `+` — LED anode (long leg, in row `e`)
- `−` — LED cathode (short leg, in row `f`, same column as anode)
- `K` — short jumper from cathode column (row `j`) to `–` rail

Each LED uses columns in pairs: odd column for the PCA9685 wire +
resistor left leg, even column for the resistor right leg + LED. So
LED 1 is in columns 1–2, LED 2 in columns 3–4, ..., LED 15 in columns
29–30. The pattern is: `(2n−1, 2n)` for the nth LED on that breadboard.

For boards with fewer than 16 LEDs (board 3 has 10, board 7 has 12),
the remaining columns are unused.

### PCA9685 channel → LED wiring table

Each PCA9685 output channel connects to one LED position. The wire runs
from the output header on the PCA9685 board to row `a` of the LED's
left column on the breadboard.

**Board 0 (0x40) — breadboard BB-A (outbound, LEDs 1–16):**

| Ch | LED | stop_id    | BB column (wire→) | Name                           |
|----|-----|------------|-------------------|--------------------------------|
| 0  | 1   | MCC5_8     | 1                 | Central 5th Ave – Bay 8        |
| 1  | 2   | UNI2AEF    | 3                 | Union St & 2nd Ave             |
| 2  | 3   | 1SWOONM    | 5                 | S 1st St & Woodland St         |
| 3  | 4   | 1SJAMNM    | 7                 | N 1st St & James Robertson     |
| 4  | 5   | N1SOLDNM   | 9                 | N 1st St & Oldham St           |
| 5  | 6   | DICGRANN   | 11                | Dickerson Pk & Grace St        |
| 6  | 7   | DICHANNN   | 13                | N Dickerson Pk & Hancock St    |
| 7  | 8   | DICCLENN   | 15                | N Dickerson Pk & Cleveland St  |
| 8  | 9   | DICEVANN   | 17                | Dickerson Pk & Evanston Ave    |
| 9  | 10  | DICRICNN   | 19                | Dickerson Pk & Richardson Ave  |
| 10 | 11  | FERBRIWN   | 21                | Fern Ave & Brick Church Pk     |
| 11 | 12  | BAPVASWN   | 23                | BWC Dr & Vashti St             |
| 12 | 13  | BAPWEANN   | 25                | BWC Dr & Weakley Ave           |
| 13 | 14  | BAPLOCNM   | 27                | BWC Dr & Lock Rd               |
| 14 | 15  | BAPSEMNF   | 29                | BWC Dr & Seminary St           |
| 15 | 16  | BAPHAYN    | 30*               | BWC Dr & Haynes Meade Cir      |

*LED 16 uses columns 29–30 if spacing allows, or shift to a tighter
1-column-per-LED packing at the end. With 16 LEDs × 2 columns = 32
columns needed but only 30 available, the last LED on each full board
needs to share a column with the resistor (put the resistor inline in
the same column, legs in rows `a` and `c`, LED anode in row `e`).
Alternatively, use the first column of the next breadboard for the
overflow — but this couples boards and makes rearranging harder.

**Practical note:** 16 LEDs at 2-column spacing need 32 columns, but a
half-size breadboard only has 30. Two solutions:

1. **Tighter packing for the last LED:** Place the resistor vertically
   (both legs in the same column, rows `a` and `c`) instead of
   horizontally. This frees one column. Do this for LEDs 15 and 16 to
   fit 16 LEDs in 30 columns.
2. **Use full-size breadboards:** 63 columns each. Two full-size boards
   per row → 126 columns → 63 LEDs per board at 2-column spacing.
   Outbound (58 LEDs) fits on one, inbound (60) fits on the other, with
   room to spare. This cuts the board count from 8 to 4 but makes each
   board larger.

### Step-by-step wiring

> **Power off the Pi before wiring.** Unplug the USB-C cable. Don't
> rely on a soft shutdown — physically remove power.

**1. Prep the PCA9685 boards.**

Solder headers onto all 8 boards. Bridge the address solder jumpers per
the address table above. Verify each board's address is correct by
examining the jumper pads.

**2. Daisy-chain the PCA9685 boards.**

Lay out the 8 boards in order (0–7). Connect each pair with 4 wires:
SDA→SDA, SCL→SCL, VCC→VCC, GND→GND. The Adafruit breakout has matching
input/output headers for this.

**3. Connect the Pi to board 0.**

4 wires from the Pi GPIO header to board 0's input:

| Signal | Pi physical pin | PCA9685 input |
|--------|-----------------|---------------|
| SDA    | 3               | SDA           |
| SCL    | 5               | SCL           |
| 5V     | 2               | VCC           |
| GND    | 6               | GND           |

**4. Verify the I²C bus.**

Power on the Pi (no LEDs wired yet) and run:

```sh
sudo apt install -y i2c-tools   # if not installed
i2cdetect -y 1
```

You should see 8 addresses: 40, 41, 42, 43, 44, 45, 46, 47. If any
are missing, check that board's solder jumpers and daisy-chain wires.

**5. Wire one breadboard at a time.**

For each breadboard (BB-A through BB-H):

a. Insert the resistors: for each LED position, push one resistor leg
   into row `b` of the odd column, the other into row `b` of the even
   column.

b. Insert the LEDs: long leg (anode, `+`) into row `e` of the even
   column, short leg (cathode, `–`) into row `f` of the same column.

c. Wire cathodes to ground: short jumper from row `j` of each LED's
   column to the `–` power rail.

d. Connect the `–` rail to PCA9685 GND (already on the daisy-chain).

e. Wire PCA9685 output channels: one jumper per LED from the channel's
   output pin on the PCA9685 board to row `a` of the LED's odd column
   (the resistor's input side).

f. Test before moving to the next breadboard — run the sweep script
   targeting just the boards wired so far.

**6. Connect LED power supply (if separate).**

If using a dedicated 5V supply for the LEDs, connect it to the V+ and
GND screw terminal on any PCA9685 board. If using the Pi's 5V rail,
this is already handled by the VCC daisy-chain (the default solder
jumper on the Adafruit breakout bridges VCC to V+).

**7. Visual sanity check.**

- 8 PCA9685 boards, daisy-chained with 4 wires between each pair. ✓
- 4 wires from Pi to board 0. ✓
- 118 resistors, each in row `b`, bridging two columns. ✓
- 118 LEDs, long leg in row `e`, short leg in row `f`. ✓
- 118 cathode-to-`–`-rail jumpers. ✓
- 118 PCA9685-channel-to-column jumpers. ✓
- Ground rails connected to PCA9685 GND. ✓

### Smoke test

```sh
cd ~/wego-star-tracker
source .venv/bin/activate
python scripts/hello_route14.py
```

Expected behavior:

1. Sweep LEDs 1–118 in order (outbound row left→right, then inbound row
   left→right), each on for 0.1 s.
2. Reverse sweep, 118→1.
3. PWM dimming ramp on each LED (0% → 100% → 0%) to verify all 128
   PCA9685 channels produce smooth brightness.
4. All LEDs on for 2 s, then dark.

If the sweep order matches the physical left-to-right layout on both
rows, the wiring is correct.

### Troubleshooting

**`i2cdetect` shows fewer than 8 addresses.**
A board's address jumpers are wrong or its daisy-chain wires are loose.
Check continuity on SDA and SCL across the chain. A missing board
breaks the chain for all boards after it.

**One LED never lights, the others are fine.**
Polarity (long leg in wrong row) or a leg isn't fully seated. Second
most likely: the PCA9685 output jumper is in the wrong column.

**A whole group of 16 LEDs is dark.**
That PCA9685 board isn't responding. Check its I²C address, the daisy-
chain connections to/from it, and that its headers are soldered.

**LEDs are very dim.**
Missing cathode-to-`–`-rail jumper, or the `–` rail isn't connected to
GND. Without a return path, LEDs may glow faintly via leakage.

**LEDs flicker or behave erratically.**
I²C bus integrity issue. Long daisy-chains can pick up noise. Add 4.7 kΩ
pull-up resistors on SDA and SCL at the Pi end (the PCA9685 breakout
has onboard pull-ups, but 8 boards on a long bus may need stronger
ones). Keep I²C wires short and away from the LED power lines.

**Script crashes with `OSError: [Errno 121] Remote I/O error`.**
An I²C device isn't responding. Run `i2cdetect -y 1` to see which
address is missing. Reseat that board's connections.

## LED states

With both legs wired separately, direction is encoded by position —
a lit LED on the top row IS an outbound bus, bottom row IS inbound.
This simplifies the LED states compared to the Star board:

| State   | Meaning                          | PCA9685 behavior             |
|---------|----------------------------------|------------------------------|
| OFF     | No bus at this stop              | Duty cycle = 0               |
| AT_STOP | Bus stopped at or arriving       | Duty cycle = 4095 (full on)  |
| NEARBY  | Bus between this stop and next   | Duty cycle ∝ distance (dimmer as bus moves away) |

The NEARBY state is optional polish — it smooths the visual so the dot
doesn't teleport between stops. The PCA9685's 12-bit resolution makes
smooth distance-based dimming trivial.

The Star board's BOTH state (pulse when both directions overlap at one
station) isn't needed — outbound and inbound have separate LEDs. The
only exception is `MCC5_8` at positions 1 and 118, where both LEDs
could light if a bus is loading at Central for both directions. This
just works — two LEDs on, one per row.

## Software architecture

### New modules

```
src/wego_metroboard/
  route14/
    __init__.py
    stops.py            118 Stop dataclasses with stop_id, name, lat, lon, board, channel
    tracker.py          real-time vehicle → nearest-stop snapping
    pca9685_leds.py     PCA9685-backed LED controller
scripts/
    run_route14.py      main loop: RT poll + schedule fallback + LED tick
    hello_route14.py    hardware smoke test (sweep + dimming demo)
```

### stops.py — 118 stops with PCA9685 addressing

```python
@dataclass(frozen=True)
class Stop:
    stop_id: str
    name: str
    led: int            # 1-based position in the loop (1–118)
    direction: int      # 0 = outbound leg, 1 = inbound leg
    lat: float
    lon: float
    board: int          # PCA9685 board index (0–7)
    channel: int        # channel on that board (0–15)
    timepoint: bool     # True for the 12 scheduled timepoints
```

Two lookup dicts:
- `BY_STOP_ID: dict[str, Stop]` — for RT feed stop_id matching
- `BY_LED: dict[int, Stop]` — for sequential sweep / animation

### tracker.py — snapping vehicle positions to stops

1. Fetch `vehiclepositions.pb`, filter to `route_id == "14"`.
2. For each vehicle, use `current_status` and `stop_id` from the RT
   feed when available (GTFS-RT may report these directly for buses).
3. If only lat/lon is available, compute haversine distance to all
   stops on the matching direction's leg (58 or 60 stops, not all 118).
   Snap to the nearest within 200 m.
4. Return `dict[str, VehicleSnap]` keyed by vehicle_id:

```python
@dataclass
class VehicleSnap:
    stop_id: str            # nearest stop
    led: int                # LED position (1–118)
    distance_m: float       # meters from the snapped stop
    direction_id: int       # 0 or 1
```

This gives the LED layer enough to light the stop LED and optionally
dim adjacent LEDs for the NEARBY effect.

### pca9685_leds.py — LED controller

```python
class Route14Leds:
    def __init__(self, stops: Sequence[Stop]):
        # Initialize 8 PCA9685 boards via adafruit-circuitpython-pca9685
        ...

    def update(self, snaps: dict[str, VehicleSnap]):
        # Set duty cycle for each LED based on vehicle proximity
        # Full brightness at the snapped stop, dimmed for NEARBY
        ...

    def all_off(self):
        # Zero all 128 channels across all 8 boards
        ...
```

No tick loop needed for blink/pulse — the simplified LED states (off /
on / dimmed) are all static duty-cycle writes. The visual movement
comes from the 30 s poll cycle updating which LED is lit as the bus
progresses.

### run_route14.py — main loop

```
boot:
  configure I²C bus
  init 8× PCA9685 boards
  init Route14Leds(STOPS)
  load today's schedule windows as fallback

every 30 s:
  try:
    fetch vehiclepositions.pb
    filter to route_id == "14"
    snap each vehicle to nearest stop
    source = "realtime"
  except (network error, empty feed, no vehicles):
    compute active stops from schedule windows
    source = "schedule"

  leds.update(snaps)
  log vehicle positions + source

on date rollover:
  reload schedule windows

on SIGINT:
  leds.all_off()
  exit
```

Single-threaded, single loop. No tick needed since there are no
animation states to advance.

### Reuse from the Star codebase

| Module        | Reuse                                                    |
|---------------|----------------------------------------------------------|
| feeds.py      | `fetch_vehicle_positions()` works as-is                  |
| schedule.py   | `windows_for_today(route_id="14")` works as-is           |
| leds.py       | `state_for()` not needed — direction encoded by position |
| gpio.py       | Not used — PCA9685 replaces gpiozero                     |
| stations.py   | Not used — replaced by route14/stops.py                  |

## Dependencies

New Python packages:

| Package                               | Purpose                           |
|---------------------------------------|-----------------------------------|
| `adafruit-circuitpython-pca9685`      | PCA9685 I²C driver                |
| `adafruit-circuitpython-busdevice`    | I²C bus abstraction (dep of above)|
| `adafruit-blinka`                     | CircuitPython compatibility on Pi |

## Phases

### R14-P0 — Data + software, no hardware

Prove the software pipeline without any LEDs.

1. Generate `route14/stops.py` from GTFS data (all 118 positions).
2. Write `tracker.py` with nearest-stop snapping.
3. Write `run_route14.py` in mock/console mode — print which stops are
   active each cycle instead of driving LEDs.
4. Verify against the live GTFS-RT feed: do buses appear? Do they snap
   to reasonable stops?

Exit criteria: console output shows Route 14 buses moving through stops
in geographic order, matching what you see on Google Maps.

### R14-P1 — Hardware bring-up

Prove the PCA9685 wiring with a smoke test.

1. Wire one PCA9685 breakout + 16 LEDs on a breadboard.
2. Write `hello_route14.py`: sweep test (light each LED in sequence),
   plus a dimming ramp to verify PWM works per channel.
3. Add boards one at a time. Each time, extend the sweep to cover the
   new channels before wiring the next board.
4. Full 118-LED sweep across all 8 boards.

Exit criteria: all 118 LEDs light in route order, PWM dimming works on
every channel.

### R14-P2 — Real-time tracking

Connect software to hardware.

1. Integrate `pca9685_leds.py` with the main loop.
2. Run `run_route14.py` against the live feed with real LEDs.
3. Tune the nearest-stop snapping threshold.
4. Add schedule fallback for feed outages.
5. Add the NEARBY dimming effect (optional — solid on/off may be enough).

Exit criteria: LEDs track actual Route 14 buses in real time.

### R14-P3 — Polish

1. Physical board / enclosure with route map and stop labels.
2. systemd service for auto-start.
3. Wiring documentation (new WIRING_ROUTE14.md).

## Shopping list

Everything below is needed beyond what's already on hand from the Star
board (the Pi, SD card, USB-C power supply for the Pi, and basic tools).

### PCA9685 PWM driver boards

8 boards, daisy-chained on I²C. Each board drives up to 16 LEDs.

- **8× Adafruit 16-Channel 12-bit PWM/Servo Driver — I²C interface — PCA9685**
  Adafruit product 815. ~$15 each.
  https://www.adafruit.com/product/815

  These come with header pins (unsoldered). You'll solder the 2×3 pin
  header for I²C/power chaining and the row of 4×16 output headers.

  Each board has 3 solder jumper pads (A0, A1, A2) that set its I²C
  address. One board gets no jumpers (0x40), and you bridge pads in
  binary for the other 7 (see the board address table above).

### LEDs

118 individual LEDs. Any standard 5 mm through-hole LED works. Options:

- **120× 5 mm diffused LEDs, single color**
  (2 spares for dead-on-arrival or bent leads.)
  Packs of 100 are common on Amazon/Adafruit for ~$5–8. You'll need
  two packs or one 200-count.
  Adafruit has individual colors:
  - Red: product 299 (25-pack, ~$4) — need 5 packs
  - Green: product 298 (25-pack, ~$4)
  - Blue: product 780 (25-pack, ~$4)
  - Warm white: product 4203 (25-pack, ~$4)

  Or a mixed-color approach: one color for outbound (top row), another
  for inbound (bottom row). E.g., 60 green + 60 blue.

  **Diffused** (frosted) LEDs look better on a board — the glow is even
  rather than a harsh point. Clear/water-clear LEDs are brighter but
  less pleasant at close range.

### Resistors

- **120× 220 Ω resistors (¼ watt, through-hole)**
  Color bands: red-red-brown-gold. 330 Ω also works (dimmer but safer
  margin). Anything 220–330 Ω is fine for 5V logic driving a ~2V LED
  at ~10 mA.
  Packs of 100 are ~$2–3. Need two packs.
  Adafruit product 2780 (25-pack, ~$1).

### Breadboards

- **8× half-size solderless breadboard (30-column, 400-tie-point)**
  4 for the outbound row, 4 for the inbound row.
  Adafruit product 64. ~$5 each.
  https://www.adafruit.com/product/64

  Or: **4× full-size breadboard (63-column, 830-tie-point)**
  2 for outbound, 2 for inbound.
  Adafruit product 239. ~$6 each.
  https://www.adafruit.com/product/239

  Half-size are easier to arrange physically; full-size mean fewer
  board-to-board joints but are harder to curve into a layout.

### Jumper wires

- **1× jumper wire kit (M-to-M, assorted lengths)**
  Adafruit product 758. ~$4.
  https://www.adafruit.com/product/758

  You need at minimum:
  - 118× short M-to-M (LED cathode column → `–` rail) — cut from
    solid-core wire or use pre-cut jumper kits
  - 4× M-to-F or M-to-M for Pi → first PCA9685 (SDA, SCL, 5V, GND)
  - ~14× short M-to-M for daisy-chaining I²C + power between PCA9685
    boards (SDA, SCL, V+, GND between each pair — shared bus, so the
    wires just hop board to board)

- **1× solid-core hookup wire spool (22 AWG)**
  For the 118 cathode-to-ground-rail jumpers and the 118 PCA9685-
  channel-to-resistor jumpers. Pre-cut jumper kits work but a spool
  lets you cut exact lengths.
  Adafruit product 290 (black, 25 ft, ~$3) or product 288 (red).
  https://www.adafruit.com/product/290

### Power supply

- **1× 5V 2A–4A power supply with barrel jack or USB-C**
  Powers the LEDs via the PCA9685 V+ rail, separate from the Pi's own
  supply. At ~10 mA per LED × 118 LEDs = 1.18 A worst case (all on),
  but in practice 1–3 LEDs are lit at a time. 2A is more than enough.
  A second USB-C phone charger works. Or a bench supply if you have one.

  Alternatively, if the Pi's 5V supply has headroom (most 3A Pi supplies
  do), you can tap the Pi's 5V pin (physical pin 2 or 4) to power the
  PCA9685 V+ rail directly. This saves a power supply but means the Pi
  and LEDs share a single supply — fine for 1–3 LEDs lit at once.

### Soldering supplies

The PCA9685 breakout boards ship with unsoldered headers. You'll need:

- Soldering iron + solder (if not already on hand)
- The included header pins come in the box — just solder them on

### Optional but recommended

- **Wire strippers** (if using solid-core wire from a spool)
- **Helping hands / PCB holder** (for soldering the PCA9685 headers)
- **Multimeter** (for diagnosing wiring issues — continuity mode)
- **Labels / label maker** (for marking stop names on the board)
- **Mounting board** (foam core, MDF, or similar) to mount the
  breadboards and PCA9685 boards into a single display

### Summary

| Item                                   | Qty | Est. cost |
|----------------------------------------|-----|-----------|
| Adafruit PCA9685 breakout (#815)       | 8   | ~$120     |
| 5 mm diffused LEDs                     | 120 | ~$12      |
| 220 Ω resistors (¼W)                  | 120 | ~$5       |
| Half-size breadboards (#64)            | 8   | ~$40      |
| Jumper wire kit (#758)                 | 1   | ~$4       |
| Solid-core wire spool (#290)           | 1   | ~$3       |
| 5V power supply (or reuse Pi's)       | 0–1 | ~$0–10    |
| **Total (new parts only)**             |     | **~$185–195** |

The Pi itself is already on hand from the Star board. If the two boards
share the Pi, the Route 14 board just needs the I²C connection — no
second Pi required.

## Feather migration

The PCA9685 approach works identically on the ESP32-S3 Feather (same
I²C protocol, same Adafruit libraries in CircuitPython). The real-time
tracking piece requires network access — the Feather has Wi-Fi, so it
can fetch the GTFS-RT feed directly. The schedule fallback would use the
same pre-computed JSON pack approach from the Star board's Feather
migration plan.

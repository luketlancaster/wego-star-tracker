"""Canonical station list for the WeGo Star (GTFS route_id=90).

Order is geographic, west (Riverfront, downtown Nashville) to east (Lebanon).
GPIO pins are BCM numbering on a Raspberry Pi; see docs/WIRING.md.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Station:
    stop_id: str
    name: str
    lat: float
    lon: float
    gpio: int  # BCM pin


# fmt: off
STATIONS: tuple[Station, ...] = (
    Station("MCSRVRF",  "Riverfront",       36.161803, -86.773763, 17),
    Station("MCSDONEL", "Donelson",         36.167003, -86.666539, 27),
    Station("MCSHERM",  "Hermitage",        36.190234, -86.605609, 22),
    Station("MCSMJ",    "Mt. Juliet",       36.199384, -86.517000, 23),
    Station("MCSMS",    "Martha",           36.228922, -86.425777, 24),
    Station("MCSHAM",   "Hamilton Springs", 36.234559, -86.367777, 25),
    Station("MCSLB",    "Lebanon",          36.212085, -86.297240,  5),
)
# fmt: on

BY_STOP_ID: dict[str, Station] = {s.stop_id: s for s in STATIONS}

"""Tests for the schedule module: window queries and direction inference."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import dedent

import pytest

from wego_metroboard.schedule import (
    StopWindow,
    active_stops_at,
    outbound_direction_id,
)


def _at(hh: int, mm: int, ss: int = 0) -> datetime:
    # active_stops_at only consults hour/minute/second — date is irrelevant.
    return datetime(2026, 1, 1, hh, mm, ss)


def _w(stop_id: str, start_s: int, end_s: int, trip_id: str, direction_id: int) -> StopWindow:
    return StopWindow(stop_id, start_s, end_s, trip_id, direction_id)


def test_active_stops_at_returns_direction_sets() -> None:
    windows = [
        _w("MCSRVRF", 8 * 3600, 8 * 3600 + 120, "t1", 0),
        _w("MCSDONEL", 9 * 3600, 9 * 3600 + 120, "t2", 1),
    ]

    assert active_stops_at(windows, _at(8, 0, 30)) == {"MCSRVRF": {0}}
    assert active_stops_at(windows, _at(9, 1)) == {"MCSDONEL": {1}}


def test_active_stops_at_overlap_returns_both_directions() -> None:
    windows = [
        _w("MCSMJ", 17 * 3600, 17 * 3600 + 120, "out1", 0),
        _w("MCSMJ", 17 * 3600 + 30, 17 * 3600 + 150, "in1", 1),
    ]

    # Mid-overlap: both windows are open.
    assert active_stops_at(windows, _at(17, 1)) == {"MCSMJ": {0, 1}}


def test_active_stops_at_outside_windows_is_empty() -> None:
    windows = [_w("MCSRVRF", 8 * 3600, 8 * 3600 + 120, "t1", 0)]

    assert active_stops_at(windows, _at(7, 59)) == {}
    assert active_stops_at(windows, _at(8, 5)) == {}


def _write_csv(path: Path, body: str) -> None:
    path.write_text(dedent(body).lstrip())


@pytest.fixture
def gtfs_dir(tmp_path: Path) -> Path:
    # Two outbound trips originating at Riverfront (direction_id=0), one
    # inbound originating at Lebanon (direction_id=1). Route id matches the
    # WeGo Star default. service_id is intentionally varied so we can test
    # the services filter.
    _write_csv(
        tmp_path / "trips.txt",
        """
        route_id,service_id,trip_id,direction_id
        90,WK,out1,0
        90,WK,out2,0
        90,WK,in1,1
        90,SAT,out_sat,0
        99,WK,other,0
        """,
    )
    _write_csv(
        tmp_path / "stop_times.txt",
        """
        trip_id,arrival_time,departure_time,stop_id,stop_sequence
        out1,08:00:00,08:00:00,MCSRVRF,1
        out1,08:30:00,08:30:00,MCSLB,7
        out2,09:00:00,09:00:00,MCSRVRF,1
        out2,09:30:00,09:30:00,MCSMJ,4
        in1,07:00:00,07:00:00,MCSLB,1
        in1,07:45:00,07:45:00,MCSRVRF,7
        out_sat,10:00:00,10:00:00,MCSRVRF,1
        other,12:00:00,12:00:00,MCSRVRF,1
        """,
    )
    return tmp_path


def test_outbound_direction_id_infers_from_riverfront_origin(gtfs_dir: Path) -> None:
    assert outbound_direction_id(gtfs_dir) == 0


def test_outbound_direction_id_respects_service_filter(gtfs_dir: Path) -> None:
    # Restricting to weekday service_id only excludes out_sat; result still 0.
    assert outbound_direction_id(gtfs_dir, services={"WK"}) == 0


def test_outbound_direction_id_raises_when_ambiguous(tmp_path: Path) -> None:
    # Both directions have a trip starting at MCSRVRF — degenerate feed.
    _write_csv(
        tmp_path / "trips.txt",
        """
        route_id,service_id,trip_id,direction_id
        90,WK,a,0
        90,WK,b,1
        """,
    )
    _write_csv(
        tmp_path / "stop_times.txt",
        """
        trip_id,arrival_time,departure_time,stop_id,stop_sequence
        a,08:00:00,08:00:00,MCSRVRF,1
        b,08:00:00,08:00:00,MCSRVRF,1
        """,
    )

    with pytest.raises(ValueError, match="cannot determine outbound"):
        outbound_direction_id(tmp_path)

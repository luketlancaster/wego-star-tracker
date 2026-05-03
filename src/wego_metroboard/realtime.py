"""Filter GTFS-realtime feeds down to active WeGo Star stations."""

from __future__ import annotations

from google.transit import gtfs_realtime_pb2

from wego_metroboard.feeds import WEGO_STAR_ROUTE_ID
from wego_metroboard.stations import BY_STOP_ID

# VehicleStopStatus enum values from gtfs-realtime.proto:
#   0 = INCOMING_AT, 1 = STOPPED_AT, 2 = IN_TRANSIT_TO
_STOPPED_AT = 1


def active_stop_ids(feed: gtfs_realtime_pb2.FeedMessage) -> set[str]:
    """Return stop_ids of WeGo Star stations with a vehicle currently STOPPED_AT.

    Only returns stop_ids present in BY_STOP_ID — i.e., the 7 wired stations.
    Anything else (a yard stop, an unmapped intermediate point, etc.) is dropped.
    """
    active: set[str] = set()
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue
        v = entity.vehicle
        if v.trip.route_id != WEGO_STAR_ROUTE_ID:
            continue
        if v.current_status != _STOPPED_AT:
            continue
        if v.stop_id in BY_STOP_ID:
            active.add(v.stop_id)
    return active

"""WeGo / Nashville MTA GTFS endpoints + protobuf fetchers."""

from __future__ import annotations

import requests
from google.transit import gtfs_realtime_pb2

GTFS_STATIC = "https://www.wegotransit.com/GoogleExport/google_transit.zip"

RT_BASE = "http://transitdata.nashvillemta.org/TMGTFSRealTimeWebService"
VEHICLE_POSITIONS = f"{RT_BASE}/vehicle/vehiclepositions.pb"
TRIP_UPDATES = f"{RT_BASE}/tripupdate/tripupdates.pb"
SERVICE_ALERTS = f"{RT_BASE}/alert/alerts.pb"

WEGO_STAR_ROUTE_ID = "90"


def fetch_vehicle_positions(timeout: float = 10.0) -> gtfs_realtime_pb2.FeedMessage:
    """GET vehiclepositions.pb and parse it into a FeedMessage."""
    resp = requests.get(VEHICLE_POSITIONS, timeout=timeout)
    resp.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed

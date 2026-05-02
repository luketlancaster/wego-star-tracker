"""WeGo / Nashville MTA GTFS endpoints.

Phase 0 only needs the constants. Protobuf fetchers will land in Phase 1.
"""

GTFS_STATIC = "https://www.wegotransit.com/GoogleExport/google_transit.zip"

RT_BASE = "http://transitdata.nashvillemta.org/TMGTFSRealTimeWebService"
VEHICLE_POSITIONS = f"{RT_BASE}/vehicle/vehiclepositions.pb"
TRIP_UPDATES = f"{RT_BASE}/tripupdate/tripupdates.pb"
SERVICE_ALERTS = f"{RT_BASE}/alert/alerts.pb"

WEGO_STAR_ROUTE_ID = "90"

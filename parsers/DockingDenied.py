from start import cleanup_event


def parse(entry):
    entry = cleanup_event(entry, ["MarketID"])

    return entry


CONTEXT = """
The station is refusing to let us dock.
Notify if the station is refusing docking for other reasons than distance.
"""

## {'event': 'DockingDenied', 'Reason': 'RestrictedAccess', 'MarketID': 3701565440, 'StationName': 'H3G-93T', 'StationType': 'FleetCarrier'}

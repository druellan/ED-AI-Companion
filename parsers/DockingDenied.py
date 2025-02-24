# We only ptovide information for reasons other than distance

from start import cleanup_event


def parse(entry):
    entry = cleanup_event(entry, ["MarketID"])

    return entry


CONTEXT = """
The station is refusing to let us dock.
Only inform reasons other than distance.
"""

## {'event': 'DockingDenied', 'Reason': 'RestrictedAccess', 'MarketID': 3701565440, 'StationName': 'H3G-93T', 'StationType': 'FleetCarrier'}

from components.utils import cleanup_event


def parse(entry):
    entry = cleanup_event(entry, ["MarketID"])

    return entry


DESCRIPTION = "The station is refusing to let us dock."
CONTEXT = """
Notify if the station is refusing docking for other reasons than distance."""

## {'event': 'DockingDenied', 'Reason': 'RestrictedAccess', 'MarketID': 3701565440, 'StationName': 'H3G-93T', 'StationType': 'FleetCarrier'}

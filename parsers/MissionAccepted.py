from start import cleanup_event


def parse(entry):
    clean_entry = cleanup_event(entry, ["Wing", "Influence", "Reputation", "MissionID"])
    return clean_entry


CONTEXT = """
We accepted a new mission.
Stade the nature, the desitnation (if any) and how my time we have to complete it.
"""

## { "timestamp":"2025-03-15T21:52:47Z", "event":"MissionAccepted", "Faction":"Equestrian Naval Fleet", "Name":"Mission_Courier_Expansion", "LocalisedName":"Expansion Data Couriering", "TargetFaction":"Wolf 1373 Purple Rats", "DestinationSystem":"LP 397-41", "DestinationStation":"Schommer Landing", "Expiry":"2025-03-16T21:49:12Z", "Wing":false, "Influence":"++", "Reputation":"+", "Reward":115296, "MissionID":1007735718 }

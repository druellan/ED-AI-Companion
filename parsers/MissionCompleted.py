from start import cleanup_event


def parse(entry):
    clean_entry = cleanup_event(
        entry,
        [
            "MissionID",
            "DestinationSystem",
            "DestinationStation",
        ],
    )
    return clean_entry


CONTEXT = """
We completed a mission.
Stade the outcome and how we affected the factions involved.
"""

## { "timestamp":"2025-03-15T22:04:46Z", "event":"MissionCompleted", "Faction":"Equestrian Naval Fleet", "Name":"Mission_Courier_Expansion_name", "LocalisedName":"Expansion Data Couriering", "MissionID":1007735718, "TargetFaction":"Wolf 1373 Purple Rats", "DestinationSystem":"LP 397-41", "DestinationStation":"Schommer Landing", "Reward":110000, "FactionEffects":[ { "Faction":"Equestrian Naval Fleet", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":2896695396715, "Trend":"UpGood", "Influence":"+++" } ], "ReputationTrend":"UpGood", "Reputation":"+" }, { "Faction":"Wolf 1373 Purple Rats", "Effects":[ { "Effect":"$MISSIONUTIL_Interaction_Summary_EP_up;", "Effect_Localised":"The economic status of $#MinorFaction; has improved in the $#System; system.", "Trend":"UpGood" } ], "Influence":[ { "SystemAddress":2869172381097, "Trend":"UpGood", "Influence":"+++" } ], "ReputationTrend":"UpGood", "Reputation":"+" } ] }

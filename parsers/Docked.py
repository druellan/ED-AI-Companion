from start import add_states


def parse(entry):
    states = {
        "lastStationVisited": {
            "StationName": entry["StationName"],
            "StationType": entry["StationType"],
        }
    }

    add_states(states)

    return entry


CONTEXT = """
We docked to a station.
"""

## { "timestamp":"2025-02-23T15:05:51Z", "event":"Location", "DistFromStarLS":1038.730421, "Docked":true, "StationName":"Gentle Dock", "StationType":"Outpost", "MarketID":3228714752, "StationFaction":{ "Name":"Federal Reclamation Co" }, "StationGovernment":"$government_Corporate;", "StationGovernment_Localised":"Corporate", "StationAllegiance":"Federation", "StationServices":[ "dock", "autodock", "commodities", "contacts", "exploration", "missions", "outfitting", "crewlounge", "rearm", "refuel", "repair", "engineer", "missionsgenerated", "flightcontroller", "stationoperations", "powerplay", "searchrescue", "stationMenu", "livery", "socialspace", "bartender", "pioneersupplies", "apexinterstellar" ], "StationEconomy":"$economy_Industrial;", "StationEconomy_Localised":"Industrial", "StationEconomies":[ { "Name":"$economy_Industrial;", "Name_Localised":"Industrial", "Proportion":0.670000 }, { "Name":"$economy_Refinery;", "Name_Localised":"Refinery", "Proportion":0.330000 } ], "Taxi":false, "Multicrew":false, "StarSystem":"Komovoy", "SystemAddress":11666876147129, "StarPos":[70.03125,30.53125,44.15625], "SystemAllegiance":"Federation", "SystemEconomy":"$economy_Industrial;", "SystemEconomy_Localised":"Industrial", "SystemSecondEconomy":"$economy_Refinery;", "SystemSecondEconomy_Localised":"Refinery", "SystemGovernment":"$government_Corporate;", "SystemGovernment_Localised":"Corporate", "SystemSecurity":"$SYSTEM_SECURITY_medium;", "SystemSecurity_Localised":"Medium Security", "Population":7944922, "Body":"Gentle Dock", "BodyID":41, "BodyType":"Station", "Factions":[ { "Name":"Komovoy Crimson Posse", "FactionState":"None", "Government":"Anarchy", "Influence":0.026000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000, "RecoveringStates":[ { "State":"PirateAttack", "Trend":0 } ] }, { "Name":"Komovoy Fortune Inc", "FactionState":"None", "Government":"Corporate", "Influence":0.049000, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Komovoy League", "FactionState":"None", "Government":"Dictatorship", "Influence":0.078000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Komovoy Company", "FactionState":"None", "Government":"Corporate", "Influence":0.065000, "Allegiance":"Independent", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Lux Viator", "FactionState":"None", "Government":"Democracy", "Influence":0.028000, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":0.000000 }, { "Name":"Federal Reclamation Co", "FactionState":"None", "Government":"Corporate", "Influence":0.754000, "Allegiance":"Federation", "Happiness":"$Faction_HappinessBand2;", "Happiness_Localised":"Happy", "MyReputation":17.938000, "RecoveringStates":[ { "State":"Boom", "Trend":0 }, { "State":"PublicHoliday", "Trend":0 }, { "State":"Expansion", "Trend":0 } ] } ], "SystemFaction":{ "Name":"Federal Reclamation Co" } }

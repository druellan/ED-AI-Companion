def parse(entry):
    if "Factions" in entry:
        reputed_factions = [
            {"name": faction["Name"], "reputation": faction["MyReputation"]}
            for faction in entry["Factions"]
            if faction["MyReputation"] > 1
        ]

        entry["my_reputation"] = reputed_factions

    # Cleanup the entry
    keys_to_remove = [
        "Factions",
        "Multicrew",
        "StarPos",
        "SystemEconomy",
        "SystemGovernment",
        "SystemSecondEconomy",
        "SystemSecurity",
    ]
    entry = {k: v for k, v in entry.items() if k not in keys_to_remove}
    return entry


CONTEXT = """
Our ship just arrived to another system.
Provide a summary of the system.
If the system has no planets, no human presence, declare the system barren and ignore the rest.
Describe the system allegiance.
Describe the system faction and system faction state. Note if I have reputation with the faction (bad, average, good, excellent).
Note if the happiness is low, otherwise, ignore this fact.
Describe the system security level.
Describe the system economy and population.
"""

# {'event': 'FSDJump', 'Taxi': False, 'StarSystem': 'V886 Centauri', 'SystemAddress': 2931071912299, 'SystemAllegiance': 'Independent', 'SystemEconomy_Localised': 'Refinery', 'SystemSecondEconomy_Localised': 'Extraction', 'SystemGovernment_Localised': 'Democracy', 'SystemSecurity_Localised': 'High Security', 'Population': 5328590, 'Body': 'V886 Centauri', 'BodyID': 0, 'BodyType': 'Star', 'JumpDist': 7.938, 'FuelUsed': 0.507692, 'FuelLevel': 31.492308, 'SystemFaction': {'Name': 'Law of Demeter', 'FactionState': 'Boom'}, 'Conflicts': [{'WarType': 'civilwar', 'Status': 'active', 'Faction1': {'Name': 'V886 Centauri Future', 'Stake': 'Holdstock Silo', 'WonDays': 2}, 'Faction2': {'Name': 'Bureau of V886 Centauri', 'Stake': 'Phillips Analytics Installation', 'WonDays': 0}}], 'my_reputation': [{'name': 'Sirius Corporation', 'reputation': 5.98735}, {'name': 'V886 Centauri Future', 'reputation': 9.9}, {'name': 'Tamaya Empire Group', 'reputation': 6.02}]}

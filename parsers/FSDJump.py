from components.ai_tools import get_navroute
import json


def parse(entry):
    if "Factions" in entry:
        reputed_factions = [
            {"name": faction["Name"], "reputation": faction["MyReputation"]}
            for faction in entry["Factions"]
            if faction["MyReputation"] > 1
        ]

        entry["my_reputation"] = reputed_factions

    # Call get_navroute to get navigation data
    navroute_response = get_navroute()
    navroute_data = json.loads(navroute_response)

    # Add the navigation data to the entry
    if "tool_response" in navroute_data:
        entry["navroute"] = navroute_data["tool_response"]

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
If we arrived to the final destination:
- Describe the system allegiance
- Describe the system faction and system faction state. Note if I have reputation with the faction (bad, average, good, excellent)
- Note if the happiness is low, otherwise, ignore this fact
- Describe the system security level
- Describe the system economy and population
If this is a transition system:
- Ignore.
"""

# {'event': 'FSDJump', 'Taxi': False, 'StarSystem': 'V886 Centauri', 'SystemAddress': 2931071912299, 'SystemAllegiance': 'Independent', 'SystemEconomy_Localised': 'Refinery', 'SystemSecondEconomy_Localised': 'Extraction', 'SystemGovernment_Localised': 'Democracy', 'SystemSecurity_Localised': 'High Security', 'Population': 5328590, 'Body': 'V886 Centauri', 'BodyID': 0, 'BodyType': 'Star', 'JumpDist': 7.938, 'FuelUsed': 0.507692, 'FuelLevel': 31.492308, 'SystemFaction': {'Name': 'Law of Demeter', 'FactionState': 'Boom'}, 'Conflicts': [{'WarType': 'civilwar', 'Status': 'active', 'Faction1': {'Name': 'V886 Centauri Future', 'Stake': 'Holdstock Silo', 'WonDays': 2}, 'Faction2': {'Name': 'Bureau of V886 Centauri', 'Stake': 'Phillips Analytics Installation', 'WonDays': 0}}], 'my_reputation': [{'name': 'Sirius Corporation', 'reputation': 5.98735}, {'name': 'V886 Centauri Future', 'reputation': 9.9}, {'name': 'Tamaya Empire Group', 'reputation': 6.02}]}

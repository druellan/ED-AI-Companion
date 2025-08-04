from components.utils import cleanup_event


def parse(entry):
    # scan_stage = entry.get("ScanStage")

    if entry.get("TargetLocked") is False:
        return False

    if not entry.get("LegalStatus"):
        return False

    # if entry.get("LegalStatus") == "Clean":
    # return False

    # Cleanup the entry
    keys_to_remove = [
        # "Faction",
        "TargetLocked",
        "ScanStage",
        "PilotName_Localised",
        "ship",
        # "Ship_Localised"
    ]
    return cleanup_event(entry, keys_to_remove)


DESCRIPTION = "We targeted a ship for inspection"
CONTEXT = """
# Event response logic
- Bounty Value: Good ≥ 500,000 CR, Exceptional ≥ 1,000,000 CR
- Pilot Rank: Deadly, Elite, Dangerous = high risk/more danger
- Bigger ship/Combat ship: high risk/more danger
- Ship condition: HullHealth is low, Shield is low = easy win/less danger
# What to do:
- Pilot wanted: assert risk/gain for an attack, based on exceptional bounty
- Pilot clean + low hull/shield: pilot might need help
- Very dangerous ship: warn if carrying cargo

Ignore this event if the ship is not a threat or has no exceptional value
Check past history to avoid repetition
"""

# { "timestamp":"2025-05-04T21:33:54Z", "event":"ShipTargeted", "TargetLocked":true, "Ship":"krait_mkii", "Ship_Localised":"Krait Mk II", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Joseph McMullin;", "PilotName_Localised":"Joseph McMullin", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"LHS 1101 Boys", "LegalStatus":"Wanted", "Bounty":543893 }

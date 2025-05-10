def parse(entry):
    # scan_stage = entry.get("ScanStage")

    if entry.get("TargetLocked") is False:
        return False

    if not entry.get("LegalStatus"):
        return False

    # if entry.get("LegalStatus") == "Clean":
    # return False

    # Cleanup the entry
    entry.pop("Faction", None)
    entry.pop("TargetLocked", None)
    entry.pop("ScanStage", None)
    # entry.pop("Ship_Localised", None)
    entry.pop("PilotName_Localised", None)

    return entry


CONTEXT = """
We targeted a ship for inspection.
Try not to repeat identical scans. Check the previous events.
Notify only if the ship has a big bounty (> 400000 CR).
Notify only if the ship HullHealth is low.
Notify if legalStatus=wanted and PilotWank=dangerous or deadly or elite.
Ignore the event if there is nothing important to report.
"""

# { "timestamp":"2025-05-04T21:33:54Z", "event":"ShipTargeted", "TargetLocked":true, "Ship":"krait_mkii", "Ship_Localised":"Krait Mk II", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Joseph McMullin;", "PilotName_Localised":"Joseph McMullin", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"LHS 1101 Boys", "LegalStatus":"Wanted", "Bounty":543893 }

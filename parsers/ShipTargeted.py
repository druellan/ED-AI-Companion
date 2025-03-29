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
Try not to repeat consecutive scans.
Notify me if the ship has a big bounty.
Notify me if the ship is damaged, check the HullHealth. Do not notify if the ship helath is above at 80%.
"""

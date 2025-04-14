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
Notify me if the ship has a big bounty.
Notify me if the ship HullHealth is low.
You can comment about the name of the ship or the pilot if you find them funny.
Ignore the event if there is nothing to report.
"""

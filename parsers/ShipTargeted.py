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
Notify only of the pilot is wanted and the rank is dangerous, deadly or elite.
Crack a jake if the name of the pilot is funny.
Ignore the event if there is nothing to report.
"""

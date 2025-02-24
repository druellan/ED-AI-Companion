def parse(entry):
    # scan_stage = entry.get("ScanStage")

    if entry.get("TargetLocked") is False:
        print("Target lost, ignoring.")
        return False

    if not entry.get("LegalStatus"):
        print("Waiting for legal status.")
        return False

    if entry.get("LegalStatus") == "Clean":
        print("Target clean, ignoring.")
        return False

    print("Target is not clean, checking for damage.")

    # Cleanup the entry
    entry.pop("Faction", None)
    entry.pop("TargetLocked", None)
    entry.pop("ScanStage", None)
    # entry.pop("Ship_Localised", None)
    entry.pop("PilotName_Localised", None)

    return entry


CONTEXT = """
We targeted a ship for inspection.
Notify me if the ship has a big bounty. Ignore this notification otherwise.
Notify me if the ship has a bad LegalStatus AND PilotRank is above average. Do not notify if the pilot is harmless.
Notify me if the ship is damaged, check the HullHealth and ShieldHealth properties. Do not notify if the ship helath is at 100%.
"""

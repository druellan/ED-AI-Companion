from start import cleanup_event


def parse(entry):
    if not entry.get("PlayerPilot", False):
        return False

    clean_event = cleanup_event(entry, ["Fighter", "PlayerPilot"])
    return clean_event


CONTEXT = """
Our hull has received some damage!
Only notify if the hull health is critically low.
"""

## { "timestamp":"2025-03-01T22:33:25Z", "event":"HullDamage", "Health":0.452574, "PlayerPilot":true, "Fighter":false }

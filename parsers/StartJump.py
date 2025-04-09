from start import cleanup_event


def parse(entry):
    # We are only reacting to hyperspace jumps
    if entry.get("JumpType") == "Hyperspace":
        # We are only interested in the destination system
        entry = cleanup_event(entry, ["JumpType", "Taxi", "SystemAddress", "StarClass"])
        return entry

    return False


CONTEXT = """
    We are jumping to another system.
    Remind me about the destination system, specially if the system is the final destination.
    Remind me about the ship fuel.
    Mention the star only if there is something wrong with it.
"""

# { "timestamp":"2025-02-17T01:19:15Z", "event":"StartJump", "JumpType":"Hyperspace", "Taxi":false, "StarSystem":"Gurughna", "SystemAddress":3382588773082, "StarClass":"K" }
# { "timestamp":"2025-03-03T01:20:00Z", "event":"StartJump", "JumpType":"Supercruise", "Taxi":false }

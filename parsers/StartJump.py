from start.py import cleanup_event


def parse(entry):
    # We are only reacting to hyperspace jumps
    if entry.get("JumpType") != "Hyperspace":
        return False

    # We are only interested in the destination system
    entry = cleanup_event(entry, ["JumpType", "Taxi", "SystemAddress", "StarClass"])

    return entry


CONTEXT = """
    We are jumping to another system.
    Remind me about the destination system.
    Remind me about the ship fuel.
    Mention the star only if there is something wrong with it.
"""

# { "timestamp":"2025-02-17T01:19:15Z", "event":"StartJump", "JumpType":"Hyperspace", "Taxi":false, "StarSystem":"Gurughna", "SystemAddress":3382588773082, "StarClass":"K" }

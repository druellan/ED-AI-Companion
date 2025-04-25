def parse(entry):
    return entry


CONTEXT = """
    We are under attack.
    Check immediate previous events for a "$Pirate_OnDeclarePiracyAttack" message, that might be the attacker.
    These events can repear a lot, check previous events and ignore this event if you see repetition.
"""

## { "timestamp":"2025-03-15T16:33:40Z", "event":"UnderAttack", "Target":"You" }

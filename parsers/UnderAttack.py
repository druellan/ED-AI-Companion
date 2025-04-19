def parse(entry):
    return entry


CONTEXT = """
    We are under attack.
    Check immediate previous events for a "$Pirate_OnDeclarePiracyAttack" message, that might be the attacker.
    Don't repeat this event if you find other similar events in the previous events list.
"""

## { "timestamp":"2025-03-15T16:33:40Z", "event":"UnderAttack", "Target":"You" }

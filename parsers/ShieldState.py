def parse(entry):
    if not entry.get("ShieldsUp"):
        return entry
    return False


DESCRIPTION = "Our ship shields are up or down."
CONTEXT = """
Alert if the shields are down."""

## { "timestamp":"2025-03-01T22:33:25Z", "event":"ShieldState", "ShieldsUp":false }

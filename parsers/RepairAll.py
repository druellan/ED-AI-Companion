from start import add_states


def parse(entry):
    add_states({"hullHealth": 1})
    return entry


CONTEXT = """
The ship has been repaired.
"""

## { "timestamp":"2025-03-01T22:40:25Z", "event":"RepairAll", "Cost":34300 }

from start import add_states


def parse(entry):
    info = {
        "HullHealth": entry.get("HullHealth"),
    }
    add_states(info)
    return False


CONTEXT = """
"""

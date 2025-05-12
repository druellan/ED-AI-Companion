from components.state_manager import add_states


def parse(entry):
    info = {
        "HullHealth": entry.get("HullHealth"),
    }
    add_states(info)
    return False


CONTEXT = """
Our ship's loadout information was updated, or we switched ships.
"""

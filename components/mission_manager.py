# # components/mission_manager.py

# # components/mission_manager.py

import json
from collections import deque

missions_memory = deque(maxlen=50)
MISSION_FILE_PATH = "missions_memory.json"


# Keep a list of current missions
def update_missions(entry):
    global missions_memory
    missions_memory = get_missions()

    event = entry.get("event")

    # If the event is MissionAccepted, add it to the deque
    if event == "MissionAccepted":
        missions_memory.append(entry)
        _save_missions_to_file()

    # If the event is MissionCompleted or MissionRedirected, remove the corresponding mission
    elif event in ["MissionCompleted", "MissionRedirected"]:
        mission_id = entry.get("MissionID")
        for mission in list(missions_memory):
            if mission.get("MissionID") == mission_id:
                missions_memory.remove(mission)
                break
        _save_missions_to_file()


# Modify the get_missions function to use the deque
def get_missions():
    global missions_memory
    # If the deque is empty, try to load from file
    if not missions_memory:
        try:
            with open(MISSION_FILE_PATH, "r") as file:
                missions_data = json.load(file)
                missions_memory.extend(missions_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    return list(missions_memory)


# Add an initialization function for missions
def init_missions():
    global missions_memory
    try:
        with open(MISSION_FILE_PATH, "r") as file:
            missions_data = json.load(file)
            missions_memory.extend(missions_data)
    except FileNotFoundError:
        # If the file doesn't exist, create it with an empty list
        _save_missions_to_file()


def _save_missions_to_file():
    """Private helper function to save missions to the JSON file."""
    with open(MISSION_FILE_PATH, "w") as file:
        json.dump(list(missions_memory), file)

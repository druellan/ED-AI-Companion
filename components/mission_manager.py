# # components/mission_manager.py

import json
from collections import deque

missions_memory = deque(maxlen=50)


# Keep a list of current missions
def update_missions(entry):
    mission_file_path = "missions_memory.json"

    # Load existing missions into deque if it's empty
    if not missions_memory:
        try:
            with open(mission_file_path, "r") as file:
                missions_data = json.load(file)
                missions_memory.extend(missions_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    # If the event is MissionAccepted, add it to the deque
    if entry.get("event") == "MissionAccepted":
        missions_memory.append(entry)

        # Save the updated deque to file
        with open(mission_file_path, "w") as file:
            json.dump(list(missions_memory), file)

    # If the event is MissionCompleted, remove the corresponding mission
    if entry.get("event") == "MissionCompleted":
        # Find and remove the completed mission
        mission_id = entry.get("MissionID")
        for mission in list(missions_memory):
            if mission.get("MissionID") == mission_id:
                missions_memory.remove(mission)
                break

        # Save the updated deque to file
        with open(mission_file_path, "w") as file:
            json.dump(list(missions_memory), file)


# Modify the get_missions function to use the deque
def get_missions():
    # If the deque is empty, try to load from file
    if not missions_memory:
        try:
            with open("missions_memory.json", "r") as file:
                missions_data = json.load(file)
                missions_memory.extend(missions_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    return list(missions_memory)


# Add an initialization function for missions
def init_missions():
    try:
        with open("missions_memory.json", "r") as file:
            missions_data = json.load(file)
            missions_memory.extend(missions_data)
    except FileNotFoundError:
        pass

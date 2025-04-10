import os
import json
from components.constants import COLOR
from components.utils import output, get_latest_journal_file


from config import (
    JOURNAL_DIRECTORY,
    DEBUG_STATE_UPDATE,
)


# Look into the journal for the initial state of the ship
def init_state():
    journal_file_path = get_latest_journal_file(JOURNAL_DIRECTORY)

    if not journal_file_path:
        output("No journal files found.", COLOR.RED)
        return

    with open(journal_file_path, "r") as file:
        for line in file:
            entry = json.loads(line)
            filtered_entry = filter_state_events(entry)
            if filtered_entry:
                update_state(filtered_entry)


# Gather information from the ingame status and save it to the ship-state.json file
def update_state(event):
    status_path = os.path.join(JOURNAL_DIRECTORY, "Status.json")
    try:
        with open(status_path, "r") as file:
            status = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        status = {}

    filtered_status = {
        "LegalState": status.get("LegalState"),
        "Balance": status.get("Balance"),
        "FuelLevel": status.get("Fuel", {}).get("FuelMain"),
        "FuelReservoir": status.get("Fuel", {}).get("FuelReservoir"),
    }

    filtered_event = filter_state_events(event)

    # Merge filtered status with filtered event
    if event:
        filtered_status.update(filtered_event)

    add_states(filtered_status)


# Get any information and save only information related to the ship-state.json file
def add_states(status):
    state_file_path = "ship-state.json"

    if DEBUG_STATE_UPDATE:
        output(f"Updating status: {status}", COLOR.CYAN)

    # Load existing data or create empty dict
    try:
        with open(state_file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Update status while preserving other data
    data.update(status)

    # Write back to file
    with open(state_file_path, "w") as file:
        json.dump(data, file)

    return True


def filter_state_events(entry):
    filtered = {}

    if entry.get("event") == "LoadGame":
        filtered = {
            "Ship": entry.get("Ship"),
            "ShipName": entry.get("ShipName"),
            "FuelLevel": entry.get("FuelLevel"),
            "FuelCapacity": entry.get("FuelCapacity"),
            "Balance": entry.get("Credits"),
        }
    if entry.get("event") == "Loadout":
        filtered = {
            "HullHealth": entry.get("HullHealth"),
        }

    if entry.get("event") == "Fuel":
        filtered["FuelLevel"] = entry["Fuel"].get("FuelMain")
        filtered["FuelReservoir"] = entry["Fuel"].get("FuelReservoir")

    if entry.get("event") == "ReservoirReplenished":
        filtered["FuelLevel"] = entry.get("FuelMain")
        filtered["FuelReservoir"] = entry.get("FuelReservoir")

    if entry.get("event") == "RepairAll":
        filtered["HullHealth"] = 1
    if entry.get("event") == "HullDamage":
        filtered["HullHealth"] = entry.get("Health")

    if entry.get("event") == "RefuelAll":
        current_state = get_state_all()
        if "FuelMain" in current_state:
            filtered["FuelMain"] = current_state["FuelCapacity"]

    return filtered


# Get all the information from the ship-state.json file
def get_state_all():
    state_file_path = "ship-state.json"

    # Load existing data or create empty dict
    try:
        with open(state_file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    return data

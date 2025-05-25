## components/state_manager.py

import json
import os

from components.utils import get_latest_journal_file, log
from config import (
    DEBUG_STATE_UPDATE,
    JOURNAL_DIRECTORY,
)


# Look into the journal for the initial state of the ship
def init_state():
    journal_file_path = get_latest_journal_file(JOURNAL_DIRECTORY)

    if not journal_file_path:
        log("error", "No journal files found.")
        return

    with open(journal_file_path, "r") as file:
        for line in file:
            try:
                entry = json.loads(line)
                filtered_entry = filter_state_events(entry)
                if filtered_entry:
                    add_states(filtered_entry)
            except json.JSONDecodeError:
                # Skip malformed JSON lines
                continue


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
        log("debug", f"Updating status: {status}")

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
            "Ship": entry.get("Ship"),
            "ShipName": entry.get("ShipName"),
            "HullHealth": entry.get("HullHealth"),
        }
    if entry.get("event") == "ShipyardSwap":
        filtered = {
            "Ship": entry.get("ShipType"),
            "ShipName": "",
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

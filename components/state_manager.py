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

    filtered_event = filter_state_events(event)

    # Merge filtered status with filtered event
    if event:
        status.update(filtered_event)

    if "timestamp" in status:
        del status["timestamp"]

    add_states(status)


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
    event = entry.get("event")
    match event:
        case "LoadGame":
            return {
                "Ship": entry.get("Ship"),
                "ShipName": entry.get("ShipName"),
                "FuelLevel": round(entry.get("FuelLevel")),
                "FuelCapacity": round(entry.get("FuelCapacity")),
                "Balance": entry.get("Credits"),
            }

        case "Loadout":
            return {
                "Ship": entry.get("Ship"),
                "ShipName": entry.get("ShipName"),
                "HullHealth": entry.get("HullHealth"),
            }

        case "ShipyardSwap":
            return {
                "Ship": entry.get("ShipType"),
                "ShipName": "",
            }

        case "Fuel":
            return {
                "FuelLevel": round(entry["Fuel"].get("FuelMain")),
            }
        case "ReservoirReplenished":
            return {
                "FuelLevel": round(entry.get("FuelMain")),
            }
        case "RefuelAll":
            current_state = get_state_all()
            if "FuelLevel" in current_state:
                return {"FuelLevel": current_state["FuelCapacity"]}
            return {}

        case "RepairAll":
            return {"HullHealth": 1}
        case "HullDamage":
            return {"HullHealth": entry.get("Health")}

        case "Docked":
            return {"Docked": True, "onStation": entry.get("StationName")}
        case "Undocked":
            return {"Docked": False, "onStation": ""}
        case "Touchdown":
            return {
                "Docked": True,
                "onStation": entry.get("OnStation"),
                "onPlanet": entry.get("onPlanet"),
            }
        case "Liftoff":
            return {
                "Docked": False,
                "onStation": False,
            }
        case "SupercruiseDestinationDrop":
            return {"Current Threatlevel": entry.get("Threat")}
        case _:
            return {}


# Get all the information from the ship-state.json file
def get_state_all():
    state_file_path = "ship-state.json"

    # Load existing data or create empty dict
    try:
        with open(state_file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Calculate FuelLevel percentage if both FuelLevel and FuelCapacity exist
    if "FuelLevel" in data and "FuelCapacity" in data and data["FuelCapacity"] > 0:
        new_fuellevel = round((data["FuelLevel"] / data["FuelCapacity"]) * 100)
        data["FuelLevel"] = f"{new_fuellevel}%"

    return data


def get_navigation_status():
    navroute_file_path = os.path.join(JOURNAL_DIRECTORY, "NavRoute.json")
    try:
        with open(navroute_file_path, "r", encoding="utf-8") as f:
            navroute_data = json.load(f)

            if "Route" in navroute_data:
                filtered_route = []
                for system in navroute_data["Route"]:
                    filtered_system = {
                        "StarSystem": system["StarSystem"],
                        "StarClass": system["StarClass"],
                    }
                    filtered_route.append(filtered_system)
                return {"Route": filtered_route}
            return {}

    except FileNotFoundError:
        log("error", f"NavRoute.json not found at {navroute_file_path}")
        return json.dumps({"tool_response": "Error: NavRoute.json not found"})
    except json.JSONDecodeError:
        log("error", f"Error decoding NavRoute.json at {navroute_file_path}")
        return json.dumps({"tool_response": "Error: Could not decode NavRoute.json"})
    except Exception as e:
        log("error", f"An unexpected error occurred in get_navroute: {e}")
        return json.dumps(
            {"tool_response": f"Error: An unexpected error occurred: {e}"}
        )


def get_cargo_status():
    try:
        cargo_path = os.path.join(JOURNAL_DIRECTORY, "Cargo.json")
        with open(cargo_path, "r") as file:
            cargo = json.load(file)
            cargo_inventory = cargo.get("Inventory")
    except (FileNotFoundError, json.JSONDecodeError):
        cargo_inventory = "[]"

    return cargo_inventory

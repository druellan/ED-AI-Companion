# I want the AI to inform be about the cargo, the fuel and possible contraband I have in store.

import json
import os
from config import (
    JOURNAL_DIRECTORY,
)


def parse(entry):
    print("Reading the cargo file.")
    cargo_file = os.path.join(JOURNAL_DIRECTORY, "Cargo.json")

    try:
        with open(cargo_file, "r") as file:
            cargo_content = json.load(file)
    except FileNotFoundError:
        print("Market file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []

    return cargo_content


CONTEXT = """
We undocked from a space port.
Just mention the cargo, don't mention the total or the units for each cargo.
Notify me if I have less than 10 limpets, ignore otherwise.
Check for cargo flagged as stolen or ilegal, ignore otherwise.
Notify me about the fuel levels.
"""

## { "timestamp":"2024-08-04T02:08:13Z", "event":"Undocked", "StationName":"Coelho Station", "StationType":"Orbis", "MarketID":128932533, "Taxi":false, "Multicrew":false }

## { "timestamp":"2025-02-08T16:16:17Z", "event":"Cargo", "Vessel":"Ship", "Count":352, "Inventory":[
## { "Name":"fish", "Count":65, "Stolen":0 },
## { "Name":"silver", "Count":255, "Stolen":0 },
## { "Name":"drones", "Name_Localised":"Limpet", "Count":32, "Stolen":0 }
## ] }

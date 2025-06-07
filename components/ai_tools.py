# components/ai_tools.py
import inspect
import json
import sys

import requests

from components.memory_manager import get_recent_event_memory

from config import EDSM_API, JOURNAL_DIRECTORY
from components.utils import log, json_to_compact_text
from components.tts_manager import send_text_to_voice
import os


async def get_init_data():
    """Retrieves information needed for ALL events."""

    await send_text_to_voice("I'm using tools now, Commander.")

    return ""


def get_navroute():
    """Retrieves the current navigation route from NavRoute.json and returns it in compact text format."""
    log("info", "Tool: get_navroute called")
    navroute_file_path = os.path.join(JOURNAL_DIRECTORY, "NavRoute.json")
    try:
        with open(navroute_file_path, "r", encoding="utf-8") as f:
            navroute_data = json.load(f)

        compact_navroute_data = json_to_compact_text(navroute_data)
        return json.dumps({"tool_response": compact_navroute_data})
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


def get_market():
    """Retrieves a list of products from the local market, including prices and profit margins."""
    log("info", "Tool: get_market called")
    market_file_path = os.path.join(JOURNAL_DIRECTORY, "Market.json")
    try:
        with open(market_file_path, "r", encoding="utf-8") as f:
            market_data = json.load(f)

        compact_market_data = json_to_compact_text(market_data)
        return json.dumps({"tool_response": compact_market_data})
    except FileNotFoundError:
        log("error", f"Market.json not found at {market_file_path}")
        return json.dumps({"tool_response": "Error: Market.json not found"})
    except json.JSONDecodeError:
        log("error", f"Error decoding Market.json at {market_file_path}")
        return json.dumps({"tool_response": "Error: Could not decode Market.json"})
    except Exception as e:
        log("error", f"An unexpected error occurred in get_market: {e}")
        return json.dumps(
            {"tool_response": f"Error: An unexpected error occurred: {e}"}
        )


def get_events(event_name=None):
    """Retrieves the last 100 events from the ship journal. If event_name is specified, it filters the events by that name."""
    log("info", f"Tool: get_memory called with event_name='{event_name}'")

    # Retrieve the last 100 events by default
    recent_events = get_recent_event_memory(count=100)

    if event_name:
        filtered_events = [
            event for event in recent_events if event.get("event") == event_name
        ]
        return json.dumps(filtered_events)
    else:
        return json.dumps(recent_events)


def get_system(system_name):
    """Gets EDSM system info for the given system name."""
    # log("debug", f"Tool: get_system called with system_name={system_name}")

    if not system_name:
        log("error", "System name is required for get_system.")
        return

    params = {
        "systemName": system_name,
        "showPermit": 1,
        "showInformation": 1,
    }
    try:
        response = requests.get(EDSM_API + "/api-v1/system", params=params)
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching data for {system_name}: {e}")

    return


def get_system_bodies(system_name):
    """Gets EDSM body info for the given system name."""
    # log("debug", f"Tool: get_system_bodies called with system_name={system_name}")

    if not system_name:
        log("error", "System name is required for get_system_bodies.")
        return

    params = {"systemName": system_name}
    try:
        response = requests.get(EDSM_API + "/api-system-v1/bodies", params=params)
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching bodies data for {system_name}: {e}")

    return


def get_system_scan(system_name):
    """Gets estimated value and valuable bodies in a system from EDSM."""
    if not system_name:
        log("error", "System name is required for get_system_scan.")
        return

    params = {"systemName": system_name}
    try:
        response = requests.get(
            EDSM_API + "/api-system-v1/estimated-value", params=params
        )
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching scan data for {system_name}: {e}")

    return


def get_system_stations(system_name):
    """Gets information about stations in a system from EDSM."""

    if not system_name:
        log("error", "System name is required for get_system_stations.")
        return

    params = {"systemName": system_name}
    try:
        response = requests.get(EDSM_API + "/api-system-v1/stations", params=params)
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching station data for {system_name}: {e}")

    return


def get_station_market(system_name):
    """Gets information about the market in a system from EDSM."""
    # log("debug", f"Tool: get_station_market called with systemName={system_name}")

    if not system_name:
        log("error", "The market ID is mandatory.")
        return

    params = {"systemName": system_name}
    try:
        response = requests.get(
            EDSM_API + "/api-system-v1/stations/market", params=params
        )
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching market data for {system_name}: {e}")

    return


def get_system_factions(system_name):
    """Gets information about the factions in a system from EDSM."""
    # log("debug", f"Tool: get_system_factions called with system_name={system_name}")

    if not system_name:
        log("error", "System name is required for get_system_factions.")
        return

    params = {"systemName": system_name}
    try:
        response = requests.get(EDSM_API + "/api-system-v1/factions", params=params)
        log("debug", "response {response}")
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        log("error", f"Error fetching factions data for {system_name}: {e}")

    return


def _get_available_tools():
    tools_list = []
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if (
            inspect.isfunction(obj)
            and not inspect.isbuiltin(obj)
            and not name.startswith("_")
            and obj.__doc__
        ):
            description = obj.__doc__.strip()
            signature = inspect.signature(obj)
            params = ", ".join([param.name for param in signature.parameters.values()])
            tools_list.append(f"{name}({params}) - {description}")

    return "\n".join(tools_list)


# Example usage (for testing within ai_tools.py)
# if __name__ == "__main__":
#     print("--- Available Tools ---")
#     print(_get_available_tools())
#     print("\n--- Example Tool Calls ---")
#     # print(get_memory())
#     # print(get_system("Sol"))
#     # print(get_system_stations("Sol"))

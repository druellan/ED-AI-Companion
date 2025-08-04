# We use EDSM API to gather information about the target system, so the AI can warn us if the system has a special condition, like a permit lock.

import requests

from config import EDSM_API


def parse(entry):
    # Let's fetch information about the target star
    system_name = entry.get("Name")

    params = {
        "systemName": system_name,
        "showPermit": 1,
        "showInformation": 1,
    }

    try:
        response = requests.get(EDSM_API + "/api-v1/system", params=params)
        data = response.json()

        extracted_data = {
            "population": data.get("information", {}).get("population"),
            "reserve": data.get("information", {}).get("reserve"),
            # "government": data.get("information", {}).get("government"),
            "requirePermit": data.get("requirePermit"),
        }

        return {"event": entry, "system_information": extracted_data}

    except Exception as e:
        print(f"Error fetching EDSM data: {e}")

    return entry


DESCRIPTION = "We are targeting our next FSD destination."
CONTEXT = """
   Ignore population numbers.
   Check previous events to see if we are in the middle of a route, if true: skip responses unless you see dangers and remarkable information"""

## Example of the event ##
## { "timestamp":"2025-02-02T21:16:52Z", "event":"FSDTarget", "Name":"LP 470-65", "SystemAddress":672028370361, "StarClass":"M", "RemainingJumpsInRoute":1 }

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


CONTEXT = """
    We are targeting our next FSD destination.
    If RemainingJumpsInRoute > 1 the target is a transition system to our destination, otherwise, it is the final destination.
"""

## Example of the event ##
## { "timestamp":"2025-02-02T21:16:52Z", "event":"FSDTarget", "Name":"LP 470-65", "SystemAddress":672028370361, "StarClass":"M", "RemainingJumpsInRoute":1 }

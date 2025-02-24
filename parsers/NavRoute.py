# We pull the NavRoute.json information, since the event is just a report of the current route.

import json
import os
from config import (
    JOURNAL_DIRECTORY,
)


def parse(entry):
    print("Reading the NavRoute file.")
    navroute = os.path.join(JOURNAL_DIRECTORY, "NavRoute.json")

    try:
        with open(navroute, "r") as file:
            navroute_content = json.load(file)
    except FileNotFoundError:
        print("NavRoute file not found.")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return []

    #    if "Route" in navroute_content:
    #        if len(navroute_content["Route"]) > 0:
    #            navroute_content["Route"] = navroute_content["Route"][1:]
    return navroute_content


CONTEXT = """
    We just traced a new navigation route.
    The first entry is the current system. Ignore it.
    The last entry is the destination.
    Tell me how many jumps I need to reach the destination.
    Confirm if the route seems safe.
"""

## Example of the event ##
## { "timestamp":"2025-02-07T01:01:15Z", "event":"NavRoute", "Route":[
## { "StarSystem":"Morten-Marte", "SystemAddress":2008132129498, "StarPos":[81.87500,36.87500,47.53125], "StarClass":"K" },
## { "StarSystem":"Crucis Sector FR-V b2-2", "SystemAddress":5070074881465, "StarPos":[83.78125,41.06250,42.71875], "StarClass":"M" }
## ] }

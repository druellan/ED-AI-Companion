# tools/journal_tools.py

import os
import json

from config import JOURNAL_DIRECTORY
from components.memory_manager import get_recent_event_memory
from components.utils import log, json_to_compact_text


class JournalTools:
    """
    A class to interact with the local journal files and event memory for Elite Dangerous.
    """

    # Disabled for now
    def _get_current_market(self):
        """
        Retrieves a list of products from the local market, including prices and profit margins.
        """
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

    def get_events(self, event_name=None):
        """
        Retrieves the last 100 events from the ship journal. If event_name is specified, it filters the events by that name.
        """
        log("info", f"Tool: get_events called with event_name='{event_name}'")

        # Retrieve the last 100 events by default
        recent_events = get_recent_event_memory(count=100)

        if event_name:
            filtered_events = [
                event for event in recent_events if event.get("event") == event_name
            ]
            return json.dumps(filtered_events)
        else:
            return json.dumps(recent_events)

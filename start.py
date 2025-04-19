# ED:AI Companion by druellan

import os
import json
import time

# import requests

from components.ai_interface import send_event_to_api, check_openrouter_rate_limits
from components.tts_manager import send_text_to_voice

from components.state_manager import update_state, init_state
from components.memory_manager import add_memory, init_memory
from components.mission_manager import update_missions, init_missions

from components.utils import (
    log,
    get_latest_journal_file,
    cleanup_event,
    json_to_compact_text,
    merge_true_events,
)

from parsers import EVENT_PARSERS

# Config.py
from config import (
    JOURNAL_DIRECTORY,
    LLM_MODEL_NAME,
    TTS_WINDOWS_VOICE,
    TTS_EDGE_VOICE,
    TTS_TYPE,
    STARTUP_EVENTS,
    COMBAT_EVENTS,
    TRAVEL_EVENTS,
    EXPLORATION_EVENTS,
    TRADE_EVENTS,
    POWERPLAY_EVENTS,
    SQUADRON_EVENTS,
    STATION_SERVICES_EVENTS,
    FLEET_CARRIER_EVENTS,
    ODYSSEY_EVENTS,
    OTHER_EVENTS,
    STATUS_EVENTS,
    DEBUG_EVENT_DUMP,
    DEBUG_PARSER_PROMPT,
    DEBUG_AI_RESPONSE,
)

VERSION = "0.1.5"


# Monitor the journal files for new events
def monitor_journal():
    current_journal = get_latest_journal_file(JOURNAL_DIRECTORY)
    if not current_journal:
        log("system", "No journal files found.")
        return

    log("system", f"Monitoring journal file: {current_journal}")

    with open(current_journal, "r", encoding="utf-8") as file:
        file.seek(0, os.SEEK_END)
        while True:
            # Check for a new journal file
            new_journal = get_latest_journal_file(JOURNAL_DIRECTORY)
            if new_journal != current_journal:
                log("system", f"Switching to new journal file: {new_journal}")
                current_journal = new_journal
                file.close()
                file = open(current_journal, "r", encoding="utf-8")

            new_lines = file.readlines()
            file.seek(0, os.SEEK_END)

            if new_lines:
                process_journal_entries(new_lines)
            else:
                time.sleep(1)


def process_journal_entries(lines):
    entries = []
    for line in lines:
        try:
            entry = json.loads(line)
            entries.append(entry)
        except json.JSONDecodeError:
            continue

    # Group consecutive entries by event type
    current_event_type = None
    current_batch = []

    for entry in entries:
        event_type = entry.get("event")

        # Skip filtered events
        if event_type in ["Fileheader", "Shutdown", "Music"]:
            continue

        if DEBUG_EVENT_DUMP:
            log("debug", entry)

        update_state(entry)
        add_memory(entry)
        update_missions(entry)

        # If this is a new event type, process the previous batch
        if event_type != current_event_type:
            if current_batch:
                process_event_batch(current_batch)
            current_batch = [entry]
            current_event_type = event_type
        else:
            current_batch.append(entry)

    # Process the final batch
    if current_batch:
        process_event_batch(current_batch)


def process_event_batch(batch):
    if not batch:
        return

    event_type = batch[0]["event"]
    log("event", f"Processing {len(batch)} {event_type} events")

    # Clean up each entry in the batch
    clean_batch = [
        cleanup_event(entry, ["timestamp", "build", "SystemAddress"]) for entry in batch
    ]

    # Build concatenated string of events
    entry_strings = []
    for entry in clean_batch:
        if event_type in EVENT_PARSERS:
            parsed_entry = EVENT_PARSERS[event_type]["function"](entry)
            if parsed_entry is not False:
                entry_strings.append(json_to_compact_text(parsed_entry))
        else:
            entry_strings.append(json_to_compact_text(entry))

    if not entry_strings:
        log("event", "Parser ignored all events")
        return False

    # Add context if available
    if event_type in EVENT_PARSERS and "context" in EVENT_PARSERS[event_type]:
        final_string = (
            EVENT_PARSERS[event_type]["context"]
            + " Events: "
            + "; ".join(entry_strings)
        )
    else:
        final_string = "Events: " + "; ".join(entry_strings)

    if DEBUG_PARSER_PROMPT:
        log("debug", final_string)

    # If the event is in the list, send it to the AI
    if event_type in EVENT_LIST:
        log("event", f"Reacting to {event_type} events")
        response_text = send_event_to_api(final_string)
        if response_text:
            if DEBUG_AI_RESPONSE:
                if "NULL" in response_text:
                    log("AI", "(AI dropped the response).")
                    return False
                log("AI", f"{response_text}")
            speak_response(response_text)
    else:
        log("event", f"Ignoring {event_type} events")


# Send the response to the TTS engine, based on the config file
def speak_response(response):
    if response is False:
        return

    send_text_to_voice(response)


if __name__ == "__main__":
    EVENT_LIST = merge_true_events(
        STARTUP_EVENTS,
        COMBAT_EVENTS,
        TRAVEL_EVENTS,
        EXPLORATION_EVENTS,
        TRADE_EVENTS,
        POWERPLAY_EVENTS,
        SQUADRON_EVENTS,
        STATION_SERVICES_EVENTS,
        FLEET_CARRIER_EVENTS,
        ODYSSEY_EVENTS,
        OTHER_EVENTS,
        STATUS_EVENTS,
    )
    os.system("")  # enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607

    log("info", f"Welcome to ED:AI Companion V{VERSION}, Commander")
    log("info", f"Main model to use: {LLM_MODEL_NAME}")
    check_openrouter_rate_limits()

    if TTS_TYPE == "WINDOWS":
        log("info", f"Text-to-Speech: type {TTS_TYPE} voice {TTS_WINDOWS_VOICE}")
    else:
        log("info", f"Text-to-Speech: type {TTS_TYPE} voice {TTS_EDGE_VOICE}")

    init_state()
    init_memory()
    init_missions()

    log("info", "All systems ready!")
    speak_response("All systems ready.")

    monitor_journal()

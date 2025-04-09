# ED:AI Companion by druellan

import os
import json
import time

# import requests

from components.ai_interface import send_event_to_api
from components.tts_manager import send_text_to_voice

from components.state_manager import update_state, init_state
from components.memory_manager import add_memory, init_memory
from components.mission_manager import update_missions, init_missions

from components.utils import (
    output,
    get_latest_journal_file,
    cleanup_event,
    json_to_compact_text,
    merge_true_events,
)
from components.constants import COLOR

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
        output("No journal files found.", COLOR.RED)
        return

    output(f"Monitoring journal file: {current_journal}")

    with open(current_journal, "r", encoding="utf-8") as file:
        file.seek(0, os.SEEK_END)
        while True:
            # Check for a new journal file
            new_journal = get_latest_journal_file(JOURNAL_DIRECTORY)
            if new_journal != current_journal:
                output(f"Switching to new journal file: {new_journal}")
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
            output(entry)

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
    output(f"Processing {len(batch)} {event_type} events", COLOR.BRIGHT_CYAN)

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
        output("Parser ignored all events", COLOR.BRIGHT_CYAN)
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
        output(final_string, COLOR.CYAN)

    # If the event is in the list, send it to the AI
    if event_type in EVENT_LIST:
        output(f"Reacting {event_type} events", COLOR.BRIGHT_CYAN)
        response_text = send_event_to_api(final_string)
        if response_text:
            if DEBUG_AI_RESPONSE:
                if response_text.startswith("NULL"):
                    output("AI dropped the response.", COLOR.CYAN)
                    return False
                output(f"AI response: {response_text}", COLOR.CYAN)
            speak_response(response_text)
    else:
        output(f"Ignoring {event_type} events", COLOR.BRIGHT_CYAN)


# Operate on the received event, check if we have specific parsers for it
def generate_response(entry):
    event = entry.get("event", False)
    # Hard filter events
    hardFilered = ["Fileheader", "Shutdown", "Music"]
    output(f"Received event: {event}", COLOR.BRIGHT_CYAN)

    if not event:
        return

    if event in hardFilered:
        return

    # Check if the event has a parser
    if event in EVENT_PARSERS:
        parsed_entry = EVENT_PARSERS[event]["function"](entry)
        output(f"Parsed event: {event}", COLOR.BRIGHT_CYAN)
    else:
        parsed_entry = entry

    if parsed_entry is False:
        output("Parser ignored the event", COLOR.BRIGHT_CYAN)
        return False

    if event in EVENT_PARSERS and "context" in EVENT_PARSERS[event]:
        entry_string = (
            EVENT_PARSERS[event]["context"]
            + "Data: "
            + json_to_compact_text(parsed_entry)
        )
    else:
        entry_string = json_to_compact_text(parsed_entry)

    if DEBUG_PARSER_PROMPT:
        output(entry_string, COLOR.CYAN)

    # If the event is in the list, send it to the AI
    if event in EVENT_LIST:
        output(f"Reacting to event: {event}", COLOR.BRIGHT_CYAN)
        response_text = send_event_to_api(entry_string)

    else:
        output(f"Ignoring the event: {event}", COLOR.BRIGHT_CYAN)
        return False

    # Output the AI response
    if response_text:
        if DEBUG_AI_RESPONSE:
            if response_text.startswith("NULL"):
                output("AI dropped the response.", COLOR.CYAN)
                return False
            output(f"AI response: {response_text}", COLOR.CYAN)
        return response_text


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

    output(f"\nWelcome to ED Companion V{VERSION}, Commander", COLOR.BRIGHT_WHITE)
    output(f"Main model to use: {LLM_MODEL_NAME}")
    if TTS_TYPE == "WINDOWS":
        output(f"Text-to-Speech: type {TTS_TYPE} voice {TTS_WINDOWS_VOICE}")
    else:
        output(f"Text-to-Speech: type {TTS_TYPE} voice {TTS_EDGE_VOICE}")

    init_state()
    init_memory()
    init_missions()

    output("All systems ready!", COLOR.BRIGHT_GREEN)
    speak_response("All systems ready.")

    monitor_journal()

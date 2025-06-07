# ED:AI Companion by druellan

import asyncio
import json
import os

from components.ai_interface import get_openrouter_rate_limits, send_event_to_api
from components.memory_manager import (
    add_event_memory,
    init_event_memory,
    init_response_memory,
)
from components.mission_manager import init_missions, update_missions
from components.state_manager import init_state, update_state
from components.tts_manager import send_text_to_voice
from components.utils import (
    cleanup_event,
    get_latest_journal_file,
    json_to_compact_text,
    log,
    merge_true_events,
)

# Config.py
from config import (
    COMBAT_EVENTS,
    DEBUG_EVENT_DUMP,
    DEBUG_PARSER_PROMPT,
    EXPLORATION_EVENTS,
    FLEET_CARRIER_EVENTS,
    JOURNAL_DIRECTORY,
    JOURNAL_TIME_INTERVAL,
    LLM_MODEL_NAME,
    ODYSSEY_EVENTS,
    OTHER_EVENTS,
    POWERPLAY_EVENTS,
    SQUADRON_EVENTS,
    STARTUP_EVENTS,
    STATION_SERVICES_EVENTS,
    STATUS_EVENTS,
    TRADE_EVENTS,
    TRAVEL_EVENTS,
    TTS_EDGE_VOICE,
    TTS_TYPE,
    TTS_WINDOWS_VOICE,
)
from parsers import EVENT_PARSERS

VERSION = "0.2.0"


# Monitor the journal files for new events
async def _monitor_journal():
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
                await _process_journal_entries(new_lines)
            else:
                await asyncio.sleep(JOURNAL_TIME_INTERVAL)


async def _process_journal_entries(lines):
    entries = []
    for line in lines:
        try:
            entry = json.loads(line)
            entries.append(entry)
        except json.JSONDecodeError:
            continue

    # Process events in batches of 10 (regardless of type)
    current_batch = []
    max_batch_size = 20

    for entry in entries:
        event_type = entry.get("event")

        # Skip filtered events
        if event_type in ["Fileheader", "Shutdown", "Music", "ShipLocker"]:
            continue

        if DEBUG_EVENT_DUMP:
            log("debug", entry)

        update_state(entry)
        add_event_memory(entry)
        update_missions(entry)

        # Add entry to current batch
        current_batch.append(entry)

        # Process batch when it reaches max size
        if len(current_batch) >= max_batch_size:
            await _process_event_batch(current_batch)
            current_batch = []

    # Process the final batch if there are any remaining events
    if current_batch:
        await _process_event_batch(current_batch)


async def _process_event_batch(batch):
    if not batch:
        return

    log("event", f"Processing batch of {len(batch)} events")

    # Clean up each entry in the batch
    clean_batch = [
        cleanup_event(entry, ["timestamp", "build", "SystemAddress"]) for entry in batch
    ]

    # Collect contexts and events separately
    contexts = {}
    event_strings = []
    events_to_process = False

    # First pass: collect all contexts by event type
    for entry in clean_batch:
        event_type = entry.get("event")

        # Only process events that are in our EVENT_LIST
        if event_type in EVENT_LIST and event_type in EVENT_PARSERS:
            context = EVENT_PARSERS[event_type].get("context", "")
            if context and event_type not in contexts:
                contexts[event_type] = context

    # Second pass: process all events
    for entry in clean_batch:
        event_type = entry.get("event")

        # Only process events that are in our EVENT_LIST
        if event_type in EVENT_LIST:
            events_to_process = True
            if event_type in EVENT_PARSERS:
                parsed_entry = EVENT_PARSERS[event_type]["function"](entry)
                if parsed_entry is not False:
                    event_strings.append(
                        f"Event {event_type}: {json_to_compact_text(parsed_entry)}"
                    )
            else:
                event_strings.append(
                    f"Event {event_type}: {json_to_compact_text(entry)}"
                )

    if not event_strings:
        if events_to_process:
            log("event", "Parser ignored all events")
        else:
            log("event", "No events in batch need processing")
        return False

    # Build the final string with contexts first, then events
    final_parts = []

    # Add all unique contexts first
    for event_type, context in contexts.items():
        final_parts.append(f"Context for {event_type}: {context}")

    # Add all event data
    final_parts.extend(event_strings)

    # Join everything with newlines
    final_string = "\n".join(final_parts)

    if DEBUG_PARSER_PROMPT:
        log("debug", final_string)

    # Send mixed events to the AI if we have any to process
    log(
        "event",
        f"Reacting to an event batch with {len(event_strings)} processable events ({len(contexts)} unique contexts)",
    )
    response_text = send_event_to_api(final_string)

    if response_text:
        if "NULL" in response_text:
            log("AI", "(AI dropped the response).")
            return

        log("AI", f"{response_text}")
        await _speak_response(response_text)


# Send the response to the TTS engine, based on the config file
async def _speak_response(response):
    if response is False:
        return

    await send_text_to_voice(response)


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
    get_openrouter_rate_limits()

    if TTS_TYPE == "WINDOWS":
        log("info", f"Text-to-Speech: type {TTS_TYPE} voice {TTS_WINDOWS_VOICE}")
    else:
        log("info", f"Text-to-Speech: type {TTS_TYPE} voice {TTS_EDGE_VOICE}")

    init_state()
    init_event_memory()
    init_response_memory()
    init_missions()

    log("info", "All systems ready!")
    asyncio.run(_speak_response("All systems ready."))

    asyncio.run(_monitor_journal())

# ED:AI Companion by druellan

import asyncio  # Import asyncio for running async functions
import json
import os
import re  # Import the regex module
import sys  # Import the sys module
import time

from components import ai_tools  # Import the ai_tools module
from components.ai_interface import check_openrouter_rate_limits, send_event_to_api
from components.memory_manager import add_memory, init_memory
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
    DEBUG_AI_RESPONSE,
    DEBUG_EVENT_DUMP,
    DEBUG_PARSER_PROMPT,
    EXPLORATION_EVENTS,
    FLEET_CARRIER_EVENTS,
    JOURNAL_DIRECTORY,
    LLM_MODEL_NAME,
    LLM_USE_TOOLS,
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

VERSION = "0.1.5"


# Monitor the journal files for new events
async def monitor_journal():
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
                await process_journal_entries(new_lines)
            else:
                time.sleep(1)


async def process_journal_entries(lines):
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
                await process_event_batch(current_batch)
            current_batch = [entry]
            current_event_type = event_type
        else:
            current_batch.append(entry)

    # Process the final batch
    if current_batch:
        await process_event_batch(current_batch)


async def process_event_batch(batch):
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
            # Process tool calls first
            if LLM_USE_TOOLS:
                tool_output = process_tools(response_text, final_string)
                if tool_output is not None:
                    response_text = tool_output

            # If no tool call was detected, proceed with speaking the response
            if DEBUG_AI_RESPONSE:
                if "NULL" in response_text:
                    log("AI", "(AI dropped the response).")
                    return
                log("AI", f"{response_text}")
            await speak_response(response_text)
    else:
        log("event", f"Ignoring {event_type} events")


# Send the response to the TTS engine, based on the config file
async def speak_response(response):
    if response is False:
        return

    await send_text_to_voice(response)


# Process the AI's response to detect and execute tool calls
def process_tools(response_text, event_string):
    """
    Inspects the AI response for tool calls and executes them.
    Expected format: function_name('argument') or function_name()
    """
    tool_output = None
    # Regex to find function calls like function_name() or function_name('...')
    # It captures the function name and the content within single quotes (if any)
    tool_call_pattern = re.compile(r"^\s*(\w+)\s*\(\s*(?:'(.*?)')?\s*\)\s*$")

    for line in response_text.splitlines():
        match = tool_call_pattern.match(line)
        if match:
            tool_name = match.group(1)
            # The argument is in group 2, which can be None if no argument was provided
            tool_arg = match.group(2)

            log("info", f"Detected tool call: {tool_name} with argument: {tool_arg}")

            tool_function = getattr(ai_tools, tool_name, None)

            if tool_function and callable(tool_function):
                try:
                    if tool_arg is not None:
                        tool_output = tool_function(tool_arg)
                    else:
                        tool_output = tool_function()

                    # log("AI", f"Tool '{tool_name}' executed. Output: {tool_output}")
                    # For now, we just return the first tool output found.
                    # Future steps might involve processing multiple tool calls
                    # or sending the output back to the AI.

                    # let's recursively call the AI again, but this time we return the function response
                    formatted_tool_output = json_to_compact_text(
                        json.dumps(tool_output)
                    )
                    response_to_ai = f"""
{event_string}

# This was your response
{response_text} 

You invoked a function, this is the result:
{formatted_tool_output}
                    """
                    # log("debug", response_to_ai)
                    final_response = send_event_to_api(response_to_ai)
                    return final_response

                except Exception as e:
                    log("error", f"Error executing tool '{tool_name}': {e}")
                    continue
            else:
                log("error", f"Tool function '{tool_name}' not found or not callable.")
                continue
        else:
            # Log lines that are not tool calls if needed for debugging
            # log("debug", f"Line did not match tool pattern: {line}")
            pass

    return None


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
    asyncio.run(speak_response("All systems ready."))

    asyncio.run(monitor_journal())

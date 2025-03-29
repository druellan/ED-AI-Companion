# ED:AI Companion by druellan
# Version: 0.1.1

import sys
import os
import time
import json
from pprint import pprint

# import requests
import asyncio
from collections import deque
# import io

import pyttsx3
import edge_tts
from openai import OpenAI

from pygame import mixer
from pedalboard import Pedalboard, Reverb, Chorus
import soundfile as sf

# Config.py
from config import (
    JOURNAL_DIRECTORY,
    SYSTEM_PROMPT,
    USER_PROMPT,
    LLM_ENDPOINT,
    LLM_API_KEY,
    LLM_MODEL_NAME,
    LLM_MODEL_NAMES,
    TTS_WINDOWS_VOICE,
    TTS_WINDOWS_RATE,
    TTS_WINDOWS_VOLUME,
    TTS_WINDOWS_LIST,
    TTS_EDGE_VOICE,
    TTS_EDGE_RATE,
    TTS_EDGE_VOLUME,
    TTS_EDGE_PITCH,
    TTS_TYPE,
    TTS_EFFECTS,
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
    MEMORY_EVENTS,
    DEBUG_EVENT_DUMP,
    DEBUG_PARSER_PROMPT,
    DEBUG_AI_RESPONSE,
    DEBUG_STATE_UPDATE,
)
from parsers import EVENT_PARSERS

VERSION = "0.1.1"


class COLOR:
    # Regular colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Bright/Bold colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_PURPLE = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # Styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKE = "\033[9m"

    # Reset
    END = "\033[0m"
    RESET = "\033[0m"  # Alternative name for END


# Memory
event_memory = deque(maxlen=50)
missions_memory = deque(maxlen=50)

# from tempfile import NamedTemporaryFile


# Detect the latest journal file
def get_latest_journal_file(directory):
    files = [
        f
        for f in os.listdir(directory)
        if f.startswith("Journal") and f.endswith(".log")
    ]
    if not files:
        return None

    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
    return os.path.join(directory, latest_file)


# Send event data to the AI API
def send_event_to_api(event_data):
    client = OpenAI(
        base_url=LLM_ENDPOINT,
        api_key=LLM_API_KEY,
        default_headers={
            "X-Title": "ED:AI Companion",
            "HTTP-Referer": "ED:AI Companion",
        },
        timeout=20.0,
    )

    # Start the client and the model
    completion = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        extra_body={
            "models": LLM_MODEL_NAMES,
        },
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": get_user_prompt(event_data)},
        ],
        temperature=0.2,
    )

    # Send the messages variable to a file
    with open("last_prompt.json", "w") as file:
        last_prompt = get_system_prompt() + "\n\n" + get_user_prompt(event_data)
        file.write(last_prompt)

    # Check if completion has an error
    if hasattr(completion, "error") and completion.error:
        error_code = completion.error.get("code", 500)
        error_message = completion.error.get("message", "Unknown error")

        # output("Response from AI API:")
        # error_metadata = completion.error.get("metadata", "Unknown error")
        # output(error_metadata)
        return error_message + " code " + str(error_code)

    # Check if completion has choices
    if not completion.choices:
        output("No message from API, trying next LLM", COLOR.YELLOW)
        return error_message

    return completion.choices[0].message.content.strip()


# Text-to-Speech functions, using Windows TTS
async def send_local_text_to_voice(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")

    # List available voices
    if "TTS_WINDOWS_LIST" in globals() and TTS_WINDOWS_LIST:
        for index, voice in enumerate(voices):
            if voice.name == TTS_WINDOWS_VOICE:
                output(f"Voice {index}: {voice.name} < selected", COLOR.BRIGHT_WHITE)
            else:
                output(f"Voice {index}: {voice.name}")

    for index, voice in enumerate(voices):
        if voice.name == TTS_WINDOWS_VOICE:
            break
    else:
        index = None

    if index is not None:
        try:
            engine.setProperty("voice", voices[index].id)
            engine.setProperty("rate", TTS_WINDOWS_RATE)
            engine.setProperty("volume", TTS_WINDOWS_VOLUME)

            # Save to temporary file instead of speaking directly
            temp_file = "./tts-temp.mp3"
            engine.save_to_file(text, temp_file)
            engine.runAndWait()

            # Add effects if enabled
            if TTS_EFFECTS:
                add_audio_effects(temp_file)

            # Play with pygame mixer
            mixer.init()
            mixer.music.load(temp_file)
            mixer.music.play()

            while mixer.music.get_busy():
                time.sleep(0.1)

            mixer.music.unload()
            mixer.quit()

            # Cleanup
            os.remove(temp_file)

        except Exception as e:
            output(f"Windows TTS error: {str(e)}", COLOR.RED)
    else:
        output("Specified TTS voice not found.", COLOR.RED)


# Text-to-Speech functions, using Edge TTS
async def send_edge_text_to_voice(text):
    try:
        voice = TTS_EDGE_VOICE
        rate = TTS_EDGE_RATE
        volume = TTS_EDGE_VOLUME
        pitch = TTS_EDGE_PITCH
        communicate = edge_tts.Communicate(
            text, voice, rate=rate, volume=volume, pitch=pitch
        )

        temp_file = "./tts-temp.mp3"

        await communicate.save(temp_file)

        # Add effects to the audio file
        if TTS_EFFECTS:
            add_audio_effects(temp_file)

        # Play with pygame mixer
        mixer.init()
        mixer.music.load(temp_file)
        mixer.music.play()

        while mixer.music.get_busy():
            time.sleep(0.1)

        mixer.music.unload()
        mixer.quit()

        # Cleanup
        os.remove(temp_file)

    except Exception as e:
        output(f"Edge TTS error: {str(e)}", COLOR.RED)
        # Optionally fall back to Windows TTS
        if TTS_TYPE != "WINDOWS":
            output("Falling back to Windows TTS", COLOR.YELLOW)
            await send_local_text_to_voice(text)


def add_audio_effects(audio):
    # Load the audio file
    audio, sample_rate = sf.read("./tts-temp.mp3")

    # Create an effects board
    board = Pedalboard(
        [
            Reverb(room_size=0.1, wet_level=0.1),
            Chorus(rate_hz=2.0, depth=0.25),  # Add chorus effect
        ]
    )

    # Apply effects
    effected = board(audio, sample_rate)

    # Save the processed audio
    sf.write("./tts-temp.mp3", effected, sample_rate)


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

    if TTS_TYPE == "WINDOWS":
        asyncio.run(send_local_text_to_voice(response))
    else:
        asyncio.run(send_edge_text_to_voice(response))


# Get the main prompt and enrich it with the current status
def get_system_prompt():
    # Replace status placeholder in system prompt
    global_status = get_state_all()
    recent_events = get_recent_memory(20)
    missions = get_missions()

    try:
        cargo_path = os.path.join(JOURNAL_DIRECTORY, "Cargo.json")
        with open(cargo_path, "r") as file:
            cargo = json.load(file)
            cargo_inventory = json_to_compact_text(cargo.get("Inventory"))
    except (FileNotFoundError, json.JSONDecodeError):
        cargo_inventory = "[]"

    system_prompt = (
        SYSTEM_PROMPT.replace("{current_status}", json_to_compact_text(global_status))
        .replace("{recent_events}", json_to_compact_text(recent_events))
        .replace("{current_cargo}", json_to_compact_text(cargo_inventory))
        .replace("{current_missions}", json_to_compact_text(missions))
    )

    return system_prompt


# Get the main prompt and add the context
def get_user_prompt(context):
    user_prompt = USER_PROMPT.replace("{event_new}", str(context))

    return user_prompt


# Keep a list of current missions
def update_missions(entry):
    mission_file_path = "missions_memory.json"

    # Load existing missions into deque if it's empty
    if not missions_memory:
        try:
            with open(mission_file_path, "r") as file:
                missions_data = json.load(file)
                missions_memory.extend(missions_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    # If the event is MissionAccepted, add it to the deque
    if entry.get("event") == "MissionAccepted":
        missions_memory.append(entry)

        # Save the updated deque to file
        with open(mission_file_path, "w") as file:
            json.dump(list(missions_memory), file)

    # If the event is MissionCompleted, remove the corresponding mission
    if entry.get("event") == "MissionCompleted":
        # Find and remove the completed mission
        mission_id = entry.get("MissionID")
        for mission in list(missions_memory):
            if mission.get("MissionID") == mission_id:
                missions_memory.remove(mission)
                break

        # Save the updated deque to file
        with open(mission_file_path, "w") as file:
            json.dump(list(missions_memory), file)


# Modify the get_missions function to use the deque
def get_missions():
    # If the deque is empty, try to load from file
    if not missions_memory:
        try:
            with open("missions_memory.json", "r") as file:
                missions_data = json.load(file)
                missions_memory.extend(missions_data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    return list(missions_memory)


# Add an initialization function for missions
def init_missions():
    try:
        with open("missions_memory.json", "r") as file:
            missions_data = json.load(file)
            missions_memory.extend(missions_data)
    except FileNotFoundError:
        pass


# Get all the information from the ship-state.json file
def get_state_all():
    state_file_path = "ship-state.json"

    # Load existing data or create empty dict
    try:
        with open(state_file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    return data


# Look into the journal for the initial state of the ship
def init_state():
    journal_file_path = get_latest_journal_file(JOURNAL_DIRECTORY)

    if not journal_file_path:
        output("No journal files found.", COLOR.RED)
        return

    with open(journal_file_path, "r") as file:
        for line in file:
            entry = json.loads(line)
            filtered_entry = filter_state_events(entry)
            if filtered_entry:
                update_state(filtered_entry)


# Gather information from the ingame status and save it to the ship-state.json file
def update_state(event):
    status_path = os.path.join(JOURNAL_DIRECTORY, "Status.json")
    try:
        with open(status_path, "r") as file:
            status = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        status = {}

    filtered_status = {
        "LegalState": status.get("LegalState"),
        "Balance": status.get("Balance"),
        "FuelLevel": status.get("Fuel", {}).get("FuelMain"),
        "FuelReservoir": status.get("Fuel", {}).get("FuelReservoir"),
    }

    filtered_event = filter_state_events(event)

    # Merge filtered status with filtered event
    if event:
        filtered_status.update(filtered_event)

    add_states(filtered_status)


# Get any information and save only information related to the ship-state.json file
def add_states(status):
    state_file_path = "ship-state.json"

    if DEBUG_STATE_UPDATE:
        output(f"Updating status: {status}", COLOR.CYAN)

    # Load existing data or create empty dict
    try:
        with open(state_file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Update status while preserving other data
    data.update(status)

    # Write back to file
    with open(state_file_path, "w") as file:
        json.dump(data, file)

    return True


# HELPERS


def filter_state_events(entry):
    filtered = {}

    if entry.get("event") == "LoadGame":
        filtered = {
            "Ship": entry.get("Ship"),
            "ShipName": entry.get("ShipName"),
            "FuelLevel": entry.get("FuelLevel"),
            "FuelCapacity": entry.get("FuelCapacity"),
            "Balance": entry.get("Credits"),
        }
    if entry.get("event") == "Loadout":
        filtered = {
            "HullHealth": entry.get("HullHealth"),
        }

    if entry.get("event") == "Fuel":
        filtered["FuelLevel"] = entry["Fuel"].get("FuelMain")
        filtered["FuelReservoir"] = entry["Fuel"].get("FuelReservoir")

    if entry.get("event") == "ReservoirReplenished":
        filtered["FuelLevel"] = entry.get("FuelMain")
        filtered["FuelReservoir"] = entry.get("FuelReservoir")

    if entry.get("event") == "RepairAll":
        filtered["HullHealth"] = 1
    if entry.get("event") == "HullDamage":
        filtered["HullHealth"] = entry.get("Health")

    if entry.get("event") == "RefuelAll":
        current_state = get_state_all()
        if "FuelMain" in current_state:
            filtered["FuelMain"] = current_state["FuelCapacity"]

    return filtered


def output(string, color=None):
    if color:
        print(f"{color}{string}{COLOR.END}")
    else:
        print(f"{string}")


def cleanup_event(entry, keys_to_remove):
    # Remove the specified keys
    for key in keys_to_remove:
        if key in entry:
            del entry[key]
    return entry


def merge_true_events(*dicts):
    merged_events = []
    for dictionary in dicts:
        for event, status in dictionary.items():
            if status:
                merged_events.append(event)
    return merged_events


def json_to_str(obj):
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def json_to_compact_text(data):
    if isinstance(data, dict):
        parts = [
            f"{k}={json_to_compact_text(v)}" for k, v in data.items() if v is not None
        ]
        return "|".join(parts)
    elif isinstance(data, list):
        return "+".join(json_to_compact_text(item) for item in data if item is not None)
    elif isinstance(data, bool):
        return "1" if data else "0"
    elif data is None:
        return ""
    else:
        return str(data).replace(" ", "_")


def init_memory():
    try:
        with open("event_memory.json", "r") as file:
            event_memory.extend(json.load(file))
    except FileNotFoundError:
        pass


def add_memory(event_data):
    # list of event allowed to be memorized

    if event_data["event"] in MEMORY_EVENTS:
        event_memory.append(event_data)
        with open("event_memory.json", "w") as file:
            json.dump(list(event_memory), file)


def get_recent_memory(count=None):
    if count is None:
        return list(event_memory)

    return list(event_memory)[-count:]


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

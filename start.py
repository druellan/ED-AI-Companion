# ED:AI Companion by druellan
# Version: 0.1.0

import sys
import os
import time
import json
from pprint import pprint

# import requests
import asyncio
# import io

import pyttsx3
import edge_tts
from openai import OpenAI
from pygame import mixer

# Config.py
from config import (
    JOURNAL_DIRECTORY,
    SYSTEM_PROMPT,
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
    TTS_NOTHING_TO_REPORT,
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
from parsers import EVENT_PARSERS

VERSION = "0.1.0"


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
        default_headers={"X-Title": "ED Ship Helper"},
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
            {"role": "user", "content": event_data},
        ],
        temperature=0.2,
    )

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
        engine.setProperty("voice", voices[index].id)
        engine.setProperty("rate", TTS_WINDOWS_RATE)
        engine.setProperty("volume", TTS_WINDOWS_VOLUME)

        engine.say(text)
        engine.runAndWait()
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

        await communicate.save("./edge-tts-temp.mp3")
        mixer.init()
        mixer.music.load("./edge-tts-temp.mp3")
        mixer.music.play()

        # Wait for playback to finish
        while mixer.music.get_busy():
            time.sleep(0.1)

        mixer.music.unload()
        mixer.quit()
        os.remove("./edge-tts-temp.mp3")

    except Exception as e:
        output(f"Edge TTS error: {str(e)}", COLOR.RED)
        # Optionally fall back to Windows TTS
        if TTS_TYPE != "WINDOWS":
            output("Falling back to Windows TTS", COLOR.YELLOW)
            await send_local_text_to_voice(text)


# Monitor the journal files for new events
def monitor_journal():
    current_journal = get_latest_journal_file(JOURNAL_DIRECTORY)
    if not current_journal:
        output("No journal files found.", COLOR.RED)
        return

    output(f"Monitoring journal file: {current_journal}")

    with open(current_journal, "r") as file:
        file.seek(0, os.SEEK_END)
        while True:
            # Check for a new journal file
            new_journal = get_latest_journal_file(JOURNAL_DIRECTORY)
            if new_journal != current_journal:
                output(f"Switching to new journal file: {new_journal}")
                current_journal = new_journal
                file.close()

                if new_journal:
                    file = open(new_journal, "r")
                    current_journal = new_journal
                else:
                    output("No new journal file found.", COLOR.RED)
                    continue
                file.seek(0, os.SEEK_END)

            line = file.readline()

            if line:
                try:
                    entry = json.loads(line)
                    # Cleanup the entry, getting rid of properties we don't need, like, ever
                    clean_entry = cleanup_event(
                        entry, ["timestamp", "build", "SystemAddress"]
                    )
                    # print(clean_entry)

                    # Start working with the response
                    response = generate_response(clean_entry)

                    if response:
                        # Send the text to the TTS engine
                        speak_response(response)

                except json.JSONDecodeError:
                    pass
            else:
                time.sleep(1)


# Operate on the received event, check if we have specific parsers for it
def generate_response(entry):
    event = entry.get("event", False)
    output(f"Received event: {event}", COLOR.BRIGHT_CYAN)

    if not event:
        return

    # Let's save the current status of the ship
    save_status()

    # Check if the event has a parser
    if event in EVENT_PARSERS:
        parsed_entry = EVENT_PARSERS[event]["function"](entry)
        output(f"Parsed event: {event}", COLOR.BRIGHT_CYAN)
    else:
        parsed_entry = entry

    if parsed_entry is False:
        output("Parser decided to ignore the event", COLOR.BRIGHT_CYAN)
        return False

    if event in EVENT_PARSERS and "context" in EVENT_PARSERS[event]:
        entry_string = (
            EVENT_PARSERS[event]["context"]
            + "Data: "
            + json_to_compact_text(parsed_entry)
        )
    else:
        entry_string = json_to_compact_text(parsed_entry)

    output(entry_string, COLOR.CYAN)

    # If the event is in the list, send it to the AI
    if event in EVENT_LIST:
        output(f"Reacting to event: {event}", COLOR.BRIGHT_CYAN)
        response_text = send_event_to_api(entry_string)

    else:
        output(f"AI ignoring event: {event}", COLOR.BRIGHT_CYAN)
        return False

    # Output the AI response
    if response_text:
        if response_text.startswith("Nothing to report."):
            output(f"AI response: {response_text}", COLOR.CYAN)
            if TTS_NOTHING_TO_REPORT is True:
                return response_text
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
    system_prompt = SYSTEM_PROMPT.replace("{current_status}", str(global_status))

    return system_prompt


# Save information to the ship-state.json file
def set_states(status):
    state_file_path = "ship-state.json"

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

    try:
        with open(journal_file_path, "r") as file:
            for line in file:
                try:
                    entry = json.loads(line)
                    if entry.get("event") == "LoadGame":
                        init_info = {
                            "Ship": entry.get("Ship"),
                            "FuelLevel": entry.get("FuelLevel"),
                            "FuelCapacity": entry.get("FuelCapacity"),
                            "Credits": entry.get("Credits"),
                        }
                        set_states(init_info)
                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        output("Journal file not found", COLOR.RED)
        return None


# Gather information from the ingame status and save it to the ship-state.json file
def save_status():
    status = os.path.join(JOURNAL_DIRECTORY, "Status.json")

    try:
        with open(status, "r") as file:
            status_content = json.load(file)

    except FileNotFoundError:
        output("Status file not found.", COLOR.RED)
        return []
    except json.JSONDecodeError:
        output("Error decoding JSON.", COLOR.RED)
        return []

    current_status = {}
    if "LegalState" in status_content:
        current_status["LegalState"] = status_content["LegalState"]
    if "Balance" in status_content:
        current_status["Credits"] = status_content["Balance"]

    set_states(current_status)

    # HELPERS


def output(string, color=None):
    if color:
        print(f"{color}{string}{COLOR.END}")
    else:
        print(f"{string}")


def cleanup_event(entry, keys_to_remove):
    # List of keys to remove

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

    output("All systems ready!", COLOR.BRIGHT_GREEN)
    speak_response("All systems ready.")

    init_state()
    monitor_journal()

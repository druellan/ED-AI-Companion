## components/memory_manager.py

import json
import datetime
import nltk
import string
from collections import deque
from humanize import naturaldelta

# Config.py
from config import MEMORY_EVENTS, MAX_MEMORY_EVENTS, MAX_MEMORY_RESPONSE
from components.utils import log, json_to_compact_text

event_memory = deque(maxlen=MAX_MEMORY_EVENTS)
response_memory = deque(maxlen=MAX_MEMORY_RESPONSE)


def init_event_memory():
    try:
        with open("event_memory.json", "r") as file:
            event_memory.extend(json.load(file))
    except FileNotFoundError:
        pass


def add_event_memory(event_data, description=False):
    # list of event allowed to be memorized
    if event_data["event"] in MEMORY_EVENTS:
        # event_data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        if description:
            event_data["description"] = description

        event_memory.append(event_data)
        with open("event_memory.json", "w") as file:
            json.dump(list(event_memory), file)


def get_recent_event_memory(count=None):
    current_time = datetime.datetime.utcnow()
    transformed_events = []
    for event in reversed(
        event_memory
    ):  # Iterate in reverse to get the most recent events first
        transformed_event = event.copy()

        if "timestamp" in transformed_event:
            event_time = datetime.datetime.fromisoformat(
                transformed_event["timestamp"].rstrip("Z")
            )
            time_diff = current_time - event_time
            transformed_event["when"] = naturaldelta(time_diff) + " ago"
            del transformed_event["timestamp"]
        transformed_events.append(transformed_event)

        if count is not None and len(transformed_events) >= count:
            break

    return transformed_events


def get_string_recent_event_memory(count=None):
    recent_events = get_recent_event_memory(count)
    event_list = ""

    for event in recent_events:
        # Extract and remove 'when' for timeframe
        timeframe = event.pop("when", None)
        # Extract and remove 'event' for event name
        event_name = event.pop("event", None)
        # Build the rest of the info as key=value pairs
        info = json_to_compact_text(event)
        # Compose the output line
        line = ""
        if timeframe:
            line += f"{timeframe} | "
        if event_name:
            line += f"{event_name} | "
        if info:
            line += info
        event_list += line.strip() + "\n"
    return event_list


def init_response_memory():
    try:
        with open("response_memory.json", "r") as file:
            response_memory.extend(json.load(file))
    except FileNotFoundError:
        log("INFO", "Response memory file not found. Creating a new one.")
        with open("response_memory.json", "w") as file:
            json.dump([], file)


def add_response_memory(response_string):
    if response_string.startswith("NULL"):
        return

    # Download stopwords if not already present
    try:
        from nltk.corpus import stopwords

        stop_words = set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords")
        from nltk.corpus import stopwords

        stop_words = set(stopwords.words("english"))

    # Basic sentence splitting (by period)
    sentences = [s.strip() for s in response_string.split(".") if s.strip()]
    seen = set()
    unique_sentences = []
    for s in sentences:
        if s not in seen:
            seen.add(s)
            unique_sentences.append(s)
    cleaned = []
    for sentence in unique_sentences:
        # Remove punctuation and stopwords
        words = [
            w.strip(string.punctuation)
            for w in sentence.split()
            if w.lower().strip(string.punctuation) not in stop_words
            and w.strip(string.punctuation)
        ]
        cleaned.append(" ".join(words))
    cleaned_response = ". ".join(cleaned)

    entry = {
        "response": cleaned_response,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }
    response_memory.append(entry)
    with open("response_memory.json", "w") as file:
        json.dump(list(response_memory), file)


def get_recent_response_memory(count=None):
    current_time = datetime.datetime.utcnow()
    responses = list(response_memory)
    # responses.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    for response in responses:
        if "timestamp" in response:
            response_time = datetime.datetime.fromisoformat(
                response["timestamp"].rstrip("Z")
            )
            time_diff = current_time - response_time
            response["when"] = naturaldelta(time_diff) + " ago"
            del response["timestamp"]

    if count is None:
        return responses
    return responses[-count:]


# returns a list of memory responses, but in this format: {time} ago | Message
def get_string_recent_response_memory(count=None):
    memory_list = get_recent_response_memory(count)
    # memory_list.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    response_list = ""

    for memory in memory_list:
        if "when" in memory:
            response_list += f"{memory['when']} | "
        response_list += memory["response"] + "\n"
    return response_list

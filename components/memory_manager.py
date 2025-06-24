## components/memory_manager.py

import json
import datetime
import nltk
import string
from collections import deque
from humanize import naturaldelta

# Config.py
from config import MEMORY_EVENTS
from components.utils import log

event_memory = deque(maxlen=20000)
response_memory = deque(maxlen=20000)


def init_event_memory():
    try:
        with open("event_memory.json", "r") as file:
            event_memory.extend(json.load(file))
    except FileNotFoundError:
        pass


def add_event_memory(event_data):
    # list of event allowed to be memorized

    if event_data["event"] in MEMORY_EVENTS:
        event_data["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
        event_memory.append(event_data)
        with open("event_memory.json", "w") as file:
            json.dump(list(event_memory), file)


def get_recent_event_memory(count=None):
    current_time = datetime.datetime.utcnow()
    events = list(event_memory)
    for event in events:
        if "timestamp" in event:
            event_time = datetime.datetime.fromisoformat(event["timestamp"].rstrip("Z"))
            time_diff = current_time - event_time
            event["when"] = naturaldelta(time_diff) + " ago"
            del event["timestamp"]

    if count is None:
        return events
    return events[-count:]


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

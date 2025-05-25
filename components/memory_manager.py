## components/memory_manager.py

import json
import datetime
import nltk
import string
from collections import deque

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
    if count is None:
        return list(event_memory)

    return list(event_memory)[-count:]


def init_response_memory():
    try:
        with open("response_memory.json", "r") as file:
            response_memory.extend(json.load(file))
    except FileNotFoundError:
        log("ERROR", "Response memory file not found")
        pass


def add_response_memory(response_string):
    if response_string == "NULL":
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
    if count is None:
        return list(response_memory)
    return list(response_memory)[-count:]

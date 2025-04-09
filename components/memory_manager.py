import json
from collections import deque

# Config.py
from config import MEMORY_EVENTS

event_memory = deque(maxlen=200)


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

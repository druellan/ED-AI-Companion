import os
import json
from components.constants import COLOR


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
        return (
            "["
            + "|".join(json_to_compact_text(item) for item in data if item is not None)
            + "]"
        )
    elif isinstance(data, bool):
        return "1" if data else "0"
    elif data is None:
        return ""
    else:
        return str(data).replace(" ", "_")


def log(type_str, message):
    type_configs = {
        "INFO": {"color": COLOR.BRIGHT_CYAN, "label": "INFO"},
        "EVENT": {"color": COLOR.BRIGHT_CYAN, "label": "EVENT"},
        "AI": {"color": COLOR.BRIGHT_YELLOW, "label": "AI"},
        "DEBUG": {"color": COLOR.WHITE, "label": "DEBUG"},
        "ERROR": {"color": COLOR.RED, "label": "ERROR"},
        "SYSTEM": {
            "color": COLOR.CYAN,
            "label": "SYSTEM",
        },
    }

    # Convert type_str to uppercase for consistency
    type_str = type_str.upper()

    config = type_configs.get(type_str, type_configs["INFO"])
    from datetime import datetime

    timestamp = datetime.now().strftime("%H:%M:%S")
    SUPERSCRIPT = str.maketrans("0123456789:", "⁰¹²³⁴⁵⁶⁷⁸⁹·")
    superscript = timestamp.translate(SUPERSCRIPT)

    label_text = config["label"]
    padded_text = label_text.ljust(6)
    boxed_label = f"❬{padded_text}❭"

    print(
        f"{COLOR.BRIGHT_BLACK}{superscript} {COLOR.END}{config['color']}{boxed_label} {message}{COLOR.END}"
    )


def rebuild_event_index():
    from components.memory_manager import event_memory
    from config import MEMORY_EVENTS, JOURNAL_DIRECTORY
    from components.utils import log

    from parsers import EVENT_PARSERS

    # Clear the event_memory deque
    log("info", "Cleared event memory.")

    # Find the 3 most recent journal files
    import glob

    journal_files = glob.glob(os.path.join(JOURNAL_DIRECTORY, "Journal*.log"))
    journal_files.sort(key=os.path.getmtime, reverse=True)
    recent_files = journal_files[:30][::-1]  # Reverse so oldest is first

    log("info", f"Processing {len(recent_files)} most recent journal files.")

    event_count = 0
    for journal_file in recent_files:
        log("info", f"Processing {journal_file}")
        with open(journal_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    event = json.loads(line)
                    event_type = event.get("event")
                    if event_type in MEMORY_EVENTS:
                        if event_type in EVENT_PARSERS:
                            event["description"] = EVENT_PARSERS[event_type].get(
                                "description", ""
                            )

                        event_memory.append(event)
                        event_count += 1
                except Exception as e:
                    log("error", f"Failed to process line: {e}")

    with open("event_memory.json", "w") as file:
        json.dump(list(event_memory), file)

    log("info", f"Total events processed: {event_count}")

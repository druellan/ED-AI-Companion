import os
import json
from openai import OpenAI
from components.utils import output, json_to_compact_text
from components.constants import COLOR

from components.state_manager import get_state_all
from components.memory_manager import get_recent_memory
from components.mission_manager import get_missions

# Config.py
from config import (
    JOURNAL_DIRECTORY,
    SYSTEM_PROMPT,
    USER_PROMPT,
    LLM_ENDPOINT,
    LLM_API_KEY,
    LLM_MODEL_NAME,
    LLM_MODEL_NAMES,
)


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

import os
import json
import requests
from openai import OpenAI
from components.utils import log, json_to_compact_text

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
    LLM_MAX_TOKENS_ALERT,
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
        timeout=0.2,
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
        temperature=1.0,
    )

    # Rough token estimation
    # Based on 4 chars per token (GPT uses slightly different rules but this is a rough estimate)
    system_prompt_length = round(len(get_system_prompt()) // 4)
    user_prompt_length = round(len(get_user_prompt(event_data)) // 4)
    estimated_tokens = system_prompt_length + user_prompt_length

    # Log the token estimation
    if estimated_tokens > LLM_MAX_TOKENS_ALERT:
        log("AI", f"WARNING: estimated tokens: {estimated_tokens}")

    log("AI", f"Estimated tokens: {estimated_tokens}")

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
        log("error", "No message from API, trying next LLM")
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


# Check the rate limits
def check_openrouter_rate_limits():
    response = requests.get(
        url="https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {LLM_API_KEY}"},
    )

    # Get rate limits from the response data
    data = response.json().get("data", {})
    limit = data.get("limit")
    limit_remaining = data.get("limit_remaining")
    rate_limit = data.get("rate_limit", {})
    rate_limit_requests = rate_limit.get("requests")
    interval = rate_limit.get("interval")

    log(
        "info",
        f"API Limit: {limit} ({limit_remaining}) | Rate Limit Requests: {rate_limit_requests} Interval: {interval}",
    )

    return response

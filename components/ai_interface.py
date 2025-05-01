# components/ai_interface.py
import json
import os

import requests
from openai import OpenAI

from components import ai_tools
from components.ai_tools import get_available_tools
from components.memory_manager import get_recent_memory
from components.mission_manager import get_missions
from components.state_manager import get_state_all
from components.utils import json_to_compact_text, log

# Config.py
from config import (
    JOURNAL_DIRECTORY,
    LLM_API_KEY,
    LLM_ENDPOINT,
    LLM_MAX_TOKENS_ALERT,
    LLM_MODEL_NAME,
    LLM_MODEL_NAMES,
    LLM_USE_TOOLS,
    SYSTEM_PROMPT,
    USER_PROMPT,
    DEBUG_AI_PROMPT_DUMP
)


# Send event data to the AI API
def send_event_to_api(event_data, tool_response=None):
    client = OpenAI(
        base_url=LLM_ENDPOINT,
        api_key=LLM_API_KEY,
        default_headers={
            "X-Title": "ED:AI Companion",
            "HTTP-Referer": "ED:AI Companion",
        },
        timeout=20.0,
    )

    # Send the prompt to a file
    if DEBUG_AI_PROMPT_DUMP:
        with open("last_prompt.json", "w") as file:
            last_prompt = get_system_prompt() + "\n\n" + get_user_prompt(event_data)
            file.write(last_prompt)

    # Rough token estimation
    # Based on 4 chars per token (GPT uses slightly different rules but this is a rough estimate)
    system_prompt_length = round(len(get_system_prompt()) // 4)
    user_prompt_length = round(len(get_user_prompt(event_data)) // 4)
    estimated_tokens = system_prompt_length + user_prompt_length

    # Log the token estimation
    if estimated_tokens > LLM_MAX_TOKENS_ALERT:
        log("AI", f"WARNING: estimated tokens: {estimated_tokens}")

    log("AI", f"Estimated tokens: {estimated_tokens}")

    # get the list of all tools available
    if LLM_USE_TOOLS and not tool_response:
        tool_list = json.loads(get_available_tools())
    else:
        tool_list = []

    # get ready the promps
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": get_user_prompt(event_data)}
    ]
    
    # Add tool response if it exists
    if tool_response:
        messages.append(tool_response)

    # get the AI response
    ai_response = client.chat.completions.create(
        model=LLM_MODEL_NAME,
        extra_body={
            "models": LLM_MODEL_NAMES,
        },
        tools=tool_list,
        messages=messages,
        temperature=0.1,
    )

    if not ai_response or not ai_response.choices:
        log("error", "No response or choices from API")
        return "Error: No response from AI"

    ai_message = ai_response.choices[0].message

    # Check if response has content
    # if not ai_response or not ai_message.content:
    #     log("error", "No message content from API")
    #     return "Error: No response from AI"
    
    string_response = ai_message.content

    # Check for tool calls if they exist
    if hasattr(ai_message, 'tool_calls') and ai_message.tool_calls and LLM_USE_TOOLS:
        if ai_message.tool_calls is not None:
            tool_response = get_tool_response(ai_message)
            if tool_response:
                string_response = send_event_to_api(event_data, tool_response)

    return string_response


def get_tool_response(ai_message):
    tool_call = ai_message.tool_calls[0]
    tool_name = tool_call.function.name
    tool_args = json.loads(tool_call.function.arguments)

    tool_function = getattr(ai_tools, tool_name, None)

    if tool_function and callable(tool_function):
        log("AI", f"Calling Tool '{tool_name}'")
        try:
            if tool_args is not None:
                tool_output = tool_function(**tool_args)  # Use unpacking to pass arguments correctly
            else:
                tool_output = tool_function()

            # For now, we just return the first tool output found.
            # Future steps might involve processing multiple tool calls
            # or sending the output back to the AI.

            # let's recursively call the AI again, but this time we return the function response
            tool_result = json_to_compact_text(tool_output)  # Remove extra JSON encoding since output is already JSON

            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_result,
            }
        except Exception as e:
            log("error", f"Error executing tool '{tool_name}': {e}")
            return None
        
    return None


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
    # log("debug", system_prompt)
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
        f"API Limit: {limit} ({limit_remaining}) | Rate Limit Requests: {rate_limit_requests} | Interval: {interval}",
    )

    return response

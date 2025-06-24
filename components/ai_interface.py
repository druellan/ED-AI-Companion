# components/ai_interface.py
import json
import os
import re

from typing import cast

import requests
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from components import ai_tools
from components.ai_tools import _get_available_tools
from components.memory_manager import (
    get_recent_event_memory,
    add_response_memory,
    get_recent_response_memory,
)
from components.mission_manager import get_missions
from components.state_manager import (
    get_state_all,
    get_navigation_status,
    get_cargo_status,
)
from components.utils import json_to_compact_text, log

# Config.py
from config import (
    DEBUG_AI_PROMPT_DUMP,
    DAMAGE_EFFECTS,
    USER_INFORMATION,
    JOURNAL_EVENT_MEMORY,
    JOURNAL_RESPONSE_MEMORY,
    LLM_API_KEY,
    LLM_ENDPOINT,
    LLM_MAX_TOKENS_ALERT,
    LLM_MODEL_NAME,
    LLM_MODEL_NAMES,
    LLM_USE_TOOLS,
    SYSTEM_PROMPT,
    ASSISTANT_PROMPT,
    TOOLS_PROMPT,
    USER_PROMPT,
)


# Check the rate limits
def get_openrouter_rate_limits():
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

    system_prompt = _get_system_prompt()
    assistant_prompt = _get_assistant_prompt()
    user_prompt = _get_user_prompt(event_data)

    _log_token_estimation(system_prompt, user_prompt, assistant_prompt)

    # get ready the prompts
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": assistant_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Add tool response if it exists (this will be used for the new tool calling mechanism)

    if tool_response:
        messages.append(
            cast(ChatCompletionMessageParam, {"role": "tool", "content": tool_response})
        )

    # Send the prompt content to a plain text file
    if DEBUG_AI_PROMPT_DUMP:
        # debug to check how the last prompt has constructed
        with open("last_prompt.json", "w", encoding="utf-8") as file:
            file.write("--- SYSTEM ---\n")
            file.write(str(system_prompt))
            file.write("--- ASSISTANT ---\n")
            file.write(str(assistant_prompt))
            file.write("\n\n--- USER ---\n")
            file.write(str(user_prompt))
            file.write("\n")

    # get the AI response
    try:
        ai_response = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            extra_body={
                "models": LLM_MODEL_NAMES,
            },
            messages=messages,
            temperature=0.1,
        )

        if hasattr(ai_response, "error"):
            log("error", f"API Error: {ai_response}")
            return "API Error"

        if not ai_response or not ai_response.choices:
            log("error", "No response or choices from API")
            return "Error: No response from AI"

        ai_message_content = ai_response.choices[0].message.content

        # Process the AI response for tool calls

        tool_output = None
        if LLM_USE_TOOLS:
            tool_output = _get_tool_response(ai_message_content)

        if tool_output:
            # If a tool was called and returned output, send it back to the AI
            log("debug", tool_output)
            return send_event_to_api(event_data, json_to_compact_text(tool_output))
        else:
            # Otherwise, return the AI's original message content
            add_response_memory(ai_message_content)
            post_processed_message_content = _process_response_artifacts(
                ai_message_content
            )
            return post_processed_message_content

    except requests.exceptions.HTTPError as e:
        log("error", f"An API error occurred: {e}")
        # Attempt to extract and print the JSON response if available
        if hasattr(e, "response") and hasattr(e.response, "json"):
            try:
                error_json = e.response.json()
                log(
                    "error",
                    f"API Error Response JSON: {json.dumps(error_json, indent=2)}",
                )
            except json.JSONDecodeError:
                log("error", "Could not decode API error response as JSON.")
        return "Error communicating with AI API"


def _get_tool_response(ai_message_content):
    pattern = r"^(\w+)\((.*)\)$"
    tool_output = None

    # Use re.finditer with the re.MULTILINE flag
    # This finds all matches, but we'll process only the first valid one.
    iterator = re.finditer(pattern, ai_message_content.strip(), re.MULTILINE)

    for match in iterator:
        # Process the first match found
        tool_name = match.group(1)
        tool_param_string = match.group(2).strip()
        matched_line = match.group(0)  # The full line that matched

        tool_function = getattr(ai_tools, tool_name, None)

        if tool_function and callable(tool_function):
            log(
                "AI",
                f"Attempting to call Tool '{tool_name}' with parameter '{tool_param_string}'",
            )
            try:
                if tool_param_string:
                    cleaned_param = tool_param_string.strip().strip("'\"")
                    tool_output = tool_function(cleaned_param)
                else:
                    # Call function without arguments if param string is empty
                    tool_output = tool_function()

                log(
                    "AI",
                    f"Successfully called Tool '{tool_name}' returning '{tool_output}'.",
                )
                return tool_output

            except TypeError as e:
                log(
                    "error",
                    f"Error calling tool '{tool_name}' with parameter '{tool_param_string}' from line '{matched_line}': Incorrect arguments. {e}",
                )
                # Stop processing after the first attempt, even if it fails
                return None
            except Exception as e:
                log(
                    "error",
                    f"Error executing tool '{tool_name}' with parameter '{tool_param_string}' from line '{matched_line}': {e}",
                )
                # Stop processing after the first attempt, even if it fails
                return None
        else:
            log(
                "AI",
                f"Tool '{tool_name}' found in '{matched_line}' but is not found or not callable in ai_tools.",
            )
            # Stop processing as we only care about the first potential tool call line
            return None

    # Return None if the iterator had no matches or the first match wasn't a valid/executable tool
    return None


# Get the main prompt and enrich it with the current status
def _get_system_prompt():
    system_prompt = SYSTEM_PROMPT.replace("{user_information}", USER_INFORMATION)

    if LLM_USE_TOOLS:
        system_prompt += TOOLS_PROMPT
        system_prompt += _get_available_tools()

    return system_prompt


# Get the assistant prompts
def _get_assistant_prompt():
    global_status = get_state_all()
    recent_events = get_recent_event_memory(JOURNAL_EVENT_MEMORY)
    recent_responses = get_recent_response_memory(JOURNAL_RESPONSE_MEMORY)
    navdata = get_navigation_status()
    missions = get_missions()
    cargo_inventory = get_cargo_status()

    system_prompt = (
        ASSISTANT_PROMPT.replace(
            "{current_status}", json_to_compact_text(global_status)
        )
        .replace("{recent_events}", json_to_compact_text(recent_events))
        .replace("{current_cargo}", json_to_compact_text(cargo_inventory))
        .replace("{current_missions}", json_to_compact_text(missions))
        .replace("{recent_responses}", json_to_compact_text(recent_responses))
        .replace("{navroute_status}", json_to_compact_text(navdata))
    )

    return system_prompt


# Get the main prompt and add the context
def _get_user_prompt(context):
    user_prompt = USER_PROMPT.replace("{event_new}", str(context))

    return user_prompt


# Just a helper to calculate and log token estimations
def _log_token_estimation(system_prompt, user_prompt, assistant_prompt):
    # Rough token estimation
    # Based on 3.5 chars per token (GPT uses slightly different rules but this is a rough estimate)
    system_prompt_length = round(len(system_prompt) // 3.5)
    assistant_prompt_length = round(len(assistant_prompt) // 3.5)
    user_prompt_length = round(len(user_prompt) // 3.5)

    estimated_tokens = (
        system_prompt_length + user_prompt_length + assistant_prompt_length
    )

    # Log the token estimation
    if estimated_tokens > LLM_MAX_TOKENS_ALERT:
        log("AI", f"WARNING: estimated tokens: {estimated_tokens}")

    log("AI", f"Estimated tokens: {estimated_tokens}")


def _process_response_artifacts(response_content):
    import random

    if not DAMAGE_EFFECTS:
        return response_content

    state = get_state_all()
    hull_health = state["HullHealth"]

    # if hull_health > 0.3:
    #     return response_content

    def stutter_word(word):
        # Repeat small words (less than 10 letters)
        if len(word) < 9:
            clean_word = word.rstrip(".,!?")
            repeats = random.randint(2, 5)
            result = clean_word
            for _ in range(repeats - 1):
                separator = "," if random.random() < 0.5 else ""
                if (
                    _ == repeats - 2
                ):  # Last repetition uses original word with punctuation
                    result += f"{separator}{word}"
                else:
                    result += f"{clean_word}"
            return result
        return word

    def last_vowel_repeat(word):
        # Define vowels
        vowels = set("aiu")  # those seems to be the most efectives for TTS

        # Clean the word from any punctuation for processing
        clean_word = word.rstrip(".,!?")

        # If the word ends in a vowel, repeat it 10-20 times
        if clean_word and clean_word[-1] in vowels:
            repeated_vowel = clean_word[-1] * random.randint(10, 20)
            punct = word[len(clean_word) :]
            return f"{clean_word}{repeated_vowel}{punct}"
        return word

    # Split content into words
    words = response_content.split()
    processed_words = []

    stutter_chances = 0.1 * (1 - hull_health)
    vowel_repeat_chances = 0.30 * (1 - hull_health)

    for word in words:
        # Apply random artifacts with different probabilities
        if random.random() < stutter_chances:
            processed_words.append(stutter_word(word))
        elif random.random() < vowel_repeat_chances:
            processed_words.append(last_vowel_repeat(word))
        else:
            processed_words.append(word)

    # Join words back together
    processed_content = " ".join(processed_words)

    return processed_content

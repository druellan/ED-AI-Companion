# components/ai_interface.py
import json

import requests
from openai import OpenAI


from components import ai_tools
from components.memory_manager import (
    get_string_recent_event_memory,
    add_response_memory,
    get_string_recent_response_memory,
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
def send_event_to_api(event_data, tool_response=None, tool_call_id=None):
    client = OpenAI(
        base_url=LLM_ENDPOINT,
        api_key=LLM_API_KEY,
        default_headers={
            "X-Title": "ED:AI Companion",
            "HTTP-Referer": "ED:AI Companion",
        },
        timeout=10.0,
    )

    system_prompt = _get_system_prompt()
    assistant_prompt = _get_assistant_prompt()
    user_prompt = _get_user_prompt(event_data)
    tools = False

    if LLM_USE_TOOLS:
        tools = json.loads(ai_tools._get_available_tools())

    _log_token_estimation(system_prompt, user_prompt, assistant_prompt)

    # get ready the prompts
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": assistant_prompt},
        {"role": "user", "content": user_prompt},
    ]

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
            tools=tools,
            temperature=0.1,
        )

        if hasattr(ai_response, "error"):
            log("error", f"API Error: {ai_response}")
            return "API Error"

        if not ai_response or not ai_response.choices:
            log("error", "No response or choices from API")
            return "Error: No response from AI"

        message = ai_response.choices[0].message

        # Unified final message handling
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_response = getattr(ai_tools, tool_name)(**tool_args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_response),
                    }
                )
            # Get the final answer after tool responses
            ai_response = client.chat.completions.create(
                model=LLM_MODEL_NAME,
                extra_body={
                    "models": LLM_MODEL_NAMES,
                },
                messages=messages,
                tools=tools,
                temperature=0.1,
            )
            final_message = ai_response.choices[0].message
        else:
            final_message = message

        ai_message_content = final_message.content
        add_response_memory(ai_message_content)
        post_processed_message_content = _process_response_artifacts(ai_message_content)
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


# Get the main prompt and enrich it with the current status
def _get_system_prompt():
    global_status = get_state_all()
    navdata = get_navigation_status()
    missions = get_missions()
    cargo_inventory = get_cargo_status()

    prompt = (
        SYSTEM_PROMPT.replace("{current_status}", json_to_compact_text(global_status))
        .replace("{current_cargo}", json_to_compact_text(cargo_inventory))
        .replace("{current_missions}", json_to_compact_text(missions))
        .replace("{navroute_status}", json_to_compact_text(navdata))
        .replace("{user_information}", USER_INFORMATION)
    )

    if LLM_USE_TOOLS:
        prompt += TOOLS_PROMPT

    return prompt


# Get the assistant prompts
def _get_assistant_prompt():
    global_status = get_state_all()
    recent_events = get_string_recent_event_memory(JOURNAL_EVENT_MEMORY)
    recent_responses = get_string_recent_response_memory(JOURNAL_RESPONSE_MEMORY)
    navdata = get_navigation_status()
    missions = get_missions()
    cargo_inventory = get_cargo_status()

    prompt = (
        ASSISTANT_PROMPT.replace(
            "{current_status}", json_to_compact_text(global_status)
        )
        .replace("{recent_events}", (recent_events))
        .replace("{current_cargo}", json_to_compact_text(cargo_inventory))
        .replace("{current_missions}", json_to_compact_text(missions))
        .replace("{recent_responses}", recent_responses)
        .replace("{navroute_status}", json_to_compact_text(navdata))
    )

    return prompt


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

    if hull_health > 0.3:
        return response_content

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

"""The agent's tool-calling loop.

Given a starting prompt, repeatedly asks the model for a next step. If the
model requests tool calls, they're executed and their results are fed back
in; if it returns plain text, that's the final answer.
"""

import time

from google import genai
from google.genai import types

from jarvis.config import MAX_ITERATIONS, MODEL_NAME, RATE_LIMIT_DELAY_SECONDS
from jarvis.prompts import system_prompt
from jarvis.tools.call_function import available_functions, call_function


def run(client: genai.Client, user_prompt: str, verbose: bool = False) -> str | None:
    """Run the agent to completion on a single prompt.

    Returns the model's final text response, or None if the agent hit
    MAX_ITERATIONS without producing one.
    """
    message_history = [types.Content(role="user", parts=[types.Part(text=user_prompt)])]

    for _ in range(MAX_ITERATIONS):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message_history,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            ),
        )

        function_calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)

        if not function_calls:
            return response.text or ""

        if verbose:
            print(f"Model requested {len(function_calls)} function call(s)...")

        message_history.append(response.candidates[0].content)

        for function_call in function_calls:
            result_content = call_function(function_call, verbose=verbose)
            message_history.append(result_content)

            if verbose:
                try:
                    result_data = result_content.parts[0].function_response.response
                    print(f" -> Function result: {result_data}")
                except (AttributeError, IndexError):
                    print(" -> Function result: [could not read response]")

        # Small pause between tool-call round trips to stay under Gemini's
        # free-tier rate limit. Bump RATE_LIMIT_DELAY_SECONDS in config.py
        # if you're still hitting 429s.
        time.sleep(RATE_LIMIT_DELAY_SECONDS)

    return None

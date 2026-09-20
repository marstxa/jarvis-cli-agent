import argparse
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MAX_ITERATIONS, MODEL_NAME, RATE_LIMIT_DELAY_SECONDS
from functions.call_function import available_functions, call_function
from prompts import system_prompt


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY is not set. Create a .env file with GEMINI_API_KEY=<your key>.")

    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Jarvis: a minimal tool-calling coding agent")
    parser.add_argument("user_prompt", type=str, help="The task to give the agent")
    parser.add_argument("--verbose", action="store_true", help="Print each function call and its result")
    args = parser.parse_args()

    message_history = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    for iteration in range(MAX_ITERATIONS):
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
            if response.text:
                print(f"Response:\n{response.text}")
            else:
                print("Error: model returned an empty response.")
            return

        if args.verbose:
            print(f"Model requested {len(function_calls)} function call(s)...")

        message_history.append(response.candidates[0].content)

        for function_call in function_calls:
            result_content = call_function(function_call, verbose=args.verbose)
            message_history.append(result_content)

            if args.verbose:
                try:
                    result_data = result_content.parts[0].function_response.response
                    print(f" -> Function result: {result_data}")
                except (AttributeError, IndexError):
                    print(" -> Function result: [could not read response]")

        # Small pause between tool-call round trips to stay under Gemini's
        # free-tier rate limit. Bump RATE_LIMIT_DELAY_SECONDS in config.py
        # if you're still hitting 429s.
        time.sleep(RATE_LIMIT_DELAY_SECONDS)

    print(f"Stopped after {MAX_ITERATIONS} tool-call rounds without a final answer.")


if __name__ == "__main__":
    main()

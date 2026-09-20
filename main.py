import argparse
import os

from dotenv import load_dotenv
from google import genai
from jarvis.agent import run

from jarvis.config import MAX_ITERATIONS


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise RuntimeError("GEMINI_API_KEY is not set. Create a .env file with GEMINI_API_KEY=<your key>.")

    parser = argparse.ArgumentParser(description="Jarvis: a minimal tool-calling coding agent")
    parser.add_argument("user_prompt", type=str, help="The task to give the agent")
    parser.add_argument("--verbose", action="store_true", help="Print each function call and its result")
    args = parser.parse_args()

    client = genai.Client(api_key=api_key)
    result = run(client, args.user_prompt, verbose=args.verbose)

    if result:
        print(f"Response:\n{result}")
    elif result is None:
        print(f"Stopped after {MAX_ITERATIONS} tool-call rounds without a final answer.")
    else:
        print("Error: model returned an empty response.")


if __name__ == "__main__":
    main()

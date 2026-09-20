"""Configuration constants for the agent."""

# Character limit applied when reading a file, so a huge file doesn't blow
# out the context window sent to the model.
MAX_CHARS = 10000

# The agent is only ever allowed to read, write, and execute files inside
# this directory. It's injected into every function call regardless of
# what the model asks for, so a prompt-injected or hallucinated path can't
# make the agent touch anything outside it. See calculator/README.md for
# what this sandboxed project is.
WORKING_DIRECTORY = "./calculator"

# Hard cap on how many times the agent is allowed to call tools in a single
# run, so a model that keeps requesting function calls (a bad plan, a loop,
# a misbehaving response) can't run indefinitely.
MAX_ITERATIONS = 20

# Gemini's free tier is rate-limited per minute. This is a small pause
# between tool-call round trips to stay under it; raise it if you're
# hitting 429s.
RATE_LIMIT_DELAY_SECONDS = 2

MODEL_NAME = "gemini-2.5-flash"

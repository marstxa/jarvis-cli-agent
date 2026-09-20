# Jarvis — a minimal tool-calling coding agent

A small coding agent built from scratch on top of the Gemini API. You give it
a task in natural language; it plans which of a handful of file tools to
call, executes them, reads the results, and repeats until it has an answer.
No agent framework — the tool-calling loop, the function schemas, and the
sandboxing are all hand-written to understand how the pattern actually works
underneath tools like Claude Code or Cursor.

> **Educational project.** It runs arbitrary Python files as subprocesses
> with the permissions of whoever runs it. Don't point it at anything you
> don't trust, and don't run it as anyone but yourself.

## What it can do

The model has four tools available, all scoped to a single sandboxed
directory (`calculator/` by default — see below):

| Tool | Purpose |
|---|---|
| `get_files_info` | List a directory's contents with file sizes |
| `get_file_content` | Read a file, truncated to a character limit |
| `write_file` | Create or overwrite a file |
| `run_python_file` | Execute a `.py` file as a subprocess, with optional args |

## Why `calculator/` exists

`calculator/` is a small, self-contained expression-evaluator project — an
infix parser with operator precedence, not just `eval()` — that exists
purely as something for the agent to read, run, and modify. It's not part
of the agent itself. Every tool call is hardcoded to operate inside this
directory (see `config.py`), regardless of what path the model asks for, so
the agent has something real to work with but can't touch anything outside
the sandbox. `calculator/lorem.txt` and `calculator/pkg/morelorem.txt` are
intentionally silly placeholder files the agent overwrites when asked to
edit something — if you run the agent yourself, expect their contents to
change.

## Setup

Requires Python (version pinned in `.python-version`) and a
[Gemini API key](https://ai.google.dev/).

```bash
git clone https://github.com/marstxa/jarvis-cli-agent
cd jarvis-cli-agent
```

This project uses [`uv`](https://docs.astral.sh/uv/) to manage
dependencies in an isolated virtual environment. If you don't have `uv`:

```bash
# Arch
sudo pacman -S uv
# anything else
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install dependencies. `uv sync` creates a `.venv/` folder inside the
project and installs everything into it — it does not touch your system
Python, so `import google.genai` will fail outside this environment.

```bash
uv sync
echo "GEMINI_API_KEY=your-key-here" > .env
```

Run commands one of two ways: prefix them with `uv run` (no activation
needed), or activate the environment once per shell session and use plain
`python` after that:

```bash
uv run main.py "list the files"
# or
source .venv/bin/activate
python main.py "list the files"
```

No `uv`? Use the stdlib instead:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
python main.py "list the files in the project"
python main.py "read pkg/calculator.py and explain what it does"
python main.py "add a power operator to the calculator and test it" --verbose
```

`--verbose` prints every function call the model makes and the result it
gets back — the most useful way to see the agent's actual plan rather than
just its final answer.

## How it works

1. The prompt becomes the first message in a conversation history sent to
   `gemini-2.5-flash`, along with the schemas for the four tools above. This
   loop lives in `jarvis/agent.py`; `main.py` only handles argument parsing
   and the API key.
2. If the model's response contains function calls, each one is executed
   against `calculator/` and the result is appended back into the history.
3. The full history — including tool results — is sent back to the model,
   which decides whether it has enough information to answer or needs to
   call more tools.
4. This repeats until the model returns a plain text response, or until
   `MAX_ITERATIONS` tool-call rounds pass without one (a safety cap against
   the model looping indefinitely).

Every tool call goes through the same path validation: the requested path
is resolved against the sandbox root and checked with `os.path.commonpath`,
so `../../etc/passwd`-style traversal is rejected before any file
operation happens.

## Tests

```bash
uv run python -m unittest discover
# or, with the venv activated:
python -m unittest discover
```

Each tool has its own test file under `tests/` (`test_get_files_info.py`,
etc.), covering both the happy path and the sandbox-escape and error cases.
`calculator/tests.py` is a separate, unrelated test suite — it tests the
calculator sandbox project itself, not the agent, and exists so the agent
has something to *run* via `run_python_file`.

## Project layout

```
main.py                    Entry point: CLI parsing only, delegates to jarvis.agent
jarvis/
  agent.py                  The tool-calling loop itself
  config.py                 Constants: sandbox path, iteration cap, model name
  prompts.py                System prompt
  tools/
    call_function.py       Dispatches a model function call to the right tool
    get_files_info.py
    get_file_content.py
    write_file.py
    run_python_file.py
tests/                      Tests for the agent's own tools
calculator/                 Sandboxed demo project the agent operates on
  main.py, pkg/             An infix expression evaluator, unrelated to the agent
  tests.py                  Tests for the calculator, not for the agent
```

## Limitations

- No streaming — the CLI blocks until the model responds.
- Single-directory sandbox by design; not meant to operate across a real
  project tree.
- `gemini-2.5-flash` only; swapping models means adjusting
  `config.MODEL_NAME` and possibly the system prompt.
import os
import subprocess
import sys

from google.genai import types


def run_python_file(working_directory, file_path, args=None):
    working_directory_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_directory_abs, file_path))

    if os.path.commonpath([working_directory_abs, target_path]) != working_directory_abs:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(target_path):
        return f'Error: "{file_path}" does not exist'

    if not target_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    command = [sys.executable, target_path, *(args or [])]

    try:
        completed_process = subprocess.run(command, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return "Error: Process timed out after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"

    # Previously, a non-zero exit code short-circuited this into a bare
    # "Process exited with code N" with no stdout/stderr, which threw away
    # the one thing you need to debug why it failed. Always report both
    # streams, and note the exit code as well when it's non-zero.
    parts = []
    if completed_process.stdout:
        parts.append(f"STDOUT: {completed_process.stdout}")
    if completed_process.stderr:
        parts.append(f"STDERR: {completed_process.stderr}")
    if completed_process.returncode != 0:
        parts.append(f"Process exited with code {completed_process.returncode}")
    if not parts:
        parts.append("No output produced.")

    return "\n".join(parts)


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python file within a working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file to run, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Arguments to pass to the Python file",
            ),
        },
    ),
)

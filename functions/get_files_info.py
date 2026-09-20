import os

from google.genai import types


def get_files_info(working_directory, directory="."):
    working_directory_abs = os.path.abspath(working_directory)
    target_path = os.path.normpath(os.path.join(working_directory_abs, directory))

    if os.path.commonpath([working_directory_abs, target_path]) != working_directory_abs:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_path):
        return f'Error: "{directory}" is not a directory'

    entries = os.listdir(target_path)
    if not entries:
        return f'"{directory}" is empty'

    lines = []
    for name in sorted(entries):
        entry_path = os.path.join(target_path, name)
        lines.append(f"- {name}: {os.path.getsize(entry_path)} bytes, is_dir={os.path.isdir(entry_path)}")

    return "\n".join(lines)


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

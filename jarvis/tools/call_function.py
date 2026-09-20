from google.genai import types

from jarvis.config import WORKING_DIRECTORY
from jarvis.tools.get_file_content import get_file_content, schema_get_file_content
from jarvis.tools.get_files_info import get_files_info, schema_get_files_info
from jarvis.tools.run_python_file import run_python_file, schema_run_python_file
from jarvis.tools.write_file import schema_write_file, write_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ],
)

FUNCTION_MAP = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call, verbose=False):
    function_name = function_call.name or ""

    if verbose:
        print(f"Calling function: {function_name}({function_call.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in FUNCTION_MAP:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    # The model never controls which directory a call runs against: whatever
    # working_directory it might supply is overwritten here, after copying
    # its args, so the sandbox can't be escaped via a crafted function call.
    args = dict(function_call.args) if function_call.args else {}
    args["working_directory"] = WORKING_DIRECTORY
    function_result = FUNCTION_MAP[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

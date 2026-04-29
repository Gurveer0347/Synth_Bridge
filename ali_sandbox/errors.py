import re


ERROR_HINTS = {
    "ConnectionError": (
        "Could not reach the API endpoint.",
        "Check the base URL, endpoint path, and network availability.",
    ),
    "HTTPError": (
        "The API returned an HTTP failure.",
        "Check status code, auth headers, and endpoint path from the docs.",
    ),
    "KeyError": (
        "Generated code tried to access a field that does not exist.",
        "Check the field mapping and use the available lead field names.",
    ),
    "ImportError": (
        "Generated code used a library that is not installed.",
        "Use only Python standard library modules for the demo bridge.",
    ),
    "ModuleNotFoundError": (
        "Generated code imported a missing Python package.",
        "Use only Python standard library modules for the demo bridge.",
    ),
    "TimeoutExpired": (
        "Script ran too long and was killed.",
        "Check for infinite loops or hanging API calls.",
    ),
    "SyntaxError": (
        "Generated code contains invalid Python syntax.",
        "Regenerate valid raw Python only.",
    ),
    "PermissionError": (
        "Generated code attempted an unsafe or blocked operation.",
        "Remove destructive file/process operations from the generated bridge.",
    ),
    "ValueError": (
        "Generated code raised a validation error.",
        "Fix the specific validation failure while keeping the bridge logic unchanged.",
    ),
}


def _short_type(error_type: str) -> str:
    return error_type.rsplit(".", 1)[-1]


def classify_error(stderr: str, exit_code: int, timed_out: bool = False) -> dict:
    if timed_out:
        error_type = "TimeoutExpired"
        error_message = stderr.strip() or "Script timed out"
        line_number = None
    else:
        lines = [line.strip() for line in stderr.splitlines() if line.strip()]
        last_line = lines[-1] if lines else f"Process exited with code {exit_code}"
        if ":" in last_line:
            raw_type, error_message = last_line.split(":", 1)
            error_type = _short_type(raw_type.strip())
            error_message = error_message.strip()
        else:
            error_type = "RuntimeError"
            error_message = last_line

        line_number = None
        for line in lines:
            match = re.search(r"line (\d+)", line)
            if match:
                line_number = int(match.group(1))

    likely_cause, fix_hint = ERROR_HINTS.get(
        error_type,
        (
            "Generated code failed during execution.",
            "Read the error message and repair only the failing part.",
        ),
    )
    if "401" in stderr or "Unauthorized" in stderr:
        error_type = "HTTPError"
        likely_cause = "Authentication failed."
        fix_hint = "Check the Authorization header and token format."
    elif "404" in stderr or "Not Found" in stderr:
        error_type = "HTTPError"
        likely_cause = "Endpoint URL does not exist."
        fix_hint = "Check the API endpoint path from the documentation."

    return {
        "error_type": error_type,
        "error_message": error_message,
        "line_number": line_number,
        "likely_cause": likely_cause,
        "fix_hint": fix_hint,
    }

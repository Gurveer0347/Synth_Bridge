from collections.abc import Callable

from .demo_scripts import success_code
from .errors import classify_error
from .sandbox import run_code


RepairFunc = Callable[[str, dict, int, str], str]


def default_repair_code(code: str, error_log: dict, attempt: int, mode: str) -> str:
    """Demo repair agent: converts classified failures into a corrected bridge."""
    return success_code(mode)


def _retry_instruction(error_log: dict, duplicate: bool = False) -> str:
    if duplicate:
        return (
            "You generated identical code. Try a different approach. "
            "Fix only the specific issue and output raw Python only."
        )
    return (
        "The previous code failed. Read the error carefully. "
        f"Error type: {error_log['error_type']}. "
        f"Fix hint: {error_log['fix_hint']} "
        "Fix only the specific issue. Keep everything else the same. Output raw Python only."
    )


def _failed_duplicate_attempt(attempt_number: int, previous_code: str) -> dict:
    error_log = {
        "error_type": "DuplicateCode",
        "error_message": "Repair agent returned identical code.",
        "line_number": None,
        "likely_cause": "The synthesis agent did not apply the feedback.",
        "fix_hint": "Try a different implementation instead of repeating the same script.",
    }
    return {
        "attempt": attempt_number,
        "success": False,
        "stdout": "",
        "stderr": "Repair agent generated identical code; sandbox run skipped.",
        "exit_code": 125,
        "timed_out": False,
        "duration_seconds": 0.0,
        "generated_code": previous_code,
        "error_log": error_log,
        "retry_instruction": _retry_instruction(error_log, duplicate=True),
        "duplicate_code": True,
    }


def _final_error(attempts: list[dict]) -> str:
    if not attempts:
        return "ALI did not run any attempts."
    summaries = []
    for attempt in attempts:
        error_log = attempt.get("error_log") or {}
        error_type = error_log.get("error_type", "UnknownError")
        message = error_log.get("error_message", attempt.get("stderr", "").strip())
        summaries.append(f"Attempt {attempt['attempt']}: {error_type} - {message}")
    return "ALI could not complete the bridge after retries. " + " | ".join(summaries)


def run_self_healing_bridge(
    initial_code: str,
    mode: str = "discord_live",
    max_retries: int = 3,
    timeout_seconds: int = 30,
    repair_func: RepairFunc | None = None,
) -> dict:
    repair = repair_func or default_repair_code
    current_code = initial_code
    previous_code = None
    attempts = []

    for attempt_number in range(1, max_retries + 1):
        if previous_code is not None and current_code == previous_code:
            attempt = _failed_duplicate_attempt(attempt_number, current_code)
            attempts.append(attempt)
            previous_code = current_code
            current_code = repair(current_code, attempt["error_log"], attempt_number, mode)
            continue

        execution = run_code(current_code, timeout_seconds=timeout_seconds)
        error_log = None
        retry_instruction = None
        if not execution["success"]:
            error_log = classify_error(
                execution["stderr"],
                execution["exit_code"],
                timed_out=execution["timed_out"],
            )
            retry_instruction = _retry_instruction(error_log)

        attempt = {
            "attempt": attempt_number,
            **execution,
            "generated_code": current_code,
            "error_log": error_log,
            "retry_instruction": retry_instruction,
            "duplicate_code": False,
        }
        attempts.append(attempt)

        if execution["success"]:
            return {
                "success": True,
                "generated_code": initial_code,
                "final_code": current_code,
                "output": execution["stdout"],
                "error": None,
                "attempts": attempts,
                "stage": "done",
            }

        previous_code = current_code
        current_code = repair(current_code, error_log, attempt_number, mode)

    return {
        "success": False,
        "generated_code": initial_code,
        "final_code": current_code,
        "output": attempts[-1]["stdout"] if attempts else "",
        "error": _final_error(attempts),
        "attempts": attempts,
        "stage": "failed",
    }

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


BLOCKED_PATTERNS = (
    "shutil.rmtree",
    "os.remove",
    "os.unlink",
    "os.rmdir",
    "Path.unlink",
    "Path.rmdir",
    "subprocess.",
    "eval(",
    "exec(",
)


def _safety_violation(code: str) -> str | None:
    for pattern in BLOCKED_PATTERNS:
        if pattern in code:
            return pattern
    return None


def run_code(code: str, timeout_seconds: int = 30) -> dict:
    """Run generated Python in a child process and return structured output."""
    blocked = _safety_violation(code)
    if blocked:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Blocked unsafe generated code before execution: {blocked}",
            "exit_code": 126,
            "timed_out": False,
            "duration_seconds": 0.0,
        }

    temp_path = None
    workdir = None
    start = time.perf_counter()
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONIOENCODING": "utf-8",
        "ALI_DEMO_MODE": os.environ.get("ALI_DEMO_MODE", ""),
    }
    for secret_name in ("DISCORD_WEBHOOK_URL", "HUBSPOT_PRIVATE_APP_TOKEN", "HUBSPOT_ACCESS_TOKEN"):
        if secret_name in os.environ:
            env[secret_name] = os.environ[secret_name]

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        workdir = tempfile.mkdtemp(prefix="ali_sandbox_")
        result = subprocess.run(
            [sys.executable, "-I", temp_path],
            cwd=workdir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout_seconds,
            env=env,
        )
        duration = time.perf_counter() - start
        success = result.returncode == 0 and "SUCCESS" in result.stdout
        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "timed_out": False,
            "duration_seconds": round(duration, 3),
        }
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - start
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return {
            "success": False,
            "stdout": stdout,
            "stderr": stderr or f"Script timed out after {timeout_seconds} seconds",
            "exit_code": 124,
            "timed_out": True,
            "duration_seconds": round(duration, 3),
        }
    finally:
        if temp_path:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except OSError:
                pass
        if workdir:
            try:
                shutil.rmtree(workdir, ignore_errors=True)
            except OSError:
                pass

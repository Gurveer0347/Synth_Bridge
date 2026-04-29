import os
import unittest

from ali_sandbox.demo_scripts import build_initial_demo_code
from ali_sandbox.api import create_app
from ali_sandbox.errors import classify_error
from ali_sandbox.self_healing import run_self_healing_bridge
from ali_sandbox.sandbox import run_code


class SandboxTests(unittest.TestCase):
    def test_run_code_captures_success_stdout_and_exit_code(self):
        result = run_code("print('Fetching lead')\nprint('SUCCESS')", timeout_seconds=2)

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertFalse(result["timed_out"])
        self.assertIn("SUCCESS", result["stdout"])
        self.assertEqual(result["stderr"], "")

    def test_run_code_captures_traceback_for_broken_script(self):
        result = run_code("raise ValueError('Something went wrong')", timeout_seconds=2)

        self.assertFalse(result["success"])
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("ValueError", result["stderr"])

    def test_run_code_times_out_infinite_loop(self):
        result = run_code("while True:\n    pass", timeout_seconds=1)

        self.assertFalse(result["success"])
        self.assertTrue(result["timed_out"])
        self.assertNotEqual(result["exit_code"], 0)
        self.assertIn("timed out", result["stderr"].lower())

    def test_run_code_blocks_obviously_destructive_code(self):
        result = run_code("import shutil\nshutil.rmtree('important')", timeout_seconds=2)

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 126)
        self.assertIn("Blocked unsafe generated code", result["stderr"])

    def test_run_code_passes_hubspot_token_to_child_process(self):
        old_token = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN")
        os.environ["HUBSPOT_PRIVATE_APP_TOKEN"] = "dummy-token-for-test"
        try:
            result = run_code(
                "import os\nprint(os.environ.get('HUBSPOT_PRIVATE_APP_TOKEN'))\nprint('SUCCESS')",
                timeout_seconds=2,
            )

            self.assertTrue(result["success"])
            self.assertIn("dummy-token-for-test", result["stdout"])
        finally:
            if old_token is None:
                os.environ.pop("HUBSPOT_PRIVATE_APP_TOKEN", None)
            else:
                os.environ["HUBSPOT_PRIVATE_APP_TOKEN"] = old_token


class ErrorClassifierTests(unittest.TestCase):
    def test_classify_error_extracts_type_message_and_line_number(self):
        stderr = """Traceback (most recent call last):
  File "C:\\Temp\\ali_generated.py", line 7, in <module>
    lead = data["email"]
KeyError: 'email'
"""

        error = classify_error(stderr, exit_code=1)

        self.assertEqual(error["error_type"], "KeyError")
        self.assertEqual(error["error_message"], "'email'")
        self.assertEqual(error["line_number"], 7)
        self.assertIn("field", error["likely_cause"].lower())
        self.assertIn("field mapping", error["fix_hint"].lower())

    def test_classify_error_handles_timeout(self):
        error = classify_error("Script timed out after 1 seconds", exit_code=124, timed_out=True)

        self.assertEqual(error["error_type"], "TimeoutExpired")
        self.assertIsNone(error["line_number"])
        self.assertIn("ran too long", error["likely_cause"])


class SelfHealingTests(unittest.TestCase):
    def test_bad_endpoint_demo_repairs_on_second_attempt(self):
        initial_code = build_initial_demo_code("bad_endpoint", mode="safe_demo")

        result = run_self_healing_bridge(initial_code, mode="safe_demo", timeout_seconds=2)

        self.assertTrue(result["success"])
        self.assertEqual(result["stage"], "done")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertFalse(result["attempts"][0]["success"])
        self.assertTrue(result["attempts"][1]["success"])
        self.assertIn("SUCCESS", result["output"])
        self.assertIn("Discord alert payload", result["output"])

    def test_wrong_field_demo_repairs_on_second_attempt(self):
        initial_code = build_initial_demo_code("wrong_field", mode="safe_demo")

        result = run_self_healing_bridge(initial_code, mode="safe_demo", timeout_seconds=2)

        self.assertTrue(result["success"])
        self.assertEqual(len(result["attempts"]), 2)
        self.assertEqual(result["attempts"][0]["error_log"]["error_type"], "KeyError")

    def test_duplicate_code_is_detected_without_rerunning_same_script(self):
        initial_code = "raise ValueError('same broken code')"

        def duplicate_repair(code, error_log, attempt, mode):
            return code

        result = run_self_healing_bridge(
            initial_code,
            mode="safe_demo",
            max_retries=2,
            timeout_seconds=2,
            repair_func=duplicate_repair,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["stage"], "failed")
        self.assertEqual(len(result["attempts"]), 2)
        self.assertTrue(result["attempts"][1]["duplicate_code"])
        self.assertIn("identical code", result["attempts"][1]["stderr"])

    def test_discord_live_without_webhook_falls_back_without_crashing(self):
        old_webhook = os.environ.pop("DISCORD_WEBHOOK_URL", None)
        try:
            initial_code = build_initial_demo_code("missing_auth", mode="discord_live")

            result = run_self_healing_bridge(initial_code, mode="discord_live", timeout_seconds=2)

            self.assertTrue(result["success"])
            self.assertIn("DISCORD_WEBHOOK_URL not set", result["output"])
            self.assertIn("SUCCESS", result["output"])
        finally:
            if old_webhook is not None:
                os.environ["DISCORD_WEBHOOK_URL"] = old_webhook

    def test_full_live_requires_real_credentials_and_uses_no_simulated_lead(self):
        old_hubspot = os.environ.pop("HUBSPOT_PRIVATE_APP_TOKEN", None)
        old_discord = os.environ.pop("DISCORD_WEBHOOK_URL", None)
        try:
            initial_code = build_initial_demo_code("bad_endpoint", mode="full_live")

            result = run_self_healing_bridge(
                initial_code,
                mode="full_live",
                max_retries=1,
                timeout_seconds=2,
            )

            self.assertFalse(result["success"])
            self.assertIn("HUBSPOT_PRIVATE_APP_TOKEN", result["error"])
            self.assertIn("/crm/objects/2026-03/contacts/search", result["generated_code"])
            self.assertNotIn("simulated HubSpot lead", result["generated_code"])
            self.assertNotIn("Aarav", result["generated_code"])
        finally:
            if old_hubspot is not None:
                os.environ["HUBSPOT_PRIVATE_APP_TOKEN"] = old_hubspot
            if old_discord is not None:
                os.environ["DISCORD_WEBHOOK_URL"] = old_discord

    def test_flask_run_endpoint_accepts_full_live_mode(self):
        old_hubspot = os.environ.pop("HUBSPOT_PRIVATE_APP_TOKEN", None)
        old_discord = os.environ.pop("DISCORD_WEBHOOK_URL", None)
        try:
            client = create_app().test_client()

            response = client.post(
                "/run",
                json={"mode": "full_live", "demo_failure": "bad_endpoint", "max_retries": 1, "timeout_seconds": 2},
            )
            payload = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertFalse(payload["success"])
            self.assertEqual(payload["stage"], "failed")
            self.assertIn("/crm/objects/2026-03/contacts/search", payload["generated_code"])
        finally:
            if old_hubspot is not None:
                os.environ["HUBSPOT_PRIVATE_APP_TOKEN"] = old_hubspot
            if old_discord is not None:
                os.environ["DISCORD_WEBHOOK_URL"] = old_discord


if __name__ == "__main__":
    unittest.main()

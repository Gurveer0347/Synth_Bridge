import os
import unittest

from ali_sandbox.api import create_app


class FrontendContractTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health_response_allows_vite_frontend_origin(self):
        response = self.client.get("/health", headers={"Origin": "http://localhost:5173"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:5173")
        self.assertIn("Content-Type", response.headers["Access-Control-Allow-Headers"])
        self.assertIn("POST", response.headers["Access-Control-Allow-Methods"])

    def test_run_response_keeps_attempts_list_and_adds_attempts_count(self):
        old_webhook = os.environ.pop("DISCORD_WEBHOOK_URL", None)
        try:
            response = self.client.post(
                "/run",
                json={
                    "mode": "safe_demo",
                    "demo_failure": "wrong_field",
                    "timeout_seconds": 2,
                },
            )
            payload = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertTrue(payload["success"])
            self.assertIsInstance(payload["attempts"], list)
            self.assertEqual(payload["attempts_count"], len(payload["attempts"]))
            self.assertEqual(payload["stage"], "done")
        finally:
            if old_webhook is not None:
                os.environ["DISCORD_WEBHOOK_URL"] = old_webhook

    def test_run_options_preflight_returns_cors_headers(self):
        response = self.client.open(
            "/run",
            method="OPTIONS",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "http://localhost:5173")


if __name__ == "__main__":
    unittest.main()

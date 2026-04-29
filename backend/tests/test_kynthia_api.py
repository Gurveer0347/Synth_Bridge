"""KYNTHIA backend API tests."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # Fall back to reading frontend .env directly
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                if line.startswith("REACT_APP_BACKEND_URL="):
                    BASE_URL = line.split("=", 1)[1].strip().rstrip("/")
                    break
    except Exception:
        pass


@pytest.fixture(scope="module")
def api_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ============ Health & Root ============
class TestHealth:
    def test_root(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "KYNTHIA" in data.get("message", "")

    def test_health(self, api_client):
        r = api_client.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "healthy"
        assert "time" in data


# ============ Quote Creation ============
class TestQuoteCreate:
    def test_create_valid_echo(self, api_client):
        payload = {
            "name": "TEST_Alice",
            "email": "test_alice@example.com",
            "company": "TEST Corp",
            "tier_interest": "echo",
            "budget": "$5k",
            "message": "We want a simple website.",
        }
        r = api_client.post(f"{BASE_URL}/api/quote", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data and len(data["id"]) >= 16
        assert data["name"] == payload["name"]
        assert data["email"] == payload["email"]
        assert data["tier_interest"] == "echo"
        assert data["email_sent"] is False  # Resend keys empty -> no-op
        assert "_id" not in data

    def test_create_valid_unsure_optional_fields(self, api_client):
        payload = {
            "name": "TEST_Bob",
            "email": "test_bob@example.com",
            "tier_interest": "unsure",
            "message": "Need advice.",
        }
        r = api_client.post(f"{BASE_URL}/api/quote", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["company"] == ""
        assert data["budget"] == ""
        assert data["email_sent"] is False

    def test_create_valid_cosmos(self, api_client):
        payload = {
            "name": "TEST_Carol",
            "email": "test_carol@example.com",
            "tier_interest": "cosmos",
            "message": "We want flagship cosmos site.",
        }
        r = api_client.post(f"{BASE_URL}/api/quote", json=payload)
        assert r.status_code == 200
        assert r.json()["tier_interest"] == "cosmos"

    # --- Validation ---
    def test_missing_name(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/quote", json={
            "email": "test@example.com",
            "tier_interest": "echo",
            "message": "hi",
        })
        assert r.status_code == 422

    def test_invalid_email(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/quote", json={
            "name": "TEST_x",
            "email": "not-an-email",
            "tier_interest": "echo",
            "message": "hi",
        })
        assert r.status_code == 422

    def test_invalid_tier_enum(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/quote", json={
            "name": "TEST_x",
            "email": "test_x@example.com",
            "tier_interest": "platinum",
            "message": "hi",
        })
        assert r.status_code == 422

    def test_empty_message(self, api_client):
        r = api_client.post(f"{BASE_URL}/api/quote", json={
            "name": "TEST_x",
            "email": "test_x@example.com",
            "tier_interest": "echo",
            "message": "",
        })
        assert r.status_code == 422


# ============ List Quotes ============
class TestQuoteList:
    def test_list_returns_list_no_objectid_sorted(self, api_client):
        # Seed two
        for i in range(2):
            api_client.post(f"{BASE_URL}/api/quote", json={
                "name": f"TEST_seed_{i}",
                "email": f"test_seed_{i}@example.com",
                "tier_interest": "aether",
                "message": f"seed message {i}",
            })
        r = api_client.get(f"{BASE_URL}/api/quotes")
        assert r.status_code == 200
        rows = r.json()
        assert isinstance(rows, list)
        assert len(rows) >= 2
        for row in rows:
            assert "_id" not in row
            assert "id" in row
            assert "created_at" in row
            assert row["tier_interest"] in {"echo", "aether", "cosmos", "unsure"}

        # sorted desc by created_at
        ts = [row["created_at"] for row in rows]
        assert ts == sorted(ts, reverse=True)

    def test_create_then_appears_in_list(self, api_client):
        unique_email = "test_persist_check@example.com"
        cr = api_client.post(f"{BASE_URL}/api/quote", json={
            "name": "TEST_persist",
            "email": unique_email,
            "tier_interest": "aether",
            "message": "persistence test",
        })
        assert cr.status_code == 200
        qid = cr.json()["id"]

        r = api_client.get(f"{BASE_URL}/api/quotes")
        assert r.status_code == 200
        ids = [q["id"] for q in r.json()]
        assert qid in ids

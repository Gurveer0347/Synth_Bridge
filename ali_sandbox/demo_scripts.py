from textwrap import dedent


VALID_FAILURES = {"bad_endpoint", "missing_auth", "wrong_field", "syntax_error", "timeout"}
VALID_MODES = {"safe_demo", "discord_live", "full_live"}


def _lead_literal() -> str:
    return "{'first_name': 'Aarav', 'last_name': 'Mehta', 'email': 'aarav@example.com', 'company': 'Trae Labs'}"


def success_code(mode: str = "safe_demo") -> str:
    mode = mode if mode in VALID_MODES else "safe_demo"
    if mode == "full_live":
        return full_live_code()

    if mode == "discord_live":
        live_block = dedent(
            """
            webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
            if webhook_url:
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    webhook_url,
                    data=data,
                    headers={'Content-Type': 'application/json'},
                    method='POST',
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    print(f"Discord webhook status: {response.status}")
            else:
                print("DISCORD_WEBHOOK_URL not set; fallback payload only")
            """
        ).strip()
    else:
        live_block = 'print("safe_demo mode; payload printed instead of sent")'

    base_code = dedent(
        f"""
        import json
        import os
        import urllib.request

        lead = {_lead_literal()}
        payload = {{
            "content": (
                "New HubSpot lead: "
                f"{{lead['first_name']}} {{lead['last_name']}} "
                f"<{{lead['email']}}> from {{lead['company']}}"
            )
        }}

        print("Fetched simulated HubSpot lead")
        print("Discord alert payload:")
        print(json.dumps(payload, indent=2))
        """
    ).strip()
    return f"{base_code}\n{live_block}\nprint(\"SUCCESS\")"


def full_live_code() -> str:
    return dedent(
        """
        import json
        import os
        import urllib.error
        import urllib.request

        hubspot_token = os.environ.get("HUBSPOT_PRIVATE_APP_TOKEN") or os.environ.get("HUBSPOT_ACCESS_TOKEN")
        discord_webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        missing = []
        if not hubspot_token:
            missing.append("HUBSPOT_PRIVATE_APP_TOKEN")
        if not discord_webhook_url:
            missing.append("DISCORD_WEBHOOK_URL")
        if missing:
            raise RuntimeError("full_live requires environment variables: " + ", ".join(missing))

        search_url = "https://api.hubapi.com/crm/objects/2026-03/contacts/search"
        search_body = {
            "limit": 1,
            "properties": ["firstname", "lastname", "email", "company", "createdate"],
            "sorts": [{"propertyName": "createdate", "direction": "DESCENDING"}],
        }
        search_request = urllib.request.Request(
            search_url,
            data=json.dumps(search_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {hubspot_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(search_request, timeout=15) as response:
                hubspot_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HubSpot request failed with HTTP {exc.code}: {details}") from exc

        contacts = hubspot_payload.get("results", [])
        if not contacts:
            raise RuntimeError("HubSpot returned no contacts. Create one contact before running full_live.")

        properties = contacts[0].get("properties", {})
        first_name = properties.get("firstname") or "Unknown"
        last_name = properties.get("lastname") or ""
        email = properties.get("email") or "no-email"
        company = properties.get("company") or "Unknown company"
        createdate = properties.get("createdate") or "unknown createdate"

        discord_payload = {
            "content": (
                "New live HubSpot contact: "
                f"{first_name} {last_name} <{email}> from {company}. "
                f"Created at {createdate}."
            )
        }
        discord_request = urllib.request.Request(
            discord_webhook_url,
            data=json.dumps(discord_payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(discord_request, timeout=15) as response:
                print(f"Discord webhook status: {response.status}")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Discord webhook failed with HTTP {exc.code}: {details}") from exc

        print("Fetched newest HubSpot contact via live API")
        print("Sent live Discord alert")
        print(json.dumps(discord_payload, indent=2))
        print("SUCCESS")
        """
    ).strip()


def build_initial_demo_code(demo_failure: str = "bad_endpoint", mode: str = "safe_demo") -> str:
    demo_failure = demo_failure if demo_failure in VALID_FAILURES else "bad_endpoint"
    mode = mode if mode in VALID_MODES else "safe_demo"
    if mode == "full_live":
        return full_live_code()

    if demo_failure == "bad_endpoint":
        return dedent(
            """
            import urllib.request

            print("Fetching new HubSpot lead...")
            raise ConnectionError("404 Not Found: https://api.hubspot.com/crm/v99/leads")
            """
        ).strip()
    if demo_failure == "missing_auth":
        return dedent(
            """
            print("Fetching new HubSpot lead...")
            raise PermissionError("401 Unauthorized: missing Bearer token")
            """
        ).strip()
    if demo_failure == "wrong_field":
        return dedent(
            f"""
            lead = {_lead_literal()}
            print("Formatting Discord alert...")
            print(lead["mail"])
            """
        ).strip()
    if demo_failure == "syntax_error":
        return "print('Generating bridge'\nprint('SUCCESS')"
    if demo_failure == "timeout":
        return "while True:\n    pass"

    return success_code(mode)

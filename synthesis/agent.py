"""
Synthesis Module — The Brain of ALI

This is the 4-node LangGraph pipeline:
  Node 1: Schema Extractor  — pulls field names from API docs via LLM
  Node 2: Field Mapper       — maps HubSpot fields → Discord fields
  Node 3: Code Generator     — writes Python integration script
  Node 4: Pre-Validator      — sanity-checks the generated code

Supports two modes:
  - LIVE mode:  Uses MiniMax M2.7 API (requires MINIMAX_API_KEY)
  - DEMO mode:  Uses realistic pre-built responses (no API key needed)

This is Stage 2 of the ALI pipeline.
"""

import os
import json
import requests
from langgraph.graph import StateGraph
from dotenv import load_dotenv

# Add parent dir to path so we can import state
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from state import ALIState

load_dotenv()


# ─────────────────────────────────────────────
# Standalone Doc Reader (replaces ingestion module)
# ─────────────────────────────────────────────
# TODO: Replace this with Antarjot's RAG engine (ingestion.ingest.query_docs)
#       once it's ready. For now we just read the raw docs files directly.

def query_docs(question: str, source_name: str) -> str:
    """Standalone fallback — reads raw doc file instead of querying ChromaDB.
    
    This is a temporary stub. When Antarjot's ingestion module is plugged in,
    this function gets replaced with the real RAG-powered query_docs.
    """
    doc_map = {
        "hubspot": os.path.join(os.path.dirname(__file__), "..", "docs", "hubspot_api.txt"),
        "discord": os.path.join(os.path.dirname(__file__), "..", "docs", "discord_api.txt"),
    }
    path = doc_map.get(source_name, "")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"[No docs found for {source_name}]"


# ─────────────────────────────────────────────
# Mode Detection
# ─────────────────────────────────────────────

def is_demo_mode() -> bool:
    """Check if we should run in demo mode (no real API key)."""
    key = os.environ.get("NVIDIA_NIM_API_KEY", "")
    return key == "" or key == "your_key_here" or key.startswith("your_")


# ─────────────────────────────────────────────
# LLM Helper — MiniMax M2.7 via NVIDIA NIM
# ─────────────────────────────────────────────

def call_minimax(system_prompt: str, user_prompt: str) -> str:
    """Call MiniMax M2.7 via NVIDIA NIM API.

    Uses the OpenAI-compatible NIM endpoint at integrate.api.nvidia.com.
    Returns the raw text response from the model.
    Includes error handling so one bad API call doesn't crash the pipeline.
    """
    import time

    api_key = os.environ.get("NVIDIA_NIM_API_KEY", "")
    if not api_key or api_key.startswith("your_"):
        raise RuntimeError("NVIDIA_NIM_API_KEY is not set - cannot make LIVE calls")

    for attempt in range(3):
        try:
            response = requests.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta/llama-3.1-70b-instruct",
                    "temperature": 0.2,
                    "top_p": 0.95,
                    "max_tokens": 2048,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt}
                    ]
                },
                timeout=120  # Increased timeout for complex prompts
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            print(f"  [!] NIM timeout (attempt {attempt + 1}/3), retrying...")
            time.sleep(2)
        except requests.exceptions.HTTPError as e:
            print(f"  [!] NIM HTTP error: {e}")
            if response.status_code == 429:  # Rate limited
                print("  [!] Rate limited - waiting 5s...")
                time.sleep(5)
            else:
                raise
        except (KeyError, IndexError) as e:
            print(f"  [!] Unexpected API response format: {e}")
            print(f"  [!] Raw response: {response.text[:300]}")
            raise RuntimeError(f"NIM returned unexpected format: {e}")

    raise RuntimeError("NVIDIA NIM API failed after 3 attempts")


# ─────────────────────────────────────────────
# DEMO Responses (used when no API key is set)
# ─────────────────────────────────────────────

DEMO_HUBSPOT_FIELDS = [
    "1. firstname",
    "2. lastname",
    "3. email",
    "4. phone",
    "5. company",
    "6. jobtitle",
    "7. lifecyclestage",
    "8. hs_lead_status",
    "9. createdate",
    "10. lastmodifieddate",
]

DEMO_DISCORD_FIELDS = [
    "1. content",
    "2. username",
    "3. avatar_url",
    "4. embeds",
    "5. title",
    "6. description",
    "7. color",
    "8. fields",
    "9. name",
    "10. value",
]

DEMO_FIELD_MAPPING = {
    "firstname": "fields[0].value",
    "lastname": "fields[1].value",
    "email": "fields[2].value",
    "phone": "fields[3].value",
    "company": "fields[4].value",
    "jobtitle": "description",
    "lifecyclestage": "fields[5].value",
    "createdate": "timestamp",
}

DEMO_GENERATED_CODE = '''import os
import requests

# ── Config ──
HUBSPOT_API_KEY = os.environ.get("HUBSPOT_API_KEY", "demo-key")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/demo/demo")

DEMO_MODE = HUBSPOT_API_KEY == "demo-key" or HUBSPOT_API_KEY.startswith("your_")


def fetch_latest_hubspot_contact():
    """Fetch the most recently created contact from HubSpot CRM."""
    if DEMO_MODE:
        print("[DEMO] Using mock HubSpot data")
        return {
            "firstname": "Jane",
            "lastname": "Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-555-0123",
            "company": "Acme Corp",
            "jobtitle": "Product Manager",
            "lifecyclestage": "lead",
            "createdate": "2025-04-28T10:30:00.000Z",
        }

    url = "https://api.hubapi.com/crm/v3/objects/contacts"
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    params = {
        "limit": 1,
        "sorts": "-createdate",
        "properties": "firstname,lastname,email,phone,company,jobtitle,lifecyclestage,createdate",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    results = response.json().get("results", [])
    if not results:
        raise Exception("No contacts found in HubSpot")
    return results[0]["properties"]


def send_discord_alert(contact):
    """Send a rich embed notification to Discord with contact details."""
    payload = {
        "username": "ALI Bot",
        "embeds": [
            {
                "title": "New HubSpot Lead",
                "description": f"{contact.get('jobtitle', 'N/A')} just entered the CRM",
                "color": 5814783,
                "fields": [
                    {"name": "Name", "value": f"{contact.get('firstname', '')} {contact.get('lastname', '')}", "inline": True},
                    {"name": "Email", "value": contact.get("email", "N/A"), "inline": True},
                    {"name": "Phone", "value": contact.get("phone", "N/A"), "inline": True},
                    {"name": "Company", "value": contact.get("company", "N/A"), "inline": True},
                    {"name": "Stage", "value": contact.get("lifecyclestage", "N/A"), "inline": True},
                ],
                "footer": {"text": "ALI - Autonomous Integration Layer"},
            }
        ],
    }

    if DEMO_MODE:
        print("[DEMO] Discord webhook payload:")
        print(f"  Title: {payload['embeds'][0]['title']}")
        for field in payload["embeds"][0]["fields"]:
            print(f"  {field['name']}: {field['value']}")
        print("SUCCESS")
        return

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in (200, 204):
        print("SUCCESS")
    else:
        print(f"FAILURE: Discord returned {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    try:
        contact = fetch_latest_hubspot_contact()
        print(f"Fetched contact: {contact.get('firstname', '')} {contact.get('lastname', '')}")
        send_discord_alert(contact)
    except Exception as e:
        print(f"FAILURE: {e}")
'''


# ─────────────────────────────────────────────
# NODE 1 — Schema Extractor
# ─────────────────────────────────────────────

def schema_extractor(state: ALIState) -> ALIState:
    """Extract field names from both HubSpot and Discord API docs.

    Uses RAG to pull relevant doc chunks, then asks the LLM
    to extract a clean list of field names.
    """
    demo = is_demo_mode()

    if demo:
        print("  [i] Running in DEMO mode (no API key)")
        state["hubspot_chunks"] = query_docs("list all available fields and parameters", "hubspot")
        state["discord_chunks"] = query_docs("list all available fields and parameters", "discord")
        state["hubspot_fields"] = DEMO_HUBSPOT_FIELDS
        state["discord_fields"] = DEMO_DISCORD_FIELDS
        print("[Synthesis] Node 1 complete — fields extracted (DEMO)")
        return state

    for api in ["hubspot", "discord"]:
        chunks = query_docs("list all available fields and parameters", api)
        result = call_minimax(
            system_prompt=(
                "You are an API documentation expert. "
                "Your only job is to extract field names from API documentation. "
                "Output a clean numbered list of field names only. "
                "No descriptions, no examples, no markdown."
            ),
            user_prompt=(
                f"Here is the {api} API documentation:\n{chunks}\n"
                "List all field names."
            )
        )
        if api == "hubspot":
            state["hubspot_fields"] = result.strip().split("\n")
            state["hubspot_chunks"] = chunks
        else:
            state["discord_fields"] = result.strip().split("\n")
            state["discord_chunks"] = chunks

    print("[Synthesis] Node 1 complete — fields extracted")
    return state


# ─────────────────────────────────────────────
# NODE 2 — Field Mapper
# ─────────────────────────────────────────────

def field_mapper(state: ALIState) -> ALIState:
    """Map HubSpot fields to Discord fields based on semantic similarity.

    Asks the LLM to produce a JSON mapping of field-to-field relationships.
    """
    demo = is_demo_mode()

    if demo:
        state["field_mapping"] = DEMO_FIELD_MAPPING
        print("[Synthesis] Node 2 complete — fields mapped (DEMO)")
        return state

    raw = call_minimax(
        system_prompt=(
            "You are an API integration expert connecting HubSpot CRM to Discord. "
            "Given fields from both APIs, map which fields serve the same purpose. "
            "Goal: when a new HubSpot lead is created, send a Discord alert. "
            "Output ONLY a valid JSON object. Keys = HubSpot fields, values = Discord fields. "
            "No explanation. No markdown. No backticks. Just raw JSON."
        ),
        user_prompt=(
            f"HubSpot fields:\n{chr(10).join(state['hubspot_fields'])}\n\n"
            f"Discord fields:\n{chr(10).join(state['discord_fields'])}\n\n"
            "Create the field mapping JSON."
        )
    )

    # Clean and parse JSON safely
    start = raw.find("{")
    end = raw.rfind("}") + 1
    cleaned = raw[start:end]
    try:
        state["field_mapping"] = json.loads(cleaned)
        print("[Synthesis] Node 2 complete — fields mapped")
    except json.JSONDecodeError:
        state["field_mapping"] = {}
        state["error_log"] = "Node 2 JSON parse failed"
        print("[Synthesis] Node 2 WARNING — JSON parse failed")

    return state


# ─────────────────────────────────────────────
# NODE 3 — Code Generator
# ─────────────────────────────────────────────

def code_generator(state: ALIState) -> ALIState:
    """Generate a Python integration script based on the field mapping.

    If a previous attempt failed, includes the error in the prompt
    so the LLM can self-heal and fix the issue.
    """
    demo = is_demo_mode()

    if demo:
        state["generated_code"] = DEMO_GENERATED_CODE
        print("[Synthesis] Node 3 complete — code generated (DEMO)")
        return state

    error_context = ""
    if state.get("error_log") and state.get("generated_code"):
        error_context = (
            f"This script failed:\n{state['generated_code']}\n"
            f"Error:\n{state['error_log']}\nFix it."
        )

    auth_chunks = query_docs("authentication bearer token header", "hubspot")
    webhook_chunks = query_docs("webhook payload format embeds", "discord")

    raw = call_minimax(
        system_prompt=(
            "You are a Python developer writing API integration scripts. "
            "You output ONLY raw Python code. "
            "No markdown. No backticks. No explanations. No comments at the top. "
            "The first character of your response must be the letter i (import)."
        ),
        user_prompt=(
            f"{error_context}\n"
            "Write a Python script that:\n"
            "1. Fetches the latest contact from HubSpot\n"
            "2. Sends a Discord webhook notification with contact details\n\n"
            f"HubSpot auth info:\n{auth_chunks}\n\n"
            f"Discord webhook format:\n{webhook_chunks}\n\n"
            f"Field mapping:\n{json.dumps(state['field_mapping'], indent=2)}\n\n"
            "Requirements:\n"
            "- Use requests library only\n"
            "- Use environment variables for all API keys\n"
            "- Print SUCCESS or FAILURE at the end\n"
            "Output raw Python code only."
        )
    )

    # Strip any backtick wrappers the LLM might add
    lines = raw.split("\n")
    cleaned_lines = [l for l in lines if not l.strip().startswith("```")]
    code = "\n".join(cleaned_lines)

    # Find the first import statement and trim everything before it
    first_import = next(
        (i for i, l in enumerate(code.split("\n"))
         if l.startswith("import") or l.startswith("from")),
        0
    )
    state["generated_code"] = "\n".join(code.split("\n")[first_import:])

    print("[Synthesis] Node 3 complete — code generated")
    return state


# ─────────────────────────────────────────────
# NODE 4 — Pre-Validator
# ─────────────────────────────────────────────

def pre_validator(state: ALIState) -> ALIState:
    """Run basic sanity checks on the generated code before execution.

    Checks for: imports, requests usage, HubSpot/Discord references,
    and minimum code length.
    """
    code = state.get("generated_code", "")
    checks = [
        code.startswith("import") or "import" in code[:100],
        "requests" in code,
        "hubspot" in code.lower(),
        "discord" in code.lower() or "webhook" in code.lower(),
        len(code.splitlines()) > 10
    ]
    state["validation_passed"] = all(checks)

    if not state["validation_passed"]:
        state["error_log"] = "Pre-validation failed: code looks incomplete"
        print("[Synthesis] Node 4 WARNING — validation failed")
    else:
        print("[Synthesis] Node 4 complete — validation passed")

    return state


# ─────────────────────────────────────────────
# Build the LangGraph Pipeline
# ─────────────────────────────────────────────

def build_graph():
    """Compile the 4-node LangGraph pipeline and return the runnable app."""
    graph = StateGraph(ALIState)

    graph.add_node("schema_extractor", schema_extractor)
    graph.add_node("field_mapper",      field_mapper)
    graph.add_node("code_generator",    code_generator)
    graph.add_node("pre_validator",     pre_validator)

    graph.set_entry_point("schema_extractor")
    graph.add_edge("schema_extractor", "field_mapper")
    graph.add_edge("field_mapper",     "code_generator")
    graph.add_edge("code_generator",   "pre_validator")
    graph.set_finish_point("pre_validator")

    return graph.compile()


# ─────────────────────────────────────────────
# Public Interface — What teammates call
# ─────────────────────────────────────────────

MAX_RETRIES = 3


def run_synthesis(hubspot_doc_path: str = None, discord_doc_path: str = None) -> dict:
    """Run the full synthesis pipeline with self-healing retry loop.

    This is the MAIN ENTRY POINT for the synthesis engine.
    Teammates call this function — it handles everything internally.

    Args:
        hubspot_doc_path: Optional path to HubSpot API docs.
                          Defaults to docs/hubspot_api.txt
        discord_doc_path: Optional path to Discord API docs.
                          Defaults to docs/discord_api.txt

    Returns:
        dict with keys:
            - generated_code (str): The Python integration script
            - field_mapping (dict): HubSpot→Discord field mapping
            - validation_passed (bool): Whether pre-validation passed
            - error_log (str): Error details if something failed
            - retry_count (int): How many attempts were needed
    """
    print("=" * 60)
    print("  ALI Synthesis Engine - The Brain")
    print("=" * 60)

    mode = "DEMO" if is_demo_mode() else "LIVE"
    print(f"  Mode: {mode}")
    print(f"  Model: Llama 3.1 70B (via NIM)")
    print("=" * 60)

    # Build the 4-node graph
    graph = build_graph()

    # Initialize empty state
    state = ALIState(
        hubspot_chunks="",
        discord_chunks="",
        hubspot_fields=[],
        discord_fields=[],
        field_mapping={},
        generated_code="",
        validation_passed=False,
        error_log="",
        retry_count=0
    )

    # ── Self-healing retry loop ──
    for attempt in range(MAX_RETRIES):
        state["retry_count"] = attempt
        print(f"\n{'-' * 40}")
        print(f"  Attempt {attempt + 1}/{MAX_RETRIES}")
        print(f"{'-' * 40}")

        # Run the 4-node LangGraph pipeline
        try:
            state = graph.invoke(state)
        except Exception as e:
            print(f"  [X] Pipeline crashed: {e}")
            state["error_log"] = str(e)
            continue

        # Check if pre-validation passed
        if state.get("validation_passed"):
            print(f"\n[OK] Synthesis complete on attempt {attempt + 1}!")
            print(f"  Generated code: {len(state['generated_code'])} chars")
            print(f"  Field mappings: {len(state.get('field_mapping', {}))} pairs")
            return state

        # If validation failed, the error_log is already set by pre_validator.
        # On next iteration, code_generator will read error_log and self-heal.
        print(f"  [!] Validation failed, will retry with error context...")

    print(f"\n[FAIL] All {MAX_RETRIES} attempts exhausted.")
    return state


# ─────────────────────────────────────────────
# Standalone Runner — python synthesis/agent.py
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Fix Windows console encoding (cp1252 can't handle LLM unicode output)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("\nRunning synthesis engine standalone...\n")
    result = run_synthesis()

    print("\n" + "=" * 60)
    print("  RESULTS")
    print("=" * 60)
    print(f"  Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
    print(f"  Retries used: {result['retry_count']}")
    print(f"  Error log: {result.get('error_log', 'None')}")

    if result.get("field_mapping"):
        print("\n  Field Mapping:")
        for k, v in result["field_mapping"].items():
            print(f"    HubSpot:{k}  ->  Discord:{v}")

    if result.get("generated_code"):
        print("\n  Generated Code (first 30 lines):")
        lines = result["generated_code"].split("\n")[:30]
        for i, line in enumerate(lines, 1):
            print(f"    {i:3d} | {line}")

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60)

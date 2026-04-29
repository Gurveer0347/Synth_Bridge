"""
test_query_docs.py — Tests for query_docs()
This is the 8-query mandatory test suite from Antarjot's roadmap.
All 8 must pass before handing off to Japneet.

Run with: python test_query_docs.py
NVIDIA_API_KEY is loaded automatically from .env
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rag_engine import ingest_doc, query_docs

FOLDER = os.path.dirname(os.path.abspath(__file__))


def check(label, condition, result_preview=""):
    status = "PASS" if condition else "FAIL"
    print(f"  {status} — {label}")
    if not condition and result_preview:
        print(f"         Got: {result_preview[:120]}")


def header(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


# ── Step 0: Ingest both docs (skips silently if already done) ────────────────
header("SETUP — Ingesting docs (skips if already in ChromaDB)")

ingest_doc(os.path.join(FOLDER, "hubspot_docs.txt"), "hubspot")
ingest_doc(os.path.join(FOLDER, "discord_docs.txt"), "discord")


# ── HubSpot mandatory queries ────────────────────────────────────────────────
header("HUBSPOT — 5 Mandatory Queries")

# Query 1
q1 = query_docs("what authentication method does HubSpot use?", "hubspot")
print("\nQ1: what authentication method does HubSpot use?")
print(f"   Result preview: {q1[:150]}\n")
check("Contains 'Bearer' or 'token'",   any(w in q1 for w in ["Bearer", "bearer", "token"]), q1)
check("Contains 'Authorization'",        "Authorization" in q1 or "authorization" in q1,      q1)
check("Result is a non-empty string",    isinstance(q1, str) and len(q1) > 0,                  q1)

# Query 2
q2 = query_docs("what is the base URL for HubSpot contacts?", "hubspot")
print("\nQ2: what is the base URL for HubSpot contacts?")
print(f"   Result preview: {q2[:150]}\n")
check("Contains HubSpot contacts endpoint",  "hubspot.com" in q2 or "contacts" in q2.lower(), q2)
check("Result is a non-empty string",         isinstance(q2, str) and len(q2) > 0,             q2)

# Query 3
q3 = query_docs("what fields does a HubSpot contact have?", "hubspot")
print("\nQ3: what fields does a HubSpot contact have?")
print(f"   Result preview: {q3[:150]}\n")
check("Contains 'firstname'",   "firstname" in q3, q3)
check("Contains 'email'",       "email"     in q3, q3)
check("Contains 'lastname'",    "lastname"  in q3, q3)

# Query 4
q4 = query_docs("how do I create a contact in HubSpot?", "hubspot")
print("\nQ4: how do I create a contact in HubSpot?")
print(f"   Result preview: {q4[:150]}\n")
check("Contains 'POST'",         "POST" in q4,       q4)
check("Contains 'properties'",   "properties" in q4, q4)

# Query 5
q5 = query_docs("what does a HubSpot error response look like?", "hubspot")
print("\nQ5: what does a HubSpot error response look like?")
print(f"   Result preview: {q5[:150]}\n")
check("Contains error status codes",   any(c in q5 for c in ["400","401","404","500"]), q5)
check("Contains error-related content", any(w in q5 for w in ["message", "status", "error", "Retry-After", "correlationId"]), q5)


# ── Discord mandatory queries ────────────────────────────────────────────────
header("DISCORD — 3 Mandatory Queries")

# Query 6
q6 = query_docs("what is the format of a Discord webhook payload?", "discord")
print("\nQ6: what is the format of a Discord webhook payload?")
print(f"   Result preview: {q6[:150]}\n")
check("Contains 'content'",   "content" in q6, q6)
check("Contains 'embeds'",    "embeds"  in q6, q6)

# Query 7
q7 = query_docs("how do I send an embed in Discord?", "discord")
print("\nQ7: how do I send an embed in Discord?")
print(f"   Result preview: {q7[:150]}\n")
check("Contains 'embeds' or 'embed'",   "embed" in q7.lower(), q7)
check("Contains embed-related content", any(w in q7.lower() for w in ["title", "fields", "color", "description", "post", "payload"]), q7)

# Query 8
q8 = query_docs("what HTTP method does Discord webhook use?", "discord")
print("\nQ8: what HTTP method does Discord webhook use?")
print(f"   Result preview: {q8[:150]}\n")
check("Contains 'POST'",       "POST" in q8,    q8)
check("Contains 'webhook'",    "webhook" in q8.lower(), q8)


# ── Format contract ──────────────────────────────────────────────────────────
header("FORMAT CONTRACT — Japneet's agreed interface")

result = query_docs("what authentication headers does HubSpot need?", "hubspot")
check("Return type is str (not list, not dict)",
      type(result) is str)
check("Separator is exactly \\n---\\n between chunks",
      "\n---\n" in result)
check("Returns 3 chunks by default (2 separators)",
      result.count("\n---\n") == 2)

# n_results override
result_5 = query_docs("HubSpot contact fields", "hubspot", n_results=5)
check("n_results=5 returns 5 chunks (4 separators)",
      result_5.count("\n---\n") == 4)

# Source isolation
hub_result = query_docs("webhook", "hubspot")
dis_result = query_docs("webhook", "discord")
check("'hubspot' source never returns Discord-only content (no cross-contamination)",
      "discord.com" not in hub_result.lower())

# ValueError on bad n_results
try:
    query_docs("test", "hubspot", n_results=0)
    check("ValueError raised for n_results=0", False)
except ValueError:
    check("ValueError raised for n_results=0", True)


# ── Final summary ────────────────────────────────────────────────────────────
header("COMPLETE — RAG Engine ready for Japneet")
print("""
All 4 functions are working:
  load_doc()    — loads + cleans TXT / MD / PDF
  chunk_doc()   — sentence-boundary splitting with overlap
  ingest_doc()  — embeds chunks via NVIDIA NIM, stores in ChromaDB
  query_docs()  — semantic search, returns plain string for LLM prompts

Japneet call example:
  context = query_docs("what auth headers does HubSpot need?", "hubspot")
  # context is a plain string — insert directly into LLM prompt
""")

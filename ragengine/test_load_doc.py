"""
Quick test for load_doc() and _clean_doc_text().
Run with: python test_load_doc.py
No API key needed — load_doc() does not call any external services.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from rag_engine import load_doc, _clean_doc_text

# ---------------------------------------------------------------------------
# Test 1: cleaning logic on synthetic text (no real file needed)
# ---------------------------------------------------------------------------
print("=" * 60)
print("TEST 1 — Cleaning logic on synthetic text")
print("=" * 60)

sample = """
HubSpot Developer Documentation | API Reference | Changelog | Support

HubSpot Developer Documentation | API Reference | Changelog | Support

Authentication

The HubSpot API uses Bearer token authentication. You must include the
Authorization header in every request.

The format is: Authorization: Bearer YOUR_PRIVATE_APP_KEY

Contacts Endpoint

Base URL: https://api.hubspot.com/crm/v3/objects/contacts

Use a POST request to create a new contact. The request body must include
a properties object containing the contact fields.

Required fields: firstname, lastname, email

HubSpot Developer Documentation | API Reference | Changelog | Support
HubSpot Developer Documentation | API Reference | Changelog | Support
HubSpot Developer Documentation | API Reference | Changelog | Support

https://app.hubspot.com/some/internal/link/nobody/needs

Error responses contain a status field and a message field.
A 401 status means your API key is invalid or missing.

HubSpot Developer Documentation | API Reference | Changelog | Support
HubSpot Developer Documentation | API Reference | Changelog | Support
"""

cleaned = _clean_doc_text(sample, is_markdown=False)
print("--- Cleaned output ---")
print(cleaned)
print()

# Checks
nav_lines = [line for line in cleaned.splitlines()
             if "API Reference | Changelog | Support" in line]
has_auth = "Bearer" in cleaned or "Authorization" in cleaned
has_fields = "firstname" in cleaned
has_url = "https://app.hubspot.com/some/internal/link" in cleaned
has_endpoint = "api.hubspot.com" in cleaned

print("PASS" if not nav_lines else "FAIL", "— Navigation menu lines removed")
print("PASS" if has_auth   else "FAIL", "— Authorization/Bearer content preserved")
print("PASS" if has_fields else "FAIL", "— Field names (firstname) preserved")
print("PASS" if not has_url else "FAIL", "— Bare URL-only line removed")
print("PASS" if has_endpoint else "FAIL", "— Endpoint URL in prose preserved (api.hubspot.com)")

# Check no triple blank lines remain
import re
triple_blank = bool(re.search(r"\n{3,}", cleaned))
print("PASS" if not triple_blank else "FAIL", "— No triple blank lines")

# ---------------------------------------------------------------------------
# Test 2: real file loading (if files exist yet)
# ---------------------------------------------------------------------------
print()
print("=" * 60)
print("TEST 2 — Real file loading")
print("=" * 60)

for fname in ["hubspot_docs.txt", "discord_docs.txt"]:
    fpath = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(fpath):
        result = load_doc(fpath)
        original_size = os.path.getsize(fpath)
        cleaned_size = len(result.encode("utf-8"))
        ratio = cleaned_size / original_size * 100
        print(f"{fname}:")
        print(f"  Original size : {original_size:,} bytes")
        print(f"  Cleaned size  : {cleaned_size:,} bytes ({ratio:.0f}% of original)")
        print(f"  First 300 chars of cleaned output:")
        print("  " + result[:300].replace("\n", "\n  "))
        print()
    else:
        print(f"  {fname} not found — skipping (place it in {os.path.dirname(__file__)})")

print()
print("=" * 60)
print("TEST 3 — PDF loading (if a .pdf file exists in the folder)")
print("=" * 60)

pdf_files = [f for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".pdf")]
if pdf_files:
    for pdf_name in pdf_files:
        pdf_path = os.path.join(os.path.dirname(__file__), pdf_name)
        try:
            result = load_doc(pdf_path)
            print(f"{pdf_name}:")
            print(f"  Cleaned size: {len(result):,} chars")
            print(f"  First 200 chars: {result[:200]}")
            print()
        except Exception as e:
            print(f"  FAIL — {e}")
else:
    print("  No .pdf files found — skipping")
    print("  To test: drop any API documentation PDF into", os.path.dirname(__file__))

print()
print("Test complete.")

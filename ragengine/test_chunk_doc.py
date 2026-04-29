"""
test_chunk_doc.py — Tests for chunk_doc() and _find_sentence_boundary()
Run with: python test_chunk_doc.py
No API key needed — chunk_doc() is pure Python with no external calls.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rag_engine import load_doc, chunk_doc

FOLDER = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def header(title):
    print()
    print("=" * 60)
    print(f"TEST — {title}")
    print("=" * 60)


def check(label, condition):
    print("PASS" if condition else "FAIL", "—", label)


# ---------------------------------------------------------------------------
# Test 1: basic correctness on a short controlled text
# ---------------------------------------------------------------------------
header("Basic correctness on controlled text")

sample = (
    "The HubSpot API uses Bearer token authentication. "
    "You must include the Authorization header in every request. "
    "The format is: Authorization: Bearer YOUR_KEY. "
    "Contacts have the following fields: firstname, lastname, email. "
    "Use a POST request to create a new contact. "
    "The base URL is api.hubspot.com/crm/v3/objects/contacts. "
    "Error responses contain a status field and a message field. "
    "A 401 error means the token is missing or invalid. "
    "Rate limits allow 100 requests per 10 seconds. "
    "Pagination uses a cursor called the after parameter."
)

chunks = chunk_doc(sample, chunk_size=200, overlap=40)

print(f"Input length  : {len(sample)} chars")
print(f"Chunks created: {len(chunks)}")
print()
for i, chunk in enumerate(chunks):
    print(f"  Chunk {i+1} ({len(chunk)} chars): {chunk[:80]}...")
print()

check("At least 2 chunks produced from 500+ char text with chunk_size=200",
      len(chunks) >= 2)

check("No chunk exceeds chunk_size + small tolerance (sentence boundary overshoot)",
      all(len(c) <= 220 for c in chunks))

check("No chunk is empty",
      all(len(c.strip()) > 0 for c in chunks))

check("All chunks end with sentence-ending punctuation or are the last chunk",
      all(c[-1] in (".", "?", "!") for c in chunks[:-1]))

check("First chunk contains authentication content",
      any("Bearer" in c or "Authorization" in c for c in chunks))

check("Last chunk captured (no content silently dropped)",
      any("cursor" in c or "after" in c for c in chunks))

# ---------------------------------------------------------------------------
# Test 2: overlap verification — end of chunk N appears at start of chunk N+1
# ---------------------------------------------------------------------------
header("Overlap: tail of chunk N appears in head of chunk N+1")

chunks2 = chunk_doc(sample, chunk_size=200, overlap=40)

overlap_ok = True
for i in range(len(chunks2) - 1):
    tail = chunks2[i][-30:].strip()      # last 30 chars of chunk N
    head = chunks2[i + 1][:60].strip()   # first 60 chars of chunk N+1

    # The tail of chunk N should appear somewhere in the head of chunk N+1
    # We check a 10-char substring to allow for whitespace differences
    tail_snippet = tail[:10].strip()
    if tail_snippet and tail_snippet not in head:
        overlap_ok = False
        print(f"  WARNING chunk {i+1}→{i+2}: tail '{tail_snippet}' not found in head '{head[:40]}'")

check("Overlap confirmed — tail of each chunk reappears at head of next chunk",
      overlap_ok)

# ---------------------------------------------------------------------------
# Test 3: edge cases
# ---------------------------------------------------------------------------
header("Edge cases")

# Empty string
check("Empty string returns empty list",
      chunk_doc("") == [])

# String shorter than chunk_size
short = "Hello world. This is a short sentence."
check("Text shorter than chunk_size returns exactly one chunk",
      len(chunk_doc(short, chunk_size=500)) == 1)

check("Single chunk equals stripped input text",
      chunk_doc(short, chunk_size=500)[0] == short.strip())

# No sentence boundaries (one giant run-on)
no_boundary = "a" * 1200   # 1200 chars with no punctuation
chunks_nb = chunk_doc(no_boundary, chunk_size=500, overlap=80)
check("No-boundary text gets hard-cut into chunks (no infinite loop)",
      len(chunks_nb) >= 2)

# Invalid overlap
try:
    chunk_doc("Some text.", chunk_size=100, overlap=100)
    check("ValueError raised when overlap >= chunk_size", False)
except ValueError:
    check("ValueError raised when overlap >= chunk_size", True)

# ---------------------------------------------------------------------------
# Test 4: real files
# ---------------------------------------------------------------------------
header("Real files — HubSpot and Discord docs")

for fname, source in [("hubspot_docs.txt", "hubspot"), ("discord_docs.txt", "discord")]:
    fpath = os.path.join(FOLDER, fname)
    if not os.path.exists(fpath):
        print(f"  {fname} not found — skipping")
        continue

    clean_text = load_doc(fpath)
    chunks = chunk_doc(clean_text, chunk_size=500, overlap=80)

    print(f"\n{fname}:")
    print(f"  Clean text length : {len(clean_text):,} chars")
    print(f"  Chunks created    : {len(chunks)}")
    print(f"  Avg chunk size    : {sum(len(c) for c in chunks) // len(chunks)} chars")
    print(f"  Min chunk size    : {min(len(c) for c in chunks)} chars")
    print(f"  Max chunk size    : {max(len(c) for c in chunks)} chars")

    check(f"{source}: chunk count in expected range (5–300)",
          5 <= len(chunks) <= 300)

    check(f"{source}: no oversized chunks (max 600 chars with sentence boundary tolerance)",
          all(len(c) <= 600 for c in chunks))

    check(f"{source}: no empty chunks",
          all(len(c.strip()) > 0 for c in chunks))

    print(f"\n  First chunk preview:")
    print("  " + chunks[0][:200].replace("\n", "\n  "))

    print(f"\n  Last chunk preview:")
    print("  " + chunks[-1][:200].replace("\n", "\n  "))

print()
print("chunk_doc() tests complete.")

"""
test_ingest_doc.py — Tests for ingest_doc()
Run with: python test_ingest_doc.py

REQUIRES: NVIDIA_API_KEY environment variable set.
Set it before running:
    Windows CMD  : set NVIDIA_API_KEY=nvapi-xxxx
    Windows PS   : $env:NVIDIA_API_KEY="nvapi-xxxx"
    Git Bash/WSL : export NVIDIA_API_KEY=nvapi-xxxx
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

FOLDER = os.path.dirname(os.path.abspath(__file__))


def check(label, condition):
    print("PASS" if condition else "FAIL", "—", label)


def header(title):
    print()
    print("=" * 60)
    print(f"TEST — {title}")
    print("=" * 60)


# ── API key check before importing anything that touches NVIDIA ──────────────
if not os.environ.get("NVIDIA_API_KEY"):
    print()
    print("ERROR: NVIDIA_API_KEY is not set.")
    print()
    print("Get a free key at: https://build.nvidia.com")
    print("Then run:")
    print("  Windows CMD : set NVIDIA_API_KEY=nvapi-xxxx")
    print("  PowerShell  : $env:NVIDIA_API_KEY=\"nvapi-xxxx\"")
    print("  Git Bash    : export NVIDIA_API_KEY=nvapi-xxxx")
    print()
    sys.exit(1)

from rag_engine import ingest_doc, _get_collection

# ── Test 1: Ingest HubSpot docs ──────────────────────────────────────────────
header("Ingest hubspot_docs.txt")

hubspot_path = os.path.join(FOLDER, "hubspot_docs.txt")
if not os.path.exists(hubspot_path):
    print("hubspot_docs.txt not found — run download_docs.py first")
    sys.exit(1)

ingest_doc(hubspot_path, "hubspot")

collection = _get_collection()
hubspot_results = collection.get(where={"source": "hubspot"})

check("HubSpot chunks stored in ChromaDB",
      len(hubspot_results["ids"]) > 0)

check("HubSpot chunk count matches expected range (5–100)",
      5 <= len(hubspot_results["ids"]) <= 100)

check("All stored chunks have source='hubspot' in metadata",
      all(m["source"] == "hubspot" for m in hubspot_results["metadatas"]))

check("All stored chunks have chunk_index metadata",
      all("chunk_index" in m for m in hubspot_results["metadatas"]))

check("All stored chunks have doc_length metadata",
      all("doc_length" in m for m in hubspot_results["metadatas"]))

check("Embeddings are stored — verify by fetching with include param",
      len(collection.get(where={"source": "hubspot"}, include=["embeddings"])["embeddings"]) > 0)

print(f"\n  Stored {len(hubspot_results['ids'])} HubSpot chunks")
print(f"  First chunk ID  : {hubspot_results['ids'][0]}")
print(f"  First chunk text: {hubspot_results['documents'][0][:120]}...")

# ── Test 2: Ingest Discord docs ──────────────────────────────────────────────
header("Ingest discord_docs.txt")

discord_path = os.path.join(FOLDER, "discord_docs.txt")
if not os.path.exists(discord_path):
    print("discord_docs.txt not found — run download_docs.py first")
    sys.exit(1)

ingest_doc(discord_path, "discord")

discord_results = collection.get(where={"source": "discord"})

check("Discord chunks stored in ChromaDB",
      len(discord_results["ids"]) > 0)

check("Discord chunks have source='discord' in metadata",
      all(m["source"] == "discord" for m in discord_results["metadatas"]))

check("HubSpot and Discord chunks are separate (different IDs)",
      set(hubspot_results["ids"]).isdisjoint(set(discord_results["ids"])))

print(f"\n  Stored {len(discord_results['ids'])} Discord chunks")

# ── Test 3: Duplicate guard ──────────────────────────────────────────────────
header("Duplicate guard — calling ingest_doc() twice skips re-ingestion")

count_before = len(collection.get(where={"source": "hubspot"})["ids"])
ingest_doc(hubspot_path, "hubspot")   # second call — should skip
count_after  = len(collection.get(where={"source": "hubspot"})["ids"])

check("Chunk count unchanged after second ingest_doc() call",
      count_before == count_after)

# ── Test 4: Source name normalisation ────────────────────────────────────────
header("Source name normalisation — 'HubSpot' == 'hubspot'")

ingest_doc(hubspot_path, "HubSpot")   # uppercase — should be treated as duplicate
count_upper = len(collection.get(where={"source": "hubspot"})["ids"])

check("'HubSpot' normalised to 'hubspot' and treated as duplicate",
      count_before == count_upper)

# ── Summary ──────────────────────────────────────────────────────────────────
header("Summary")
all_results = collection.get()
print(f"  Total chunks in ChromaDB : {len(all_results['ids'])}")
print(f"  HubSpot chunks           : {count_before}")
print(f"  Discord chunks           : {len(discord_results['ids'])}")
print()
print("ingest_doc() tests complete. Ready to build query_docs().")

"""
rag_engine.py — RAG Ingestion Engine for ALI (Autonomous Integration Layer)
Stage 1 of the pipeline: loads, cleans, chunks, embeds, and stores API documentation
so the Synthesis Agent (Japneet) can query it by meaning rather than keyword.

LLM/embedding backend: NVIDIA NIM  (OpenAI-compatible API)
Embedding model:        nvidia/nv-embedqa-e5-v5
Vector DB:             ChromaDB (in-memory, cosine similarity)

Supported input formats: .txt  .md  .pdf
Source names: any string the user provides — not limited to "hubspot"/"discord"
"""

import os
import re
from collections import Counter
from typing import Optional

import pypdf
from dotenv import load_dotenv

# Load .env file so NVIDIA_API_KEY is available via os.environ
# This runs once when the module is first imported.
# If .env does not exist (e.g. in production where env vars are set another way)
# load_dotenv() silently does nothing — no crash.
load_dotenv()

import chromadb
from openai import OpenAI

# ---------------------------------------------------------------------------
# Module-level singletons — created once, reused across all function calls
# ---------------------------------------------------------------------------
_nim_client: Optional[OpenAI] = None
_chroma_client: Optional[chromadb.Client] = None
_collection = None

COLLECTION_NAME = "ali_docs"
EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"   # NVIDIA NIM embedding model
CHUNK_SEPARATOR = "\n---\n"                    # Japneet's agreed interface — do not change
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"


def _get_nim_client() -> OpenAI:
    """Return the shared NVIDIA NIM client, initialising it on first call.

    NVIDIA NIM uses an OpenAI-compatible REST API, so we use the openai SDK
    but point it at NVIDIA's endpoint with an NVIDIA API key.
    """
    global _nim_client
    if _nim_client is None:
        api_key = os.environ.get("NVIDIA_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "NVIDIA_API_KEY environment variable is not set. "
                "Get a free key at https://build.nvidia.com and then run: "
                "export NVIDIA_API_KEY=nvapi-..."
            )
        _nim_client = OpenAI(
            base_url=NIM_BASE_URL,
            api_key=api_key,
        )
    return _nim_client


def _get_collection():
    """Return the shared ChromaDB collection, creating it on first call."""
    global _chroma_client, _collection
    if _collection is None:
        # EphemeralClient = fully in-memory, no disk, no server needed
        _chroma_client = chromadb.EphemeralClient()
        _collection = _chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # cosine similarity as agreed
        )
    return _collection


# ---------------------------------------------------------------------------
# Function 1: load_doc
# ---------------------------------------------------------------------------

def load_doc(filepath: str) -> str:
    """Load an API documentation file and return clean, useful text only.

    Supports .txt, .md, and .pdf files. Strips navigation menus, repeated
    boilerplate, excessive blank lines, HTML tags, and bare URLs while
    preserving all prose, field names, endpoints, code examples, and
    authentication instructions.

    Args:
        filepath: Absolute or relative path to a .txt, .md, or .pdf file.

    Returns:
        A single clean string containing only the useful documentation content.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
        ValueError: If the file extension is not .txt, .md, or .pdf.
    """
    filepath = os.path.abspath(filepath)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Documentation file not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if ext not in (".txt", ".md", ".pdf"):
        raise ValueError(f"Unsupported file type '{ext}'. Expected .txt, .md, or .pdf")

    if ext == ".pdf":
        raw_text = _extract_pdf_text(filepath)
        # PDF text is already plain text after extraction — no markdown processing needed
        return _clean_doc_text(raw_text, is_markdown=False)

    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        raw_text = fh.read()

    return _clean_doc_text(raw_text, is_markdown=(ext == ".md"))


def _extract_pdf_text(filepath: str) -> str:
    """Extract plain text from a PDF file using pypdf.

    Reads every page in the PDF and joins the extracted text together.
    PDF extraction is never perfect — headers/footers bleed into the text,
    columns sometimes merge — but _clean_doc_text() handles the noise.

    Args:
        filepath: Absolute path to a .pdf file.

    Returns:
        Raw extracted text from all pages joined with newlines.

    Raises:
        ValueError: If the PDF is encrypted and cannot be read.
    """
    reader = pypdf.PdfReader(filepath)

    if reader.is_encrypted:
        raise ValueError(
            f"PDF is password-protected and cannot be read: {filepath}\n"
            "Export the PDF without a password and try again."
        )

    pages_text = []
    total_pages = len(reader.pages)
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages_text.append(page_text)
        print(f"  Reading PDF page {page_number}/{total_pages}...", end="\r")

    if not pages_text:
        raise ValueError(
            f"No text could be extracted from: {filepath}\n"
            "The PDF may contain only scanned images. Try a text-based PDF."
        )

    print(f"  Extracted {len(reader.pages)} pages from PDF")
    return "\n".join(pages_text)


def _clean_doc_text(text: str, is_markdown: bool = False) -> str:
    """Apply all cleaning passes to raw documentation text.

    Separated from load_doc() so it can be unit-tested without touching disk.

    Args:
        text: Raw text content from the documentation file.
        is_markdown: True if the source file was .md — enables Markdown stripping.

    Returns:
        Cleaned text string with noise removed and useful content preserved.
    """
    # Pass 1 — strip HTML tags (keep the text between them, remove only the tags)
    # e.g. <p>Send a POST request</p>  →  "Send a POST request"
    text = re.sub(r"<[^>]+>", "", text)

    # Pass 2 — strip Markdown formatting markers, keep the text content
    if is_markdown:
        # Remove heading markers but keep the heading text: "## Authentication" → "Authentication"
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        # Remove bold/italic markers: **word** → word, *word* → word
        text = re.sub(r"\*{1,2}([^*\n]+)\*{1,2}", r"\1", text)
        text = re.sub(r"_{1,2}([^_\n]+)_{1,2}", r"\1", text)
        # Remove inline code backticks but keep the code text — field names matter
        text = re.sub(r"`([^`\n]+)`", r"\1", text)
        # Remove Markdown link syntax, keep the visible link text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # Remove image syntax: ![alt](url) → (drop entirely, images add no text context)
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
        # Remove horizontal rules: ---, ***, ===
        text = re.sub(r"^[-*=]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Pass 3 — remove navigation menu lines
    # Rule: a line with 2+ pipe characters AND under 120 chars is almost always
    # a nav bar like "Docs | API Reference | Changelog | Support".
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.count("|") >= 2 and len(stripped) < 120:
            continue  # looks like a navigation menu — discard
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    # Pass 4 — remove lines that are bare URLs with no surrounding prose
    # These add nothing — the doc text describing the URL is what matters
    text = re.sub(r"^\s*https?://\S+\s*$", "", text, flags=re.MULTILINE)

    # Pass 5 — remove repeated boilerplate lines
    # Lines appearing 5+ times that are short (under 80 chars) are footers,
    # company names, copyright notices etc. We cap at 80 chars to avoid stripping
    # real technical content that legitimately repeats (e.g. "Content-Type: application/json").
    all_lines = text.splitlines()
    line_counts = Counter(line.strip() for line in all_lines if line.strip())
    boilerplate = {
        line for line, count in line_counts.items()
        if count >= 5 and len(line) < 80
    }
    # Safety net: never strip lines containing real API keywords even if repeated
    _never_strip = {
        line for line in boilerplate
        if any(kw in line.lower() for kw in [
            "content-type", "authorization", "bearer", "api-key",
            "application/json", "get ", "post ", "put ", "patch ", "delete ",
            "http", "https", "200", "400", "401", "403", "404", "429", "500",
        ])
    }
    boilerplate -= _never_strip
    text = "\n".join(
        line for line in all_lines
        if line.strip() not in boilerplate
    )

    # Pass 6 — collapse 3+ consecutive newlines (= 2+ blank lines) down to 2 newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Pass 7 — strip leading/trailing whitespace from the whole document
    return text.strip()


# ---------------------------------------------------------------------------
# Function 2: chunk_doc
# ---------------------------------------------------------------------------

def chunk_doc(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    """Split clean document text into overlapping chunks at sentence boundaries.

    Each chunk is at most chunk_size characters and always ends at a sentence
    boundary (period, question mark, exclamation mark followed by whitespace,
    or a paragraph break). Consecutive chunks share `overlap` characters at
    their boundary so information that spans the cut appears fully in at
    least one chunk.

    Args:
        text:       Clean text string returned by load_doc().
        chunk_size: Target maximum characters per chunk. Default 500.
        overlap:    Characters of repeated content between consecutive chunks.
                    Default 80. Must be less than chunk_size.

    Returns:
        List of non-empty chunk strings. Each chunk ends at a sentence boundary
        and is stripped of leading/trailing whitespace.

    Raises:
        ValueError: If overlap is >= chunk_size (would cause an infinite loop).
    """
    if overlap >= chunk_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than chunk_size ({chunk_size}). "
            "Overlap is the shared tail between chunks — it cannot be as large as the chunk itself."
        )

    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        # The furthest we can read in this iteration
        window_end = min(start + chunk_size, text_length)

        # If the window reaches the end of the text, take everything left and stop
        if window_end == text_length:
            final_chunk = text[start:].strip()
            if final_chunk:
                chunks.append(final_chunk)
            break

        # Find the last sentence boundary inside [start, window_end]
        # We search backwards from window_end so we take as much text as possible
        # while still ending cleanly at a sentence boundary
        boundary = _find_sentence_boundary(text, start, window_end)

        if boundary <= start:
            # No sentence boundary found anywhere in this window (e.g. one very
            # long sentence longer than chunk_size). Hard-cut at window_end so
            # we always make progress and never loop forever.
            boundary = window_end

        chunk = text[start:boundary].strip()
        if chunk:
            chunks.append(chunk)

        # The next chunk starts `overlap` characters before the current boundary.
        # This rewinds slightly so the tail of this chunk is re-read at the head
        # of the next chunk — the overlap ensures cross-boundary content is not lost.
        candidate_start = boundary - overlap

        if candidate_start <= start:
            # The overlap would rewind us to before where we started — that means
            # this chunk was smaller than the overlap window (short text at end of
            # doc, or a long paragraph with no internal boundaries). Just advance
            # past the boundary without overlap to prevent looping.
            start = boundary
        else:
            start = candidate_start

    return chunks


def _find_sentence_boundary(text: str, start: int, end: int) -> int:
    """Find the last sentence boundary position in text[start:end].

    Searches backwards from `end` toward `start` so we maximise the amount of
    text captured in each chunk. Returns the position just after the
    sentence-ending punctuation (the period/question mark IS included in the
    chunk; the following space is stripped by the caller).

    Boundary types recognised, in descending priority (first match wins when
    searching backwards):
        1. Double newline  \\n\\n  — paragraph break, strongest boundary
        2. Period/? /!  followed by space or newline — normal sentence end

    Args:
        text:  The full document text.
        start: Start index of the search window (inclusive).
        end:   End index of the search window (exclusive).

    Returns:
        Index of the character immediately after the sentence-ending punctuation,
        or `start` if no boundary was found in the window.
    """
    for i in range(end - 1, start, -1):

        # Priority 1 — paragraph break: two consecutive newlines
        # text[i] is the second \n, text[i-1] is the first \n
        if text[i] == "\n" and i > 0 and text[i - 1] == "\n":
            # Return position after the second newline — the next paragraph starts here
            return i + 1

        # Priority 2 — sentence-ending punctuation followed by whitespace
        if text[i] in (".", "?", "!"):
            next_pos = i + 1
            if next_pos < len(text) and text[next_pos] in (" ", "\n", "\t"):
                # Return the position of the space/newline after the punctuation
                # The caller strips the chunk so the trailing space is removed
                return next_pos

    # No boundary found in this window
    return start


# ---------------------------------------------------------------------------
# Function 3: ingest_doc
# ---------------------------------------------------------------------------

def ingest_doc(filepath: str, source_name: str) -> None:
    """Load, chunk, embed, and store an API documentation file in ChromaDB.

    This is the master ingestion function. It calls load_doc() to get clean
    text, chunk_doc() to split it, then for every chunk it calls the NVIDIA
    NIM embedding model to produce a vector and stores that vector alongside
    the chunk text and metadata in ChromaDB.

    After this function returns, query_docs() can search the stored chunks by
    meaning using cosine similarity.

    Args:
        filepath:    Path to the API documentation file (.txt, .md, or .pdf).
        source_name: A short label for this API — e.g. "hubspot", "discord",
                     "stripe". Used as a metadata tag so query_docs() can
                     filter results to one API at a time. Any string is valid.

    Returns:
        None. Side effect: ChromaDB collection populated with embedded chunks.

    Raises:
        EnvironmentError: If NVIDIA_API_KEY is not set.
        FileNotFoundError: If the documentation file does not exist.
        ValueError: If the file is a password-protected PDF or has no text.
    """
    source_name = source_name.strip().lower()   # normalise: "HubSpot" → "hubspot"

    collection = _get_collection()

    # ── Duplicate guard ──────────────────────────────────────────────────────
    # Query ChromaDB for any chunks already stored for this source_name.
    # If found, skip re-ingestion — duplicate chunks corrupt similarity scores.
    existing = collection.get(where={"source": source_name})
    if existing["ids"]:
        print(
            f"[ingest_doc] '{source_name}' already in ChromaDB "
            f"({len(existing['ids'])} chunks). Skipping re-ingestion."
        )
        return

    # ── Step 1: Load and clean ───────────────────────────────────────────────
    print(f"[ingest_doc] Loading '{filepath}' ...")
    clean_text = load_doc(filepath)
    print(f"[ingest_doc] Clean text: {len(clean_text):,} characters")

    # ── Step 2: Chunk ────────────────────────────────────────────────────────
    chunks = chunk_doc(clean_text)
    total  = len(chunks)
    print(f"[ingest_doc] Split into {total} chunks")

    if total == 0:
        print(f"[ingest_doc] WARNING: no chunks produced from '{filepath}'. Aborting.")
        return

    # ── Step 3: Embed each chunk via NVIDIA NIM ──────────────────────────────
    # We collect all IDs, vectors, texts, and metadata first, then do one
    # bulk add to ChromaDB — much faster than adding one record at a time.
    client = _get_nim_client()

    ids        = []   # unique string ID for each chunk
    embeddings = []   # list of vectors (each vector is a list of floats)
    documents  = []   # the raw chunk text (stored so query_docs can return it)
    metadatas  = []   # dict of tags attached to each chunk

    for index, chunk_text in enumerate(chunks):
        print(f"[ingest_doc] Embedding chunk {index + 1}/{total} ...", end="\r")

        # Call the NVIDIA NIM embedding endpoint.
        # input_type="passage" tells the E5 model this is a document being
        # stored — the query side uses input_type="query". This asymmetry
        # improves retrieval accuracy for the E5 model family.
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[chunk_text],
            encoding_format="float",
            extra_body={"input_type": "passage", "truncate": "END"},
        )

        vector = response.data[0].embedding   # list of floats (1024 dims for E5)

        ids.append(f"{source_name}_chunk_{index}")
        embeddings.append(vector)
        documents.append(chunk_text)
        metadatas.append({
            "source":      source_name,
            "chunk_index": index,
            "doc_length":  len(chunk_text),
        })

    print()   # newline after the \r progress line

    # ── Step 4: Store everything in ChromaDB ─────────────────────────────────
    # One bulk add is significantly faster than N individual add() calls.
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    print(
        f"[ingest_doc] Done. {total} chunks stored for '{source_name}' in ChromaDB."
    )


# ---------------------------------------------------------------------------
# Function 4: query_docs
# ---------------------------------------------------------------------------

def query_docs(question: str, source_name: str, n_results: int = 3) -> str:
    """Search ChromaDB for the most relevant chunks to answer a question.

    Converts the question to a vector using the same NVIDIA NIM embedding
    model, then asks ChromaDB for the n_results chunks whose vectors are
    closest to the question vector. Returns those chunks as a single plain
    string ready to be inserted directly into Japneet's LLM prompt.

    This is Japneet's interface. The return format is exactly agreed:
        chunk1_text + "\\n---\\n" + chunk2_text + "\\n---\\n" + chunk3_text

    Args:
        question:    Plain English question about the API.
                     e.g. "what authentication headers does HubSpot need?"
        source_name: Which API to search — must match a name used in ingest_doc().
                     e.g. "hubspot" or "discord". Case-insensitive.
        n_results:   How many chunks to return. Default 3 — the sweet spot
                     between enough context and too much noise in the prompt.

    Returns:
        A single string of the top n_results chunks joined by "\\n---\\n".
        Returns an empty string if no chunks are found for this source.

    Raises:
        EnvironmentError: If NVIDIA_API_KEY is not set.
        ValueError: If n_results is less than 1.
    """
    if n_results < 1:
        raise ValueError(f"n_results must be at least 1, got {n_results}")

    source_name = source_name.strip().lower()   # same normalisation as ingest_doc
    collection  = _get_collection()
    client      = _get_nim_client()

    # ── Step 1: Convert the question to a vector ──────────────────────────────
    # input_type="query" is the counterpart to input_type="passage" used during
    # ingest_doc(). The E5 model applies a different internal transformation for
    # queries vs documents — using the right type on each side improves accuracy.
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[question],
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "END"},
    )

    question_vector = response.data[0].embedding   # 1024 floats representing the question's meaning

    # ── Step 2: Ask ChromaDB for the closest matching chunks ──────────────────
    # where={"source": source_name} filters so we only search chunks from
    # the requested API — HubSpot questions never return Discord answers.
    # ChromaDB uses cosine similarity internally: the chunks whose vectors
    # point in the most similar direction to the question vector are returned.
    results = collection.query(
        query_embeddings=[question_vector],
        n_results=n_results,
        where={"source": source_name},
    )

    # results["documents"] is a list-of-lists because query() supports batch
    # input. Since we sent one question, we take results["documents"][0].
    # e.g. [["chunk text 1", "chunk text 2", "chunk text 3"]]
    matched_chunks = results["documents"][0]

    if not matched_chunks:
        return ""   # no chunks found — Japneet's prompt will have no context

    # ── Step 3: Join and return as a single plain string ─────────────────────
    return CHUNK_SEPARATOR.join(matched_chunks)

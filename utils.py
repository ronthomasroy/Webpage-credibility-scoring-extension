"""
utils.py
--------
Shared helpers: sentence splitting and text preprocessing.
"""

import re


def split_sentences(text: str) -> list[str]:
    """
    Split *text* into sentences using a robust regex heuristic.

    Handles:
    - Normal sentences ending in . ! ?
    - Sentences separated only by newlines (no terminal punctuation)
    - Single-sentence inputs with no punctuation at all
    """
    text = text.strip()
    if not text:
        return []

    # Step 1: split on sentence-ending punctuation followed by whitespace + capital
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', text)

    # Step 2: further split on newlines in case input has line-broken sentences
    sentences = []
    for chunk in raw:
        lines = [l.strip() for l in chunk.splitlines() if l.strip()]
        sentences.extend(lines)

    # Step 3: fallback — treat the entire text as one sentence
    return sentences if sentences else [text]


def preprocess_text(text: str) -> str:
    """Light cleaning: collapse whitespace, strip leading/trailing spaces."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_entity_sentences(entity: str, sentences: list[str], full_text: str = "") -> list[str]:
    """
    Return sentences that mention *entity* (case-insensitive, word-boundary aware).

    Falls back to searching *full_text* as a single sentence if nothing is
    found in the pre-split list — this handles the case where a short input
    has no terminal punctuation and wasn't split at all.
    """
    # Build a word-boundary regex so "Modi" doesn't match "modification"
    pattern = re.compile(r'\b' + re.escape(entity) + r'\b', re.IGNORECASE)
    matched = [s for s in sentences if pattern.search(s)]

    # Fallback: if nothing matched but entity appears in the full text,
    # treat the full text itself as one sentence
    if not matched and full_text and pattern.search(full_text):
        matched = [full_text.strip()]

    return matched

"""
entity_extractor.py
-------------------
Extracts and filters political entities from text using spaCy.
Removes noise: pronouns, partials, duplicates, and non-political tokens.
"""

import re
import spacy

# ── Noise filters ──────────────────────────────────────────────────────────────

# Common pronouns and determiners to exclude
PRONOUN_SET = {
    "he", "she", "they", "it", "we", "you", "i", "him", "her", "them", "us",
    "his", "their", "its", "our", "this", "that", "these", "those", "who",
    "what", "which", "whom", "whoever", "whatever",
}

# Partial / generic political tokens that carry no entity signal on their own
PARTIAL_TOKENS = {
    "party", "government", "administration", "official", "officials",
    "leader", "leaders", "member", "members", "the", "a", "an",
    "people", "nation", "country", "state", "states",
}

# spaCy NER labels we accept as potentially political
VALID_NER_LABELS = {"PERSON", "ORG", "GPE", "NORP", "FAC", "EVENT"}

# Minimum character length for an entity to be kept
MIN_ENTITY_LENGTH = 3


def _extract_propn_chunks(doc) -> list[str]:
    """
    Fallback extraction: capture contiguous PROPN token chunks.

    This recovers political entities that NER can occasionally miss
    (for example, single-name people like "Modi").
    """
    chunks: list[str] = []
    current: list[str] = []

    for token in doc:
        if token.pos_ == "PROPN" and not token.is_punct:
            current.append(token.text)
        else:
            if current:
                chunks.append(" ".join(current))
                current = []

    if current:
        chunks.append(" ".join(current))

    return chunks


def _load_nlp():
    """Load spaCy model (en_core_web_sm). Raises RuntimeError with install hint on failure."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        raise RuntimeError(
            "spaCy model not found. Run: python -m spacy download en_core_web_sm"
        )


def _normalize(text: str) -> str:
    """Strip possessives and extra whitespace. Preserve original casing for display."""
    text = text.strip()
    text = re.sub(r"'s$|\u2019s$", "", text)  # remove possessives (' and ')
    text = re.sub(r"\s+", " ", text)            # collapse whitespace
    return text.strip()


def _is_noise(entity_text: str) -> bool:
    """Return True if the entity should be filtered out."""
    lower = entity_text.lower()

    # Reject pronouns
    if lower in PRONOUN_SET:
        return True

    # Reject partial/generic tokens
    if lower in PARTIAL_TOKENS:
        return True

    # Reject very short strings
    if len(entity_text) < MIN_ENTITY_LENGTH:
        return True

    # Reject strings that are purely numeric or punctuation
    if re.fullmatch(r"[\d\W]+", entity_text):
        return True

    return False


def extract_entities(text: str, debug: bool = False) -> list[str]:
    """
    Extract unique, clean political entities from *text*.

    Returns a deduplicated list of entity strings, normalised and filtered.
    """
    nlp = _load_nlp()
    doc = nlp(text)

    raw_entities = []
    for ent in doc.ents:
        if ent.label_ in VALID_NER_LABELS:
            raw_entities.append(ent.text)

    # Fallback: merge in PROPN chunks for entities missed by NER.
    raw_entities.extend(_extract_propn_chunks(doc))

    if debug:
        print(f"[DEBUG entity_extractor] Raw entities: {raw_entities}")

    # Normalise
    normalised = [_normalize(e) for e in raw_entities]

    # Filter noise
    filtered = [e for e in normalised if not _is_noise(e)]

    # Deduplicate while preserving first-seen order
    seen: set[str] = set()
    unique: list[str] = []
    for e in filtered:
        key = e.lower()
        if key not in seen:
            seen.add(key)
            unique.append(e)

    if debug:
        print(f"[DEBUG entity_extractor] Clean entities: {unique}")

    return unique

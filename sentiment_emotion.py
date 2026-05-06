"""
sentiment_emotion.py
--------------------
Computes per-entity sentiment and emotion scores using HuggingFace pipelines.

Models used:
  • Sentiment : distilbert-base-uncased-finetuned-sst-2-english
  • Emotion   : j-hartmann/emotion-english-distilroberta-base
"""

from __future__ import annotations
from functools import lru_cache
from transformers import pipeline

from utils import get_entity_sentences, split_sentences

# ── Model IDs ─────────────────────────────────────────────────────────────────
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
EMOTION_MODEL   = "j-hartmann/emotion-english-distilroberta-base"

# Maximum token length accepted by most distilbert-family models
MAX_TOKEN_LEN = 512


@lru_cache(maxsize=1)
def _sentiment_pipeline():
    return pipeline("sentiment-analysis", model=SENTIMENT_MODEL, truncation=True)


@lru_cache(maxsize=1)
def _emotion_pipeline():
    return pipeline("text-classification", model=EMOTION_MODEL,
                    top_k=None, truncation=True)


# ── Internal helpers ───────────────────────────────────────────────────────────

def _truncate(text: str, max_chars: int = 1000) -> str:
    """Hard-truncate very long sentences to avoid tokeniser overflow."""
    return text[:max_chars]


def _analyse_sentiment(sentences: list[str]) -> dict:
    """
    Return aggregated sentiment for a list of sentences.

    Returns:
        {
            "positive": float,   # fraction in [0, 1]
            "negative": float,
            "total"   : int,
        }
    """
    if not sentences:
        return {"positive": 0.0, "negative": 0.0, "total": 0}

    pipe = _sentiment_pipeline()
    pos_total = 0.0
    neg_total = 0.0

    for sent in sentences:
        result = pipe(_truncate(sent))[0]
        label = result["label"].upper()
        score = float(result.get("score", 0.0))

        # Convert hard-label output into soft positive/negative contributions.
        # This avoids repeated +/-1 entity bias when only a few sentences exist.
        if label == "POSITIVE":
            pos_total += score
            neg_total += (1.0 - score)
        elif label == "NEGATIVE":
            neg_total += score
            pos_total += (1.0 - score)

    total = len(sentences)
    if total == 0:
        return {"positive": 0.0, "negative": 0.0, "total": 0}

    return {
        "positive": pos_total / total,
        "negative": neg_total / total,
        "total"   : total,
    }


def _analyse_emotion(sentences: list[str]) -> dict:
    """
    Return the dominant emotion and its average score across all sentences.

    Returns:
        { "dominant_emotion": str, "emotion_scores": {emotion: avg_score} }
    """
    if not sentences:
        return {"dominant_emotion": "neutral", "emotion_scores": {}}

    pipe = _emotion_pipeline()
    aggregated: dict[str, list[float]] = {}

    for sent in sentences:
        results = pipe(_truncate(sent))[0]          # list of {label, score}
        for item in results:
            aggregated.setdefault(item["label"], []).append(item["score"])

    avg_scores = {k: sum(v) / len(v) for k, v in aggregated.items()}
    dominant   = max(avg_scores, key=avg_scores.get) if avg_scores else "neutral"

    return {"dominant_emotion": dominant, "emotion_scores": avg_scores}


# ── Public API ─────────────────────────────────────────────────────────────────

def analyse_entities(
    text: str,
    entities: list[str],
    debug: bool = False,
) -> dict[str, dict]:
    """
    For each entity, extract relevant sentences and compute sentiment + emotion.

    Returns:
        {
            entity_name: {
                "sentiment": {"positive": float, "negative": float, "total": int},
                "emotion"  : {"dominant_emotion": str, "emotion_scores": dict},
                "sentences": [str, ...],
            },
            ...
        }
    """
    sentences = split_sentences(text)
    results: dict[str, dict] = {}

    for entity in entities:
        entity_sents = get_entity_sentences(entity, sentences, full_text=text)

        if not entity_sents:
            if debug:
                print(f"[DEBUG sentiment_emotion] No sentences found for '{entity}' – skipping.")
            continue

        sentiment = _analyse_sentiment(entity_sents)
        emotion   = _analyse_emotion(entity_sents)

        results[entity] = {
            "sentiment": sentiment,
            "emotion"  : emotion,
            "sentences": entity_sents,
        }

        if debug:
            print(f"[DEBUG sentiment_emotion] '{entity}': "
                  f"pos={sentiment['positive']:.2f}, "
                  f"neg={sentiment['negative']:.2f}, "
                  f"dominant_emotion={emotion['dominant_emotion']}")

    return results

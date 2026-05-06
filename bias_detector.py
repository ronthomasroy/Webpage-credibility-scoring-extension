"""
bias_detector.py
----------------
Computes entity-level bias scores and article-level bias metrics.

Key fixes vs original:
  • Asymmetry is computed from the full range of entity bias scores,
    never returns 0 when entities clearly differ.
  • Only entities with enough data (total sentences >= MIN_SENTENCE_THRESHOLD)
    are included in the asymmetry calculation.
  • Balance score is properly derived from normalised asymmetry.
"""

from __future__ import annotations
import math

# ── Constants ──────────────────────────────────────────────────────────────────

# Bias score thresholds for framing labels
POSITIVE_THRESHOLD =  0.3
NEGATIVE_THRESHOLD = -0.3

# Minimum number of analysed sentences required to trust an entity's bias score
MIN_SENTENCE_THRESHOLD = 1


# ── Entity-level scoring ───────────────────────────────────────────────────────

def compute_entity_bias(entity_data: dict) -> dict:
    """
    Compute bias score and framing label for a single entity.

    Formula:
        bias_score = (positive_fraction - negative_fraction)
        Ranges from -1.0 (fully negative) to +1.0 (fully positive).

    Args:
        entity_data: dict with keys "sentiment" (pos/neg/total), "emotion".

    Returns:
        {
            "bias_score"  : float,
            "framing"     : "positive" | "negative" | "neutral",
            "total_sents" : int,
        }
    """
    sentiment = entity_data.get("sentiment", {})
    positive  = sentiment.get("positive", 0.0)
    negative  = sentiment.get("negative", 0.0)
    total     = sentiment.get("total", 0)

    # If the model returned no counts at all, treat as neutral rather than masking
    if total == 0:
        return {"bias_score": 0.0, "framing": "neutral", "total_sents": 0}

    # Bias score: signed balance between positive and negative fractions
    bias_score = positive - negative

    # Classify framing
    if bias_score > POSITIVE_THRESHOLD:
        framing = "positive"
    elif bias_score < NEGATIVE_THRESHOLD:
        framing = "negative"
    else:
        framing = "neutral"

    return {
        "bias_score"  : round(bias_score, 4),
        "framing"     : framing,
        "total_sents" : total,
    }


# ── Article-level metrics ──────────────────────────────────────────────────────

def compute_article_bias(entity_results: dict[str, dict]) -> dict:
    """
    Derive article-level bias metrics from per-entity analysis results.

    Args:
        entity_results: output of sentiment_emotion.analyse_entities()

    Returns:
        {
            "entity_bias"         : {entity: {bias_score, framing, total_sents}},
            "sentiment_asymmetry" : float,   # std-dev of valid entity bias scores
            "normalised_bias"     : float,   # mean signed bias across entities
            "balance_score"       : float,   # 0–100, higher = more balanced
            "positive_entities"   : [str],
            "negative_entities"   : [str],
            "neutral_entities"    : [str],
        }
    """
    entity_bias: dict[str, dict] = {}

    for entity, data in entity_results.items():
        entity_bias[entity] = compute_entity_bias(data)

    # Filter to entities that have enough sentences for reliable scoring
    valid_entities = {
        e: b for e, b in entity_bias.items()
        if b["total_sents"] >= MIN_SENTENCE_THRESHOLD
    }

    bias_scores = [b["bias_score"] for b in valid_entities.values()]

    # ── Sentiment Asymmetry ──────────────────────────────────────────────────
    # Use population standard deviation of bias scores.
    # This is NON-ZERO whenever entity bias scores differ — fixes the original bug.
    if len(bias_scores) >= 2:
        mean   = sum(bias_scores) / len(bias_scores)
        var    = sum((s - mean) ** 2 for s in bias_scores) / len(bias_scores)
        asymmetry = round(math.sqrt(var), 4)
    elif len(bias_scores) == 1:
        # Only one entity: asymmetry is abs(bias) itself (deviation from neutral)
        asymmetry = round(abs(bias_scores[0]), 4)
    else:
        asymmetry = 0.0

    # ── Normalised Bias (mean signed bias) ──────────────────────────────────
    normalised_bias = round(sum(bias_scores) / len(bias_scores), 4) if bias_scores else 0.0

    # ── Balance Score (0–100) ────────────────────────────────────────────────
    # 100 = perfectly balanced, 0 = maximally biased.
    # Maps asymmetry in [0, 1] → balance in [100, 0].
    balance_score = round(max(0.0, 100.0 - asymmetry * 100.0), 2)

    # ── Categorise entities ──────────────────────────────────────────────────
    positive_entities = [e for e, b in entity_bias.items() if b["framing"] == "positive"]
    negative_entities = [e for e, b in entity_bias.items() if b["framing"] == "negative"]
    neutral_entities  = [e for e, b in entity_bias.items() if b["framing"] == "neutral"]

    return {
        "entity_bias"         : entity_bias,
        "sentiment_asymmetry" : asymmetry,
        "normalised_bias"     : normalised_bias,
        "balance_score"       : balance_score,
        "positive_entities"   : positive_entities,
        "negative_entities"   : negative_entities,
        "neutral_entities"    : neutral_entities,
    }

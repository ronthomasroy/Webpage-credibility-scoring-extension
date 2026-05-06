# political_bias_nlp

A clean, modular Python package for detecting political bias in news articles
using NLP, sentiment analysis, and emotion detection.

---

## 📦 Package Structure

```
political_bias_nlp/
├── __init__.py            # Public API
├── entity_extractor.py    # spaCy NER + custom noise filtering
├── sentiment_emotion.py   # HuggingFace sentiment + emotion per entity
├── bias_detector.py       # Entity & article-level bias scoring
├── bias_explainer.py      # ASCII report generation
├── utils.py               # Shared text helpers
├── main.py                # CLI entry point
└── requirements.txt
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 🚀 Usage

### As a script
```bash
# Demo text
python main.py

# Your own text
python main.py --text "The government unveiled bold new reforms today..."

# From a file
python main.py --file article.txt

# Debug mode
python main.py --debug
```

### As a library
```python
from political_bias_nlp.main import run_pipeline

text = "Your article here..."
report = run_pipeline(text, debug=False)
print(report)
```

---

## 📊 Sample Output

```
══════════════════════════════════════════
        ARTICLE BIAS ANALYSIS
══════════════════════════════════════════

  Sentiment Asymmetry   : 0.4714
  Political Balance     : 52.9 / 100
  Bias Meter            : [████░░░░░░]

  Interpretation        : Slight bias detected

──────────────────────────────────────────
  BIAS EXPLANATION
──────────────────────────────────────────

  • Positive framing → Labour Party, Keir Starmer
  • Negative framing → Conservative Party, Rishi Sunak

  ⚠  Extreme sentiment asymmetry detected between entities.

══════════════════════════════════════════
```

---

## 🔧 Key Design Decisions

| Problem (original)             | Fix                                              |
|-------------------------------|--------------------------------------------------|
| Noisy entities ("This", "Party") | `PRONOUN_SET` + `PARTIAL_TOKENS` filter sets  |
| Duplicate entities ("Party A's") | Possessive stripping + lowercase dedup         |
| Asymmetry always 0             | Std-dev of bias scores (never 0 when they differ)|
| Verbose output                 | Only final report is printed                    |

---

## 🧩 Module Responsibilities

| Module                  | Responsibility                                      |
|-------------------------|-----------------------------------------------------|
| `entity_extractor.py`   | NER → filter → normalise → deduplicate              |
| `sentiment_emotion.py`  | Per-entity sentence extraction + model inference    |
| `bias_detector.py`      | Bias score, framing label, asymmetry, balance score |
| `bias_explainer.py`     | ASCII meter + human-readable report                 |
| `utils.py`              | Sentence splitting, text preprocessing              |
| `main.py`               | CLI + pipeline orchestration                        |

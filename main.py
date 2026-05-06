"""
main.py
-------
Entry point for the Political Bias NLP package.

Usage:
    python main.py                        # uses built-in demo text
    python main.py --debug                # enables verbose debug logs
    python main.py --text "Your text..."  # analyse custom text
    python main.py --file article.txt     # analyse text from file
"""

import argparse
import sys
import os

# Allow running directly from the package directory
sys.path.insert(0, os.path.dirname(__file__))

from utils              import preprocess_text
from entity_extractor   import extract_entities
from sentiment_emotion  import analyse_entities
from bias_detector      import compute_article_bias
from bias_explainer     import generate_report


# ── Demo text ─────────────────────────────────────────────────────────────────
DEMO_TEXT = """
The Labour Party unveiled an ambitious economic plan today, praised by economists as 
visionary and progressive. Party leader Keir Starmer confidently outlined bold reforms 
that would reshape public services for generations to come.

Meanwhile, the Conservative Party faced fierce criticism over its handling of the NHS crisis. 
Prime Minister Rishi Sunak struggled to defend the government's record, with analysts 
describing the response as chaotic and deeply inadequate. Several Conservative MPs 
openly questioned the party's direction.

The Liberal Democrats positioned themselves as the reasonable middle ground, 
though commentators noted their proposals lacked the detail needed for serious evaluation."""

# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(text: str, debug: bool = False) -> str:
    """
    Full analysis pipeline.

    Steps:
        1. Preprocess text
        2. Extract political entities
        3. Analyse sentiment + emotion per entity
        4. Compute article-level bias metrics
        5. Generate human-readable report

    Returns:
        Formatted report string.
    """
    # 1 ── Preprocess
    text = preprocess_text(text)

    # 2 ── Extract entities
    entities = extract_entities(text, debug=debug)
    if not entities:
        return "\n[No political entities detected. Cannot produce bias analysis.]\n"

    # 3 ── Sentiment + emotion per entity
    entity_results = analyse_entities(text, entities, debug=debug)
    if not entity_results:
        return "\n[Could not extract sufficient sentence-level data for any entity.]\n"

    # 4 ── Article-level bias
    bias_results = compute_article_bias(entity_results)

    # 5 ── Generate report
    report = generate_report(bias_results)

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Political Bias NLP Analyser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python main.py                                    # demo text\n"
               "  python main.py \"Your text here\"                  # analyze custom text\n"
               "  python main.py --file article.txt                # analyze from file\n"
               "  python main.py \"Your text\" --debug              # with debug output",
    )
    parser.add_argument("text", nargs="?", default=None, help="Text to analyse (optional; positional)")
    parser.add_argument("--text", "-t", dest="flag_text", type=str,
                        help="Text to analyse (optional; overrides positional)")
    parser.add_argument("--file",  type=str, help="Path to a .txt file to analyse (overrides text)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as fh:
            text = fh.read()
    elif getattr(args, "flag_text", None):
        text = args.flag_text
    elif args.text:
        text = args.text
    else:
        text = DEMO_TEXT

    report = run_pipeline(text, debug=args.debug)
    print(report)


if __name__ == "__main__":
    main()

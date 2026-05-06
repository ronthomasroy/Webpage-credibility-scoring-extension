"""
political_bias_nlp
------------------
A modular Python package for detecting political bias in text.

Quick usage:
    from political_bias_nlp.main import run_pipeline
    report = run_pipeline("Your article text here...")
    print(report)
"""

from .main import run_pipeline  # noqa: F401

__all__ = ["run_pipeline"]

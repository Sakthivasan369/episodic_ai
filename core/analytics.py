"""
Analytics module for ArcEngine.

Calculates ONLY the Cliffhanger Score for each episode using
zero-shot classification (facebook/bart-large-mnli).

Emotion detection has been moved to the Narrative Intelligence Engine
(narrative_intelligence.py), which uses a Llama 3.3 API call for
superior contextual understanding.
"""

import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

_cliffhanger_classifier = None


def _get_cliffhanger_classifier():
    """Lazy load cliffhanger classifier on first use."""
    global _cliffhanger_classifier
    if _cliffhanger_classifier is None:
        logger.info("Loading Cliffhanger Model (facebook/bart-large-mnli)...")
        _cliffhanger_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _cliffhanger_classifier


def analyze_series(series_data: dict) -> dict:
    """
    Analyzes a series dictionary to add cliffhanger scores to each episode.

    Uses zero-shot classification to score the tension level of each
    episode's cliffhanger action against candidate labels:
    'unresolved mystery', 'physical danger', and 'peaceful resolution'.

    The final cliffhanger_score is the sum of 'unresolved mystery' and
    'physical danger' probabilities (range 0.0 – 1.0).

    Args:
        series_data: The full series dictionary containing an 'episodes' list.

    Returns:
        The same series dictionary with 'cliffhanger_score' injected into
        each episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        cliffhanger_text = episode.get("cliffhanger_action", "")

        if cliffhanger_text.strip():
            candidate_labels = [
                "unresolved mystery",
                "physical danger",
                "peaceful resolution",
            ]
            try:
                cliffhanger_classifier = _get_cliffhanger_classifier()

                cliffhanger_results = cliffhanger_classifier(
                    cliffhanger_text, candidate_labels
                )

                scores = dict(
                    zip(cliffhanger_results["labels"], cliffhanger_results["scores"])
                )

                cliffhanger_score = (
                    scores.get("unresolved mystery", 0.0)
                    + scores.get("physical danger", 0.0)
                )

                episode["cliffhanger_score"] = round(cliffhanger_score, 4)

            except Exception as e:
                logger.error("Error during cliffhanger analysis: %s", e)
                episode["cliffhanger_score"] = 0.0
        else:
            episode["cliffhanger_score"] = 0.0

    return series_data
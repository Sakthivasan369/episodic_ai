"""
Narrative Intelligence Engine for ArcEngine.

Uses a second Llama 3.3 API call to contextually analyze each episode,
detecting irony, sarcasm, figurative language, and implied meaning to
determine the true dominant emotion and generate a stronger viral title.

Supports stateful memory: previously generated titles are passed into
each subsequent call as a strict negative constraint to prevent
repetitive naming patterns across episodes.

Internal reasoning (irony/sarcasm detection) is never exposed to the
final API payload.
"""

import os
import logging
from typing import Any, Dict, List, Optional

import instructor
from groq import Groq

from schema import NarrativeAnalysis
from prompts import get_narrative_intelligence_prompt

logger = logging.getLogger(__name__)

MODEL_NAME = "llama-3.3-70b-versatile"


def _get_fallback_response(episode: Dict[str, Any]) -> Dict[str, Any]:
    """Returns safe defaults when the Narrative Intelligence call fails."""
    return {
        "episode_title": episode.get("title", "Untitled"),
        "dominant_emotion": "Unknown",
    }


def analyze_episode_context(
    episode: Dict[str, Any],
    previous_titles: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Analyzes a single episode using Llama 3.3 via Instructor.

    Responsibilities:
        1. Infer the TRUE dominant emotion (accounting for irony, sarcasm, etc.).
        2. Generate a stronger, viral episode title that is structurally
           unique from all previously generated titles.

    On failure, the original title is preserved and emotion is set to 'Unknown'.

    Args:
        episode: A dictionary representing one episode from the series arc.
        previous_titles: Running list of titles already generated for earlier
            episodes in this series. Used to build an anti-repetition constraint.

    Returns:
        A dictionary with 'episode_title' and 'dominant_emotion' keys.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY missing.")
        return _get_fallback_response(episode)

    if previous_titles is None:
        previous_titles = []

    try:
        client = instructor.from_groq(Groq(api_key=api_key))

        # Build the standard input
        episode_input_text = (
            f"Title: {episode.get('title', '')}\n"
            f"Summary: {episode.get('summary', '')}\n"
            f"Cliffhanger Text: {episode.get('cliffhanger_text', '')}\n"
            f"Emotion Tag: {episode.get('emotion_tag', '')}"
        )

        # Dynamically build a strict anti-repetition constraint
        anti_repetition_prompt = ""
        if previous_titles:
            used_titles_str = ", ".join([f"'{t}'" for t in previous_titles])
            anti_repetition_prompt = (
                f"\n\nCRITICAL CONSTRAINT: You have already generated the "
                f"following titles for previous episodes: {used_titles_str}. "
                f"Your new viral_title MUST NOT share any core nouns, "
                f"adjectives, or structural patterns (e.g., 'The [Noun] of "
                f"[Noun]') with these previous titles. Force a completely "
                f"unique concept and vocabulary."
            )

        response: NarrativeAnalysis = client.chat.completions.create(
            model=MODEL_NAME,
            response_model=NarrativeAnalysis,
            max_retries=2,
            messages=[
                {"role": "system", "content": get_narrative_intelligence_prompt()},
                {
                    "role": "user",
                    "content": (
                        f"Analyze this episode:\n\n"
                        f"{episode_input_text}{anti_repetition_prompt}"
                    ),
                },
            ],
        )

        result = response.model_dump()

        logger.info(
            "Narrative Intelligence — Ep %s: title='%s', emotion='%s'",
            episode.get("episode_number", "?"),
            result.get("episode_title"),
            result.get("dominant_emotion"),
        )

        return result

    except Exception as exc:
        logger.error(
            "Error during narrative intelligence analysis: %s",
            exc,
            exc_info=True,
        )
        return _get_fallback_response(episode)


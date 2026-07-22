"""
Narrative Intelligence Engine for ArcEngine.

Uses a second Llama 3.3 API call to contextually analyze each episode,
detecting irony, sarcasm, figurative language, and implied meaning to
determine the true dominant emotion and generate a stronger viral title.

Internal reasoning (irony/sarcasm detection) is never exposed to the
final API payload.
"""

import logging
from typing import Dict

from generator import client
from schema import NarrativeAnalysis
from prompts import get_narrative_intelligence_prompt

logger = logging.getLogger(__name__)


def _build_episode_user_prompt(episode: Dict[str, str]) -> str:
    """Constructs the user prompt for a single episode analysis."""
    return (
        f"Episode Title: {episode.get('title', '')}\n"
        f"Episode Summary: {episode.get('summary', '')}\n"
        f"Episode Cliffhanger: {episode.get('cliffhanger_action', '')}\n"
        f"Visual Storyboard: {episode.get('visual_storyboard', '')}\n\n"
        f"Return ONLY JSON."
    )


def analyze_episode_context(episode: Dict[str, str]) -> Dict[str, str]:
    """
    Analyzes a single episode using Llama 3.3 via Instructor.

    Responsibilities:
        1. Infer the TRUE dominant emotion (accounting for irony, sarcasm, etc.).
        2. Generate a stronger, viral episode title.

    On failure, the original title is preserved and emotion is set to 'Unknown'.

    Args:
        episode: A dictionary representing one episode from the series arc.

    Returns:
        The same episode dictionary, mutated with updated 'title' and 'emotion' keys.
    """
    user_prompt = _build_episode_user_prompt(episode)
    system_prompt = get_narrative_intelligence_prompt()

    try:
        response: NarrativeAnalysis = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=NarrativeAnalysis,
            max_retries=3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        episode["title"] = response.episode_title
        episode["emotion"] = response.dominant_emotion

        logger.info(
            "Narrative Intelligence — Ep %s: title='%s', emotion='%s'",
            episode.get("episode_number", "?"),
            response.episode_title,
            response.dominant_emotion,
        )

    except Exception as e:
        logger.error(
            "Narrative Intelligence failed for episode %s: %s",
            episode.get("episode_number", "?"),
            e,
        )
        # Graceful degradation: keep original title, mark emotion unknown
        episode["emotion"] = "Unknown"

    return episode

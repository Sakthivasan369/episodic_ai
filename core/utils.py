"""
Utility helpers for ArcEngine payload processing.
"""

from typing import Dict, List


def sanitize_series_payload(series_data: dict) -> dict:
    """
    Strips internal processing keys (open_loop, click_title, emotion_tag, etc.)
    and returns a clean payload matching CleanSeriesResponse.

    Args:
        series_data: The raw series dictionary after the full pipeline run.

    Returns:
        A sanitized dictionary containing only frontend-facing fields.
    """
    clean_episodes: List[Dict] = []

    for ep in series_data.get("episodes", []):
        clean_ep = {
            "episode_number": ep.get("episode_number"),
            "title": ep.get("title", "Untitled"),
            "summary": ep.get("summary", ""),
            "cliffhanger_action": ep.get("cliffhanger_action") or ep.get("cliffhanger_text", ""),
            "emotion": ep.get("emotion", "Unknown"),
            "cliffhanger_score": ep.get("cliffhanger_score", 0.0),
            "seo_hashtags": ep.get("seo_hashtags", []),
            "is_brand_safe": ep.get("is_brand_safe", True),
            "safety_score": ep.get("safety_score", 0.0),
        }
        clean_episodes.append(clean_ep)

    return {
        "series_title": series_data.get("series_title", "Untitled Series"),
        "episodes": clean_episodes,
    }

from transformers import pipeline
import re

# Lazy loading globals
_emotion_classifier = None

def _get_emotion_classifier():
    """Lazy load emotion classifier on first use."""
    global _emotion_classifier
    if _emotion_classifier is None:
        print("Loading Emotion Model (DistilRoBERTa)...")
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base"
        )
    return _emotion_classifier

def _calculate_lightweight_cliffhanger_score(text: str) -> float:
    """
    Calculates a tension/cliffhanger score using lightweight regex and keywords.
    Avoids loading heavy LLMs to save RAM.
    """
    if not text:
        return 0.0

    score = 0.1 # Base score

    # High-tension punctuation
    if "?" in text: score += 0.2
    if "!" in text: score += 0.2
    if "..." in text: score += 0.1

    # Tension keywords
    tension_words = [
        "suddenly", "reveals", "shocks", "danger", "secret", "truth", 
        "trap", "betrayal", "death", "discovery", "mystery", "cliff"
    ]

    for word in tension_words:
        if word in text.lower():
            score += 0.15

    return min(round(score, 4), 1.0)

def analyze_series(series_data: dict) -> dict:
    """
    Analyzes a series dictionary to add emotion and cliffhanger scores to each episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        # --- 1. Emotion Analysis (Keeping DistilRoBERTa as it is small ~300MB) ---
        text_for_emotion = f"{episode.get('summary', '')} {episode.get('visual_storyboard', '')}"

        if text_for_emotion.strip():
            try:
                emotion_classifier = _get_emotion_classifier()
                emotion_results = emotion_classifier(text_for_emotion)
                dominant_emotion = emotion_results[0]
                episode["calculated_emotion"] = dominant_emotion['label'].capitalize()
                episode["emotion_intensity"] = round(dominant_emotion['score'], 4)
            except Exception as e:
                print(f"Error during emotion analysis: {e}")
                episode["calculated_emotion"] = "N/A"
                episode["emotion_intensity"] = 0.0

        # --- 2. Cliffhanger Scoring (Lightweight Rule-based) ---
        cliffhanger_text = episode.get("cliffhanger_action", "")
        episode["cliffhanger_score"] = _calculate_lightweight_cliffhanger_score(cliffhanger_text)

    return series_data
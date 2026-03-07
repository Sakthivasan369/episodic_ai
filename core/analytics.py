import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

# Hugging Face Inference API details
API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
HF_TOKEN = os.environ.get("HF_HUB_TOKEN")

def _get_emotion_from_api(text: str) -> dict:
    """
    Calls the Hugging Face Inference API to get emotion labels.
    Ensures zero RAM usage for model loading.
    """
    if not HF_TOKEN:
        return {"label": "neutral", "score": 0.0}

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=10)
        
        if response.status_code == 200:
            # Response is typically a list of lists: [[{"label": "fear", "score": 0.9}, ...]]
            results = response.json()
            if isinstance(results, list) and len(results) > 0:
                # The API returns labels sorted by score if requested, or just a list.
                # We find the one with the highest score.
                inner_results = results[0] if isinstance(results[0], list) else results
                top_emotion = max(inner_results, key=lambda x: x['score'])
                return top_emotion
        return {"label": "neutral", "score": 0.0}
    except Exception as e:
        print(f"HF API Error: {e}")
        return {"label": "neutral", "score": 0.0}

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
        # --- 1. Emotion Analysis (Offloaded to HF API) ---
        text_for_emotion = f"{episode.get('summary', '')} {episode.get('visual_storyboard', '')}"

        if text_for_emotion.strip():
            result = _get_emotion_from_api(text_for_emotion[:512]) # API limit safety
            episode["calculated_emotion"] = result['label'].capitalize()
            episode["emotion_intensity"] = round(result['score'], 4)
        else:
            episode["calculated_emotion"] = "Neutral"
            episode["emotion_intensity"] = 0.0

        # --- 2. Cliffhanger Scoring (Lightweight Rule-based) ---
        cliffhanger_text = episode.get("cliffhanger_action", "")
        episode["cliffhanger_score"] = _calculate_lightweight_cliffhanger_score(cliffhanger_text)

    return series_data
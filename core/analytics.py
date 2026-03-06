from transformers import pipeline

# 1. Emotion analysis pipeline (Removed top_k=None to safely return just the #1 emotion)
print("Loading Emotion Model...")
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)

# 2. Zero-shot classification pipeline for cliffhanger scoring
print("Loading Cliffhanger Model...")
cliffhanger_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

def analyze_series(series_data: dict) -> dict:
    """
    Analyzes a series dictionary to add emotion and cliffhanger scores to each episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        # --- 1. Emotion Analysis ---
        text_for_emotion = f"{episode.get('summary', '')} {episode.get('visual_storyboard', '')}"
        
        if text_for_emotion.strip():
            try:
                # Without top_k, it returns: [{'label': 'fear', 'score': 0.85}]
                emotion_results = emotion_classifier(text_for_emotion)
                dominant_emotion = emotion_results[0] 
                
                episode["calculated_emotion"] = dominant_emotion['label'].capitalize()
                episode["emotion_intensity"] = round(dominant_emotion['score'], 4)
            except Exception as e:
                print(f"Error during emotion analysis: {e}")
                episode["calculated_emotion"] = "N/A"
                episode["emotion_intensity"] = 0.0

        # --- 2. Cliffhanger Scoring ---
        cliffhanger_text = episode.get("cliffhanger_action", "")
        if cliffhanger_text.strip():
            candidate_labels = ["unresolved mystery", "physical danger", "peaceful resolution"]
            try:
                # This returns a dictionary of labels and their probability scores
                cliffhanger_results = cliffhanger_classifier(cliffhanger_text, candidate_labels)
                
                # Zip them together into an easy-to-read dictionary
                scores = dict(zip(cliffhanger_results['labels'], cliffhanger_results['scores']))
                
                # The Heuristic Math!
                cliffhanger_score = scores.get("unresolved mystery", 0.0) + scores.get("physical danger", 0.0)
                
                episode["cliffhanger_score"] = round(cliffhanger_score, 4)
            except Exception as e:
                print(f"Error during cliffhanger analysis: {e}")
                episode["cliffhanger_score"] = 0.0

    return series_data
from transformers import pipeline


_emotion_classifier = None
_cliffhanger_classifier = None

def _get_emotion_classifier():
    """Lazy load emotion classifier on first use."""
    global _emotion_classifier
    if _emotion_classifier is None:
        print("Loading Emotion Model...")
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base"
        )
    return _emotion_classifier

def _get_cliffhanger_classifier():
    """Lazy load cliffhanger classifier on first use."""
    global _cliffhanger_classifier
    if _cliffhanger_classifier is None:
        print("Loading Cliffhanger Model...")
        _cliffhanger_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
    return _cliffhanger_classifier

def analyze_series(series_data: dict) -> dict:
    """
    Analyzes a series dictionary to add emotion and cliffhanger scores to each episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        
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

      
        cliffhanger_text = episode.get("cliffhanger_action", "")
        if cliffhanger_text.strip():
            candidate_labels = ["unresolved mystery", "physical danger", "peaceful resolution"]
            try:
                
                cliffhanger_classifier = _get_cliffhanger_classifier()
                
                cliffhanger_results = cliffhanger_classifier(cliffhanger_text, candidate_labels)
                
                #
                scores = dict(zip(cliffhanger_results['labels'], cliffhanger_results['scores']))
                
                #
                cliffhanger_score = scores.get("unresolved mystery", 0.0) + scores.get("physical danger", 0.0)
                
                episode["cliffhanger_score"] = round(cliffhanger_score, 4)
            except Exception as e:
                print(f"Error during cliffhanger analysis: {e}")
                episode["cliffhanger_score"] = 0.0

    return series_data
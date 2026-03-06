from transformers import pipeline

# Initialize the toxicity model
print("Loading Brand Safety (Toxicity) Model...")
toxicity_model = pipeline(
    "text-classification", 
    model="unitary/toxic-bert"
)

def check_brand_safety(series_data: dict) -> dict:
    """
    Scans the generated story arc for toxic content.
    If toxicity is detected, it flags the episode.
    """
    if "episodes" not in series_data:
        return series_data

    for episode in series_data["episodes"]:
        # Combine text fields for a comprehensive safety scan
        text_to_scan = f"{episode.get('title', '')} {episode.get('summary', '')} {episode.get('cliffhanger_text', '')}"
        
        if text_to_scan.strip():
            try:
                results = toxicity_model(text_to_scan)
                # unitery/toxic-bert returns 'toxic' or 'non-toxic' (or similar label mapping)
                # Typically: [{'label': 'toxic', 'score': 0.99}]
                prediction = results[0]
                
                # Check if the label is 'toxic' and the score is high
                is_toxic = prediction['label'].lower() == 'toxic' and prediction['score'] > 0.7
                
                episode["is_brand_safe"] = not is_toxic
                episode["safety_score"] = round(prediction['score'], 4)
                
                if is_toxic:
                    episode["safety_warning"] = "Content may violate platform guidelines."
            except Exception as e:
                print(f"Error during brand safety check: {e}")
                episode["is_brand_safe"] = True # Default to True if check fails
                
    return series_data

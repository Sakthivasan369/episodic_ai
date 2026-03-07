from transformers import pipeline
import re

# Use a more comprehensive NER model for better extraction
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def generate_hashtags(episode_data: dict) -> list:
    """
    Extracts entities and generates clean, SEO-friendly hashtags from episode content.
    """
    # Combine title, summary, and cliffhanger to extract meaningful context
    text = f"{episode_data.get('title', '')} {episode_data.get('summary', '')} {episode_data.get('cliffhanger_action', '')}"
    
    # Extract entities
    entities = ner_pipeline(text)
    
    hashtags = set()
    
    # 1. Process Entities
    for entity in entities:
        # Clean the word: remove spaces and special characters
        word = re.sub(r'\W+', '', entity["word"])
        if len(word) > 2:
            hashtags.add(f"#{word}")
            
    # 2. Heuristic: Add emotion tags as hashtags
    if 'emotion_tag' in episode_data:
        emotion = re.sub(r'\W+', '', episode_data['emotion_tag'])
        hashtags.add(f"#{emotion}")

    # 3. Industry standard tags for short-form video retention
    hashtags.update(["#ShortFilm", "#Storytelling", "#MicroSeries"])

    return list(hashtags)

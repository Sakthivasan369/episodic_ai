from transformers import pipeline
import re


ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")

def generate_hashtags(episode_data: dict) -> list:
    """
    Extracts entities and generates clean, SEO-friendly hashtags from episode content.
    Ensures no duplicates and consistent casing.
    """

    text = f"{episode_data.get('title', '')} {episode_data.get('summary', '')} {episode_data.get('cliffhanger_action', '')}"
    
    #
    entities = ner_pipeline(text)
    
    hashtags = set()
    
   
    for entity in entities:
        
        word = re.sub(r'\W+', '', entity["word"]).lower()
        if len(word) > 2:
            hashtags.add(f"#{word.capitalize()}")
            
    
    if 'emotion_tag' in episode_data:
        emotion = re.sub(r'\W+', '', episode_data['emotion_tag']).lower()
        if len(emotion) > 2:
            hashtags.add(f"#{emotion.capitalize()}")

    
    industry_tags = ["ShortFilm", "Storytelling", "MicroSeries"]
    for tag in industry_tags:
        hashtags.add(f"#{tag}")

    return sorted(list(hashtags))

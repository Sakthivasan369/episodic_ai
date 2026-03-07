import os
from typing import List
import instructor
from groq import Groq
from dotenv import load_dotenv

from prompts import get_system_prompt
from schema import SeriesArc, Episode, ProtagonistProfile
from seo_hashtag_generator import generate_hashtags

load_dotenv()

# Patched Groq client using instructor
client = instructor.from_groq(Groq(api_key=os.environ.get("GROQ_API_KEY")), mode=instructor.Mode.JSON)

# List of models to try in order of preference
MODELS = [
    "llama-3.3-70b-versatile", # Primary (Best quality)
    "llama-3.1-70b-versatile", # Reliable backup
    "llama-3.1-8b-instant",    # Fast Flash backup
    "llama3-8b-8192"           # Legacy backup
]

def generate_series_arc(concept: str, mood: str, num_episodes: int = 5) -> dict:
    """
    Uses Instructor to call Groq models and enforce a strict Pydantic schema.
    Includes a fallback mechanism to try multiple models if the primary fails.
    """
    system_prompt = get_system_prompt(mood, num_episodes)
    last_error = None

    for model_name in MODELS:
        try:
            # Attempt to generate the series arc with instructor validation
            response = client.chat.completions.create(
                model=model_name,
                response_model=SeriesArc,
                max_retries=2, # Instructor level retries
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Core Concept: {concept}"}
                ],
                temperature=0.7,
            )
            
            # If successful, convert Pydantic object to a dictionary
            arc_dict = response.model_dump()
            
            # Post-process: Apply SEO hashtags to each episode using the lightweight generator
            for episode in arc_dict["episodes"]:
                # Generate script-based hashtags
                script_hashtags = generate_hashtags(episode)
                # Combine with model-generated hashtags and remove duplicates
                combined_hashtags = list(set(episode.get("seo_hashtags", []) + script_hashtags))
                episode["seo_hashtags"] = sorted(combined_hashtags)
                
            return arc_dict
            
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_error = str(e)
            continue # Try the next model in the list

    # If all models fail, return the final error
    return {"error": f"All models failed. Last error: {last_error}"}

if __name__ == "__main__":
    test_concept = "A hacker finds a file predicting the future."
    test_mood = "Gritty Cyberpunk"
    
    print("Generating story arc and hashtags... please wait.")
    result = generate_series_arc(test_concept, test_mood)
    
    import json
    print(json.dumps(result, indent=2))

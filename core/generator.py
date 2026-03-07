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

def generate_series_arc(concept: str, mood: str, num_episodes: int = 5) -> dict:
    """
    Uses Instructor to call Llama-3.3-70B-Versatile and enforce a strict Pydantic schema
    for generating a story arc, then applies SEO hashtags to each episode.
    """
    system_prompt = get_system_prompt(mood, num_episodes)

    try:
        # Generate the series arc with instructor validation
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_model=SeriesArc,
            max_retries=3,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Core Concept: {concept}"}
            ],
            temperature=0.7,
        )
        
        # Convert Pydantic object to a dictionary
        arc_dict = response.model_dump()
        
        # Post-process: Apply SEO hashtags to each episode
        for episode in arc_dict["episodes"]:
            # Generate script-based hashtags
            script_hashtags = generate_hashtags(episode)
            # Combine with model-generated hashtags and remove duplicates
            combined_hashtags = list(set(episode.get("seo_hashtags", []) + script_hashtags))
            episode["seo_hashtags"] = combined_hashtags
            
        return arc_dict
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    test_concept = "A hacker finds a file predicting the future."
    test_mood = "Gritty Cyberpunk"
    
    print("Generating story arc and hashtags... please wait.")
    result = generate_series_arc(test_concept, test_mood)
    
    import json
    print(json.dumps(result, indent=2))

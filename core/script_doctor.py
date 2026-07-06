import os
import dspy
from dotenv import load_dotenv

load_dotenv()

#
try:
    groq_lm = dspy.LM(
        'groq/llama-3.3-70b-versatile',
        api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=150
    )
    dspy.configure(lm=groq_lm)
except Exception as e:
    print(f"Failed to initialize DSPy Groq LM: {e}")


class ScriptDoctor(dspy.Signature):
    """
    Analyze the episode text and its low NLP score. 
    Provide exactly ONE punchy, actionable sentence of advice to the creator 
    on how to increase the tension or improve the cliffhanger.
    """
    episode_summary = dspy.InputField(desc="The summary of the story episode")
    cliffhanger_score = dspy.InputField(desc="A score from 0.0 to 1.0 representing tension")
    director_advice = dspy.OutputField(desc="One punchy sentence of advice")


def consult_series(series_data: dict) -> dict:
    """
    Loops through episodes and provides advice if cliffhanger_score is low.
    """
    if "episodes" not in series_data:
        return series_data

    
    predictor = dspy.Predict(ScriptDoctor)

    for episode in series_data["episodes"]:
        score = episode.get("cliffhanger_score", 0.0)
        
        
        if score < 0.5:
            summary = episode.get("summary", "No summary provided.")
            
            try:
                
                response = predictor(episode_summary=summary, cliffhanger_score=score)
                episode["director_advice"] = response.director_advice
            except Exception as e:
                print(f"DSPy Script Doctor Timeout or Error: {e}")
                episode["director_advice"] = "Script Doctor is currently unavailable, but keep the stakes high!"

    return series_data

if __name__ == "__main__":
    
    test_data = {
        "episodes": [
            {
                "summary": "The hero eats a sandwich and goes to bed.",
                "cliffhanger_score": 0.1
            }
        ]
    }
    print("Testing Script Doctor...")
    print(consult_series(test_data))

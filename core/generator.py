import os 
import json 
from groq import Groq
from dotenv import load_dotenv

from prompts import get_system_prompt

load_dotenv()

client =Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_series_arc(concept: str, mood: str) -> dict:
    """
    Calls Groq to generate a 5-episode micro-arc in strict JSON format.
    """
    system_prompt = get_system_prompt(mood)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Core Concept: {concept}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            # Force Groq to return a JSON object
            response_format={"type": "json_object"} 
        )
        
        # Parse the string response into a Python dictionary
        response_content = chat_completion.choices[0].message.content
        
        # Verify it parses correctly before returning
        parsed_json = json.loads(response_content)
        return parsed_json
        
    except Exception as e:
        print(f"Error generating series: {e}")
        return {"error": str(e)}
    
if __name__ == "__main__":
    test_concept = "A hacker finds a file predicting the future."
    test_mood = "Gritty Cyberpunk"
    
    print("Generating story arc... please wait.")
    result = generate_series_arc(test_concept, test_mood)
    
    # Print the result nicely formatted
    print(json.dumps(result, indent=2))


if __name__ =="__main__":
    test_concept = "A hacker finds a file predicting the future."
    test_mood = "Gritty Cyberpunk"
    
    print("Generating story arc... please wait.")
    result = generate_series_arc(test_concept, test_mood)
    
    # Print the result nicely formatted
    print(json.dumps(result, indent=2))

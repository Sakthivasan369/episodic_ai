from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Importing from local modules in the same directory
from generator import generate_series_arc
from analytics import analyze_series
from script_doctor import consult_series
from brand_safety import check_brand_safety

# Initialize FastAPI app
app = FastAPI(title="ArcEngine API")

# Define the Pydantic model for the request
class StoryRequest(BaseModel):
    concept: str
    mood: str

@app.get("/")
async def health_check():
    """
    Simple health-check endpoint.
    """
    return {"status": "healthy", "message": "ArcEngine API is running"}

@app.post("/generate-series")
async def generate_series(request: StoryRequest):
    """
    Full pipeline: Generate -> Local Analytics -> AI Script Doctor -> Brand Safety.
    """
    # Requirement: If the user submits empty strings, raise a 400 error.
    if not request.concept.strip() or not request.mood.strip():
        raise HTTPException(
            status_code=400, 
            detail="Validation Error: 'concept' and 'mood' cannot be empty or whitespace-only strings."
        )

    # 1. Generate the initial story arc
    series_data = generate_series_arc(request.concept, request.mood)

    # 2. Check for generation failures
    if isinstance(series_data, dict) and "error" in series_data:
        raise HTTPException(
            status_code=500, 
            detail=f"Story Generation Failed: {series_data['error']}"
        )

    # 3. Augmentation & Safety Logic
    try:
        # A: Run NLP Emotion & Cliffhanger Analytics
        augmented_result = analyze_series(series_data)
        
        # B: Run DSPy AI Script Doctor for tension advice
        consulted_result = consult_series(augmented_result)
        
        # C: Run Brand Safety Check (Toxicity Detection)
        final_result = check_brand_safety(consulted_result)
        
        return final_result
    except Exception as e:
        # Prevent server crash for downstream failures
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline Failure: {str(e)}"
        )

if __name__ == "__main__":
    # To run: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

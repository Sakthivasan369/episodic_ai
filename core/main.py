from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Importing from local modules in the same directory
from generator import generate_series_arc
from analytics import analyze_series

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
    Main endpoint to generate a story arc and augment it with emotional analytics.
    """
    # Requirement: If the user submits empty strings, raise a 400 error.
    if not request.concept.strip() or not request.mood.strip():
        raise HTTPException(
            status_code=400, 
            detail="Validation Error: 'concept' and 'mood' cannot be empty or whitespace-only strings."
        )

    # 1. Logic Flow: Pass the variables to generate_series_arc
    # The generator returns a dict (potentially with an "error" key)
    series_data = generate_series_arc(request.concept, request.mood)

    # 2. Error Handling: If the generator returns an "error" key, raise a 500 error.
    if isinstance(series_data, dict) and "error" in series_data:
        raise HTTPException(
            status_code=500, 
            detail=f"Story Generation Failed: {series_data['error']}"
        )

    # 3. Logic Flow: Pass that exact result into analyze_series and return augmented JSON.
    try:
        augmented_result = analyze_series(series_data)
        return augmented_result
    except Exception as e:
        # Safety catch for downstream processing errors
        raise HTTPException(
            status_code=500,
            detail=f"Analytics Processing Error: {str(e)}"
        )

if __name__ == "__main__":
    # To run: python main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)

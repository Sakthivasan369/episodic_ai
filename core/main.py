"""
ArcEngine API — Main pipeline orchestrator.

Pipeline:
    1. generate_series_arc()      → Base story generation (Llama 3.3)
    2. analyze_episode_context()  → Narrative Intelligence per episode (Llama 3.3)
    3. analyze_series()           → Cliffhanger scoring (BART-MNLI)
    4. generate_hashtags()        → SEO hashtag generation (BERT-NER)
    5. check_brand_safety()       → Toxicity detection (toxic-bert)
    6. sanitize_series_payload()  → Strip internal keys, enforce clean schema
"""

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from generator import generate_series_arc
from narrative_intelligence import analyze_episode_context
from analytics import analyze_series
from seo_hashtag_generator import generate_hashtags
from brand_safety import check_brand_safety
from schema import CleanSeriesResponse
from utils import sanitize_series_payload

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ArcEngine API")


class StoryRequest(BaseModel):
    concept: str
    mood: str
    num_episodes: int = 5


@app.get("/")
async def health_check():
    """
    Simple health-check endpoint.
    """
    return {"status": "healthy", "message": "ArcEngine API is running"}


@app.post("/generate-series", response_model=CleanSeriesResponse)
async def generate_series(request: StoryRequest):
    """
    Full pipeline:
        Generate → Narrative Intelligence → Cliffhanger Scoring
        → SEO Hashtags → Brand Safety.
    """

    if not request.concept.strip() or not request.mood.strip():
        raise HTTPException(
            status_code=400,
            detail="Validation Error: 'concept' and 'mood' cannot be empty or whitespace-only strings.",
        )

    # ── Step 1: Base story generation ──────────────────────────────────
    logger.info("Step 1/6 — Generating base story arc...")
    series_data = generate_series_arc(
        request.concept, request.mood, request.num_episodes
    )

    if isinstance(series_data, dict) and "error" in series_data:
        raise HTTPException(
            status_code=500,
            detail=f"Story Generation Failed: {series_data['error']}",
        )

    try:
        # ── Step 2: Narrative Intelligence (per episode) ───────────────
        logger.info("Step 2/6 — Running Narrative Intelligence...")
        for episode in series_data.get("episodes", []):
            analyze_episode_context(episode)

        # ── Step 3: Cliffhanger scoring ────────────────────────────────
        logger.info("Step 3/6 — Calculating cliffhanger scores...")
        analyzed_result = analyze_series(series_data)

        # ── Step 4: SEO hashtag generation ─────────────────────────────
        logger.info("Step 4/6 — Generating SEO hashtags...")
        for episode in analyzed_result.get("episodes", []):
            episode["seo_hashtags"] = generate_hashtags(episode)

        # ── Step 5: Brand safety check ─────────────────────────────────
        logger.info("Step 5/6 — Running brand safety check...")
        final_result = check_brand_safety(analyzed_result)

        # ── Step 6: Sanitize payload ───────────────────────────────────
        logger.info("Step 6/6 — Sanitizing payload...")
        cleaned_payload = sanitize_series_payload(final_result)

        logger.info("Pipeline complete.")
        return cleaned_payload

    except Exception as e:
        logger.exception("Pipeline failure: %s", e)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline Failure: {str(e)}",
        )


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)

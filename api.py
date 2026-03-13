from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import uuid
import asyncio

# Import required modules from existing pipeline
from main import SkillAnalyzerPipeline
from scorer import SkillScorer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title="AI Hands-On Persona Analyzer API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes. In production, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = SkillAnalyzerPipeline()
scorer = SkillScorer()

# In-memory store for async tasks (for faster frontend response and background processing)
# In a real app, use Redis/Celery.
TASKS_DB: Dict[str, Any] = {}

class AnalyzeRequest(BaseModel):
    github_username: Optional[str] = None
    resume_pdf_path: Optional[str] = None  # Mocking file upload via path for simplicity in API model
    video_urls: Optional[List[str]] = None
    extra_urls: Optional[List[str]] = None

@app.post("/api/analyze")
async def analyze_profile(request: AnalyzeRequest):
    """
    Triggers the full pipeline and scoring synchronously.
    (Note: Video transcription might take time, so limit video sizes or run async via `/api/analyze/async`)
    """
    try:
        logging.info(f"Received analysis request: {request}")
        
        if not (request.github_username or request.resume_pdf_path or request.video_urls or request.extra_urls):
            raise HTTPException(status_code=400, detail="Must provide at least one data source.")
            
        pipeline_data = pipeline.run_pipeline(
            github_username=request.github_username,
            resume_pdf_path=request.resume_pdf_path,
            video_urls=request.video_urls,
            extra_urls=request.extra_urls
        )
        
        # Calculate Score
        score_data = scorer.calculate_score(pipeline_data)
        
        return {
            "status": "success",
            "raw_data": pipeline_data,
            "analysis": score_data
        }

    except Exception as e:
        logging.error(f"Error in /api/analyze: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

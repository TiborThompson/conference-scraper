"""
FastAPI backend for speaker recommendation system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from contextlib import asynccontextmanager
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.llm.speaker_matcher import SpeakerMatcher, load_speakers_from_file

# Load speakers on startup
speakers_data = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    global speakers_data
    try:
        speakers_data = load_speakers_from_file("data/speakers.json")
        print(f"Loaded {len(speakers_data)} speakers")
    except Exception as e:
        print(f"Error loading speakers: {e}")
    yield

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    user_bio: str
    threshold: float = 6.0


class SpeakerMatch(BaseModel):
    name: str
    title: str
    organization: str
    bio: str
    score: float
    reasoning: str


class MatchResponse(BaseModel):
    matches: List[SpeakerMatch]
    total_speakers: int
    matches_found: int


@app.get("/")
async def root():
    return {"message": "Speaker Recommendation API", "speakers_loaded": len(speakers_data)}


@app.get("/speakers")
async def get_speakers():
    """Get all speakers"""
    return {"speakers": speakers_data, "count": len(speakers_data)}


@app.post("/match", response_model=MatchResponse)
async def match_speakers(request: MatchRequest):
    """Match speakers based on user bio"""
    if not speakers_data:
        raise HTTPException(status_code=500, detail="Speaker data not loaded")
    
    if not request.user_bio or len(request.user_bio.strip()) < 10:
        raise HTTPException(status_code=400, detail="User bio must be at least 10 characters")
    
    try:
        matcher = SpeakerMatcher()
        matches = await matcher.recommend_speakers(
            request.user_bio, 
            speakers_data, 
            threshold=request.threshold
        )
        
        return MatchResponse(
            matches=matches,
            total_speakers=len(speakers_data),
            matches_found=len(matches)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error matching speakers: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

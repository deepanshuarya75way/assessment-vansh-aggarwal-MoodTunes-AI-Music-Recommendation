"""
/api/music/* routes

POST /api/music/recommend  — get tracks for a given emotion
"""

from fastapi import APIRouter, HTTPException, Depends
from backend.models.recommendation import MusicRecommendRequest, MusicRecommendResponse,FeedbackRequest
from backend.services.music_engine import rerank_by_feedback
from backend.utils.lastfm import fetch_tracks_by_tag
from backend.config import get_db

router = APIRouter()

# Assuming these are imported correctly from your services
from backend.services.music_engine import (
    get_mood_tag, 
    rerank_by_feedback, 
    fetch_tracks_by_tag  # Added missing import
)
from backend.config import get_db  # Import your database dependency

router = APIRouter(prefix="/api/music", tags=["Music Recommendation"])

        
@router.post("/recommend", response_model=MusicRecommendResponse, summary="Get music recommendations for an emotion")
async def get_recommendations(request: MusicRecommendRequest, db = Depends(get_db)):
    """
    Returns a curated playlist from LastFM based on the detected emotion.

    - **emotion**: One of: happy, sad, angry, fearful, surprised, disgusted, neutral, excited
    - **user_id**: Optional user identifier
    - **limit**: Number of tracks to return (1–30, default 10)
    """
    try:
        emotion = (
            getattr(request, "emotion", None)
            or  getattr(request, "mood", None)
            or  getattr(request, "detected_emotion", None)
            or  getattr(request, "text_emotion", None)    
        )

        if emotion is None :
            raise HTTPException(status_code= 422, detail= "No emotion found")

        limit = getattr(request, "limit", 10)

        print("[recommend] fetching from lastfm..")
        result = await fetch_tracks_by_tag(emotion, limit)
        print("[recommend] fetching from lastfm from reranking..")
        tracks = await rerank_by_feedback(result["tracks"], emotion, db)
        print("[recommend] rerank done, returining response.")
       

        return MusicRecommendResponse(
            emotion = emotion,
            mood_tag = result["mood_tag"],
            tracks = tracks,
            playlist_label = result["playlist_label"]
        )
        
      
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music recommendation failed: {str(e)}")


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, db = Depends(get_db)):
    try:
        record = FeedbackRecord(**request.dict())
        await db.feedback.insert_one(record.dict())
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Feedback Saved failed")

"""
/api/music/* routes

POST /api/music/recommend  — get tracks for a given emotion
"""

from fastapi import APIRouter, HTTPException
from backend.models.recommendation import MusicRecommendRequest, MusicRecommendResponse
from backend.services.music_engine import recommend_music

router = APIRouter(prefix="/api/music", tags=["Music Recommendation"])


@router.post("/recommend", response_model=MusicRecommendResponse, summary="Get music recommendations for an emotion")
async def get_recommendations(request: MusicRecommendRequest):
    """
    Returns a curated playlist from LastFM based on the detected emotion.

    - **emotion**: One of: happy, sad, angry, fearful, surprised, disgusted, neutral, excited
    - **user_id**: Optional user identifier
    - **limit**: Number of tracks to return (1–30, default 10)
    """
    valid_emotions = {"happy", "sad", "angry", "fearful", "surprised", "disgusted", "neutral", "excited"}
    if request.emotion not in valid_emotions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid emotion '{request.emotion}'. Valid: {sorted(valid_emotions)}"
        )

    try:
        result = await recommend_music(emotion=request.emotion, limit=request.limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Music recommendation failed: {str(e)}")

"""
Music Recommendation Engine.
Orchestrates LastFM API call + any future ML-based ranking logic.
"""

from backend.utils.lastfm import fetch_tracks_by_tag
from backend.models.recommendation import Track, MusicRecommendResponse
import asyncio

MOOD_GROUPS = {
    "happy" : ["happy", "excited"],
    "sad" : ["sad", "disgusted"]
}
MOOD_TAG_MAP = {
    "happy":     "happy",
    "sad":       "sad",
    "angry":     "aggressive",
    "fearful":   "dark",
    "surprised": "uplifting",
    "disgusted": "melancholic",
    "neutral":   "chill",
    "excited":   "energetic",
}
def get_mood_tag(emotion : str) -> str :
    return MOOD_TAG_MAP.get(emotion.lower(), "chill")

async def rerank_by_feedback(tracks : list, mood : str, db) -> list :
    moods = MOOD_GROUPS.get(mood, [mood])

    try:
        cursor = db.feedback.find({"mood": {"$in": moods}})
        feedback_docs = await asyncio.wait_for(cursor.to_list(length = None), timeout = 5.0)
    except asyncio.TimeoutError :
        print("[rerank_by_feedback] MongoDB query timed out")
        return tracks
    

    if tracks not in feedback_docs: 
        return tracks

    negative_ids = set()
    positive_scores = {}
    for doc in feedback_docs:
        tid = doc["track_id"]
        if doc["feedback"] == "negative":
            negative_ids.add(tid)
        elif doc["feedback"] == "positive":
            positive_scores[tid] = positive_scores.get(tid, 0)

    def track_key(t) :
        return t.get("track_id") or f"{t.get('name')::{t.get('artist')}}"

    filtered = [t for t in tracks if t["track_id"] not in negative_ids]

    filtered.sort(key = lambda t : positive_scores.get(t["track_id"], 0), reverse = True)

    return filtered

async def create_indexes(db) :
    await db.feedback.create_index("Mood")
    await db.feedback.create_index([("mood",1), ("track_id", 1)])

async def recommend_music(emotion: str, limit: int = 10) -> MusicRecommendResponse:
    """
    Core recommendation pipeline:
      detected emotion → LastFM tag → top tracks → structured response
    """
    #result = await fetch_tracks_by_tag(emotion, limit=limit)
    result = await rerank_by_feedback(tracks, emotion, db)

    tracks = [
        Track(
            name=t["name"],
            artist=t["artist"],
            url=t.get("url"),
            image=t.get("image"),
            listeners=t.get("listeners"),
        )
        for t in result["tracks"]
    ]

    return MusicRecommendResponse(
        emotion=emotion,
        mood_tag=result["mood_tag"],
        playlist_label=result["playlist_label"],
        tracks=tracks,
    )

    

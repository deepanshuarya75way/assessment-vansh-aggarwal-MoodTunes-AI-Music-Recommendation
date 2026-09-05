"""
Music Recommendation Engine.
Orchestrates LastFM API call + any future ML-based ranking logic.
"""

from backend.utils.lastfm import fetch_tracks_by_tag
from backend.models.recommendation import Track, MusicRecommendResponse


async def recommend_music(emotion: str, limit: int = 10) -> MusicRecommendResponse:
    """
    Core recommendation pipeline:
      detected emotion → LastFM tag → top tracks → structured response
    """
    result = await fetch_tracks_by_tag(emotion, limit=limit)

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

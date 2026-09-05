"""
LastFM API wrapper.
Docs: https://www.last.fm/api/intro
Key endpoint used: tag.getTopTracks — fetch top tracks for a mood tag.
"""

import httpx
from backend.config import LASTFM_API_KEY, LASTFM_BASE_URL

# Emotion → LastFM tag mapping
EMOTION_TO_TAG = {
    "happy":     "happy",
    "sad":       "sad",
    "angry":     "aggressive",
    "fearful":   "dark",
    "surprised": "uplifting",
    "disgusted": "melancholic",
    "neutral":   "chill",
    "excited":   "energetic",
}

# Human-readable playlist labels
PLAYLIST_LABELS = {
    "happy":     "🌟 Feeling Good Vibes",
    "sad":       "🌧️ Rainy Day Feels",
    "angry":     "🔥 Let It Out",
    "fearful":   "🌙 Into the Dark",
    "surprised": "✨ Something New",
    "disgusted": "💭 Introspective",
    "neutral":   "☁️ Easy Listening",
    "excited":   "⚡ High Energy",
}


async def fetch_tracks_by_tag(emotion: str, limit: int = 10) -> dict:
    """
    Fetches top tracks for the LastFM tag corresponding to the emotion.
    Returns: {"mood_tag": str, "playlist_label": str, "tracks": List[dict]}
    """
    tag = EMOTION_TO_TAG.get(emotion, "chill")
    playlist_label = PLAYLIST_LABELS.get(emotion, "🎵 Your Playlist")

    params = {
        "method": "tag.getTopTracks",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(LASTFM_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

    tracks_raw = data.get("tracks", {}).get("track", [])
    tracks = []
    for t in tracks_raw:
        image_url = None
        images = t.get("image", [])
        for img in images:
            if img.get("size") == "large":
                image_url = img.get("#text") or None
                break

        tracks.append({
            "name": t.get("name", "Unknown"),
            "artist": t.get("artist", {}).get("name", "Unknown"),
            "url": t.get("url"),
            "image": image_url,
            "listeners": int(t.get("listeners", 0) or 0),
        })

    return {
        "mood_tag": tag,
        "playlist_label": playlist_label,
        "tracks": tracks,
    }

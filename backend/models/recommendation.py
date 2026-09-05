from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


##3class InputMode(str, Enum):
##   text = "text"  image = "image" 
class InputMode(str, Enum):
    text = "text"
    image = "image"
    manual = "manual"

class EmotionLabel(str, Enum):
    happy = "happy"
    sad = "sad"
    angry = "angry"
    surprised = "surprised"
    fearful = "fearful"
    disgusted = "disgusted"
    neutral = "neutral"
    excited = "excited"


class TextEmotionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="User's text input")
    user_id: Optional[str] = "guest"


class TextEmotionResponse(BaseModel):
    emotion: str
    confidence: float
    raw_scores: dict


class ImageEmotionResponse(BaseModel):
    emotion: str
    confidence: float
    all_emotions: dict


class Track(BaseModel):
    name: str
    artist: str
    url: Optional[str] = None
    image: Optional[str] = None
    listeners: Optional[int] = None


class MusicRecommendRequest(BaseModel):
    emotion: str
    user_id: Optional[str] = "guest"
    limit: int = Field(default=10, ge=1, le=30)


class MusicRecommendResponse(BaseModel):
    emotion: str
    mood_tag: str
    tracks: List[Track]
    playlist_label: str


class HistoryEntry(BaseModel):
    user_id: str
    input_mode: InputMode
    detected_emotion: str
    confidence: float
    tracks_recommended: List[Track]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HistoryResponse(BaseModel):
    user_id: str
    sessions: List[dict]
    total: int

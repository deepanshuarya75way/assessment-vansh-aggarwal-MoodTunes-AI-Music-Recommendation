"""
NLP-based emotion detection from text.
Uses j-hartmann/emotion-english-distilroberta-base — a DistilRoBERTa model
fine-tuned on 6 Ekman emotions: anger, disgust, fear, joy, neutral, sadness, surprise.
"""

from transformers import pipeline
from functools import lru_cache
import re

# Emotion label normalization — model outputs -> MoodTunes internal labels
EMOTION_MAP = {
    "joy": "happy",
    "sadness": "sad",
    "anger": "angry",
    "fear": "fearful",
    "surprise": "surprised",
    "disgust": "disgusted",
    "neutral": "neutral",
}


@lru_cache(maxsize=1)
def _load_pipeline():
    """Load once, cache forever. First call is slow (~10s)."""
    return pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True,
        device=-1,  # CPU; change to 0 for GPU
    )


def detect_emotion_from_text(text: str) -> dict:
    """
    Returns:
        {
            "emotion": "happy",
            "confidence": 0.92,
            "raw_scores": {"happy": 0.92, "sad": 0.03, ...}
        }
    """
    text = re.sub(r"\s+", " ", text.strip())
    classifier = _load_pipeline()
    results = classifier(text)[0]  # list of {label, score}

    raw_scores = {}
    for item in results:
        normalized = EMOTION_MAP.get(item["label"].lower(), item["label"].lower())
        raw_scores[normalized] = round(item["score"], 4)

    top = max(results, key=lambda x: x["score"])
    top_emotion = EMOTION_MAP.get(top["label"].lower(), top["label"].lower())
    confidence = round(top["score"], 4)

    return {
        "emotion": top_emotion,
        "confidence": confidence,
        "raw_scores": raw_scores,
    }

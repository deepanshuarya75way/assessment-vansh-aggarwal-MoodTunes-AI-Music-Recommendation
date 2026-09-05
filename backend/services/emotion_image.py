"""
Image-based emotion detection using DeepFace.
DeepFace internally uses a CNN trained on FER-2013 dataset.
Detects: angry, disgust, fear, happy, sad, surprise, neutral.
"""

from deepface import DeepFace
import numpy as np
from PIL import Image
import io
import base64

# Map DeepFace emotion keys → MoodTunes internal labels
EMOTION_MAP = {
    "happy": "happy",
    "sad": "sad",
    "angry": "angry",
    "fear": "fearful",
    "surprise": "surprised",
    "disgust": "disgusted",
    "neutral": "neutral",
}


def detect_emotion_from_image_bytes(image_bytes: bytes) -> dict:
    """
    Args:
        image_bytes: Raw bytes of an uploaded image (JPEG/PNG)

    Returns:
        {
            "emotion": "happy",
            "confidence": 0.87,
            "all_emotions": {"happy": 0.87, "neutral": 0.08, ...}
        }

    Raises:
        ValueError if no face is detected.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img_array = np.array(image)

    try:
        result = DeepFace.analyze(
            img_path=img_array,
            actions=["emotion"],
            enforce_detection=True,  # raises ValueError if no face found
            detector_backend="opencv",
        )
    except ValueError as e:
        raise ValueError(f"No face detected in image: {e}")

    # DeepFace returns a list when multiple faces found — take the first
    analysis = result[0] if isinstance(result, list) else result
    dominant = analysis["dominant_emotion"]
    emotion_scores = analysis["emotion"]  # raw percentages summing to ~100

    # Normalize to 0-1 range
    total = sum(emotion_scores.values()) or 1.0
    normalized = {
        EMOTION_MAP.get(k, k): round(v / total, 4)
        for k, v in emotion_scores.items()
    }

    top_emotion = EMOTION_MAP.get(dominant, dominant)
    confidence = normalized.get(top_emotion, 0.0)

    return {
        "emotion": top_emotion,
        "confidence": confidence,
        "all_emotions": normalized,
    }


def detect_emotion_from_base64(b64_string: str) -> dict:
    """Convenience wrapper for base64-encoded images."""
    image_bytes = base64.b64decode(b64_string)
    return detect_emotion_from_image_bytes(image_bytes)

"""
/api/emotion/* routes

POST /api/emotion/text   — detect emotion from text input
POST /api/emotion/image  — detect emotion from uploaded image
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from backend.models.recommendation import TextEmotionRequest, TextEmotionResponse, ImageEmotionResponse
from backend.services.emotion_text import detect_emotion_from_text
from backend.services.emotion_image import detect_emotion_from_image_bytes

router = APIRouter(prefix="/api/emotion", tags=["Emotion Detection"])


@router.post("/text", response_model=TextEmotionResponse, summary="Detect emotion from text")
async def emotion_from_text(request: TextEmotionRequest):
    """
    Accepts a text string and returns the detected emotion with confidence score.

    - **text**: Any natural language input (e.g. "I'm feeling great today!")
    - **user_id**: Optional user identifier for session tracking
    """
    try:
        result = detect_emotion_from_text(request.text)
        return TextEmotionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text emotion detection failed: {str(e)}")


@router.post("/image", response_model=ImageEmotionResponse, summary="Detect emotion from facial image")
async def emotion_from_image(file: UploadFile = File(...)):
    """
    Accepts an uploaded image (JPEG/PNG) of a face and returns the detected emotion.
    Uses DeepFace CNN (FER-2013 backbone) internally.

    - **file**: Image file upload (multipart/form-data)
    """
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG."
        )

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="Image too large. Max 10MB.")

    try:
        result = detect_emotion_from_image_bytes(image_bytes)
        return ImageEmotionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image emotion detection failed: {str(e)}")

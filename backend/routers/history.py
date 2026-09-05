"""
/api/history/* routes

POST /api/history/         — save a recommendation session
GET  /api/history/{user_id} — get session history for a user
DELETE /api/history/{user_id} — clear history for a user
"""

from fastapi import APIRouter, HTTPException, Query
from backend.models.recommendation import HistoryEntry, HistoryResponse
from backend.config import get_db
from datetime import datetime

router = APIRouter(prefix="/api/history", tags=["Session History"])


@router.post("/", summary="Save a recommendation session")
async def save_history(entry: HistoryEntry):
    """
    Persists a completed recommendation session to MongoDB.
    Called automatically by the frontend after each emotion→music flow.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected.")

    doc = entry.dict()
    doc["timestamp"] = doc.get("timestamp") or datetime.utcnow()
    # Convert Track objects to dicts
    doc["tracks_recommended"] = [t if isinstance(t, dict) else t.dict() for t in doc["tracks_recommended"]]

    result = await db.sessions.insert_one(doc)
    return {"status": "saved", "session_id": str(result.inserted_id)}


@router.get("/{user_id}", response_model=HistoryResponse, summary="Get user session history")
async def get_history(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
):
    """
    Returns past recommendation sessions for a user, newest first.

    - **user_id**: The user's identifier
    - **limit**: Max sessions to return (default 20)
    - **skip**: Pagination offset
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected.")

    cursor = db.sessions.find(
        {"user_id": user_id},
        {"_id": 0},  # exclude MongoDB _id from response
    ).sort("timestamp", -1).skip(skip).limit(limit)

    sessions = await cursor.to_list(length=limit)
    total = await db.sessions.count_documents({"user_id": user_id})

    return HistoryResponse(user_id=user_id, sessions=sessions, total=total)


@router.delete("/{user_id}", summary="Clear user history")
async def delete_history(user_id: str):
    """Removes all session records for a given user."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not connected.")

    result = await db.sessions.delete_many({"user_id": user_id})
    return {"status": "cleared", "deleted_count": result.deleted_count}

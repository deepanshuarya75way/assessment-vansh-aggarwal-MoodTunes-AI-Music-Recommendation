"""
MoodTunes FastAPI Backend
Run: uvicorn backend.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import connect_db, close_db
from backend.routers import emotion, music, history


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="🎵 MoodTunes API",
    description=(
        "Emotion-Based Music Recommendation System.\n\n"
        "## Flow\n"
        "1. Detect emotion from **text** (NLP) or **image** (CNN/FER-2013)\n"
        "2. Get **music recommendations** from LastFM for that emotion\n"
        "3. Sessions are stored in **MongoDB** for history\n\n"
        "Built with FastAPI + Motor (async MongoDB) + DeepFace + HuggingFace Transformers"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(emotion.router)
app.include_router(music.router)
app.include_router(history.router)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Quick health check endpoint."""
    return {"status": "ok", "service": "MoodTunes API", "version": "1.0.0"}


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🎵 Welcome to MoodTunes API",
        "docs": "/docs",
        "health": "/api/health",
    }

from pathlib import Path
import os

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


# moodtunes/
BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly load .env from the project root
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)


MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "moodtunes")

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY", "")
LASTFM_BASE_URL = os.getenv(
    "LASTFM_BASE_URL",
    "https://ws.audioscrobbler.com/2.0/"
)


class Database:
    client: AsyncIOMotorClient = None
    db = None


db_instance = Database()


async def connect_db():
    db_instance.client = AsyncIOMotorClient(MONGODB_URL)
    db_instance.db = db_instance.client[DB_NAME]
    print(f"✅ Connected to MongoDB: {DB_NAME}")


async def close_db():
    if db_instance.client:
        db_instance.client.close()
        print("MongoDB connection closed.")


def get_db():
    return db_instance.db
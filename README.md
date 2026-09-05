# 🎵 MoodTunes — Emotion-Based Music Recommendation System

> **Why listen to the same playlist when your music can match your mood? 🎧**

MoodTunes is an AI-powered music recommendation system that detects a user's emotional state from **text or facial expressions** and generates mood-based music recommendations.

The idea behind MoodTunes came from a simple problem: **I love listening to music, but sometimes my playlists start feeling repetitive and boring.** As an AI/ML student interested in AI applications and backend systems, I thought — *why not build a system that understands how I feel and recommends music accordingly?*

---

## ✨ Features

* 🎭 **Text Emotion Detection** — Detect emotions from user-provided text using Transformer-based NLP.
* 📷 **Facial Emotion Detection** — Analyze facial expressions from uploaded images using DeepFace.
* 🎵 **Emotion-Based Music Recommendation** — Convert detected emotions into suitable music moods.
* 🔗 **Last.fm API Integration** — Fetch music recommendations based on mood tags.
* 💾 **Session History** — Store and retrieve previous recommendation sessions using MongoDB.
* 👤 **User Sessions** — Maintain recommendation history for individual users.
* ⚡ **FastAPI Backend** — REST APIs for emotion detection, music recommendations, and history management.
* 🖥️ **Streamlit Frontend** — Interactive web interface for the complete application.

---

## 🏗️ System Architecture

```text
                         ┌───────────────────┐
                         │       User        │
                         └─────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
               Text Input                   Facial Image
                    │                             │
                    ▼                             ▼
             ┌──────────────┐             ┌──────────────┐
             │ Transformer  │             │   DeepFace   │
             │ NLP Model    │             │ Emotion Model│
             └──────┬───────┘             └──────┬───────┘
                    │                            │
                    └─────────────┬──────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Detected Emotion │
                         │ + Confidence     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Music Engine    │
                         │ Emotion → Mood   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Last.fm API    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Recommended      │
                         │ Tracks           │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
             ┌──────────────┐            ┌──────────────┐
             │  Streamlit   │            │   MongoDB    │
             │  Frontend    │            │   History    │
             └──────────────┘            └──────────────┘
```

---

## 📁 Project Structure

```text
moodtunes/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   └── recommendation.py
│   │
│   ├── routers/
│   │   ├── emotion.py
│   │   ├── music.py
│   │   └── history.py
│   │
│   ├── services/
│   │   ├── emotion_text.py
│   │   ├── emotion_image.py
│   │   └── music_engine.py
│   │
│   └── utils/
│       └── lastfm.py
│
├── frontend/
│   └── app.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Component             | Technology                   |
| --------------------- | ---------------------------- |
| Language              | Python                       |
| Frontend              | Streamlit                    |
| Backend               | FastAPI                      |
| Server                | Uvicorn                      |
| Database              | MongoDB                      |
| Database Driver       | Motor                        |
| Text Emotion          | Transformers / DistilRoBERTa |
| Facial Emotion        | DeepFace                     |
| Deep Learning         | TensorFlow / PyTorch         |
| Music API             | Last.fm                      |
| API Communication     | REST API                     |
| Environment Variables | python-dotenv                |

---

## 🧠 Emotion Detection

MoodTunes supports two ways of detecting emotions.

### 1. Text-Based Emotion Detection

The user describes their current mood using text.

Example:

```text
I just got selected for my dream internship and I am extremely excited!
```

The NLP model analyzes the text and predicts an emotion such as:

```text
happy
sad
angry
fearful
surprised
disgusted
neutral
excited
```

### 2. Facial Emotion Detection

Users can upload a facial image.

MoodTunes uses DeepFace to analyze facial expressions and estimate the user's emotional state.

---

## 🎵 Music Recommendation

After detecting the emotion, MoodTunes maps it to a suitable Last.fm music tag.

| Emotion   | Music Tag   |
| --------- | ----------- |
| Happy     | happy       |
| Sad       | sad         |
| Angry     | aggressive  |
| Fearful   | dark        |
| Surprised | uplifting   |
| Disgusted | melancholic |
| Neutral   | chill       |
| Excited   | energetic   |

The corresponding tracks are then retrieved from the Last.fm API and displayed in the Streamlit interface.

---

## 🔄 Application Flow

```text
User
  ↓
Choose Input Method
  ↓
Text / Facial Image
  ↓
Emotion Detection
  ↓
Emotion + Confidence Score
  ↓
Music Recommendation API
  ↓
Emotion → Music Tag Mapping
  ↓
Last.fm API
  ↓
Recommended Tracks
  ↓
Save Recommendation Session
  ↓
MongoDB
```

---

## 🔌 API Endpoints

| Method | Endpoint                 | Description                    |
| ------ | ------------------------ | ------------------------------ |
| POST   | `/api/emotion/text`      | Detect emotion from text       |
| POST   | `/api/emotion/image`     | Detect emotion from an image   |
| POST   | `/api/music/recommend`   | Generate music recommendations |
| POST   | `/api/history/`          | Save recommendation session    |
| GET    | `/api/history/{user_id}` | Get user session history       |
| DELETE | `/api/history/{user_id}` | Clear user history             |
| GET    | `/api/health`            | Check backend health           |

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/MoodTunes-AI-Music-Recommendation.git
cd MoodTunes-AI-Music-Recommendation
```

### 2. Create a Virtual Environment

Python 3.11 is recommended.

```bash
python -m venv venv311
```

### 3. Activate the Environment

#### Windows

```bash
venv311\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

Create a `.env` file in the project root.

Use `.env.example` as a template:

```env
MONGODB_URL=your_mongodb_connection_string
DB_NAME=moodtunes
LASTFM_API_KEY=your_lastfm_api_key
LASTFM_BASE_URL=https://ws.audioscrobbler.com/2.0/
```

> ⚠️ **Never upload `.env`, API keys, database credentials, or passwords to GitHub.**

---

## 🚀 Running the Application

### Start the Backend

Run this command from the **project root**:

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

FastAPI Swagger documentation:

```text
http://localhost:8000/docs
```

### Start the Frontend

Open a new terminal:

```bash
venv311\Scripts\activate
streamlit run frontend/app.py
```

---

## 🗄️ Database

MoodTunes uses MongoDB to store recommendation sessions.

Example session:

```json
{
  "user_id": "guest",
  "input_mode": "text",
  "detected_emotion": "happy",
  "confidence": 0.95,
  "tracks_recommended": [],
  "timestamp": "2026-09-05T00:00:00"
}
```

This allows users to view their previous recommendation sessions through the History section.

---

## 🔒 Security

Sensitive configuration is handled through environment variables.

The following files should **never** be committed:

```text
.env
venv/
venv311/
```

The repository only contains `.env.example` with placeholder values.

---

## 💡 Why I Built MoodTunes

I love listening to music, but after repeatedly listening to the same playlists, they can sometimes start feeling boring.

That made me think:

> **"What if my music could understand my mood?"**

As an AI/ML student interested in building practical AI applications and backend systems, I decided to turn that simple idea into a working project.

MoodTunes combines:

**AI + Emotion Detection + Backend Development + APIs + Database + Music Recommendation**

into one end-to-end application.

---

## 🚧 Future Improvements

* 🎧 Spotify integration
* 🤖 Advanced personalized recommendation models
* 🧠 Recommendations based on individual listening history
* 📊 Emotion and listening analytics dashboard
* 👤 User authentication
* ☁️ Cloud deployment
* 🎙️ Voice-based emotion detection
* 📷 Real-time webcam emotion detection

---

## 👨‍💻 Author

**Vansh Aggarwal**

B.Tech — Artificial Intelligence & Machine Learning

Interested in:

* Artificial Intelligence
* Machine Learning
* Backend Development
* Software Development
* AI-Powered Applications

---

⭐ If you find MoodTunes interesting, consider giving the repository a star!

"""
MoodTunes — Streamlit Frontend
Run: streamlit run frontend/app.py
Expects backend running at http://localhost:8000
"""

import streamlit as st
import requests
import base64
import json
from datetime import datetime

# ─────────────────────────── CONFIG ────────────────────────────
API_BASE = "http://localhost:8000"

EMOTION_EMOJI = {
    "happy":     "😊",
    "sad":       "😢",
    "angry":     "😠",
    "fearful":   "😨",
    "surprised": "😲",
    "disgusted": "🤢",
    "neutral":   "😐",
    "excited":   "🤩",
}

EMOTION_COLOR = {
    "happy":     "#FFD700",
    "sad":       "#6CA0DC",
    "angry":     "#FF4444",
    "fearful":   "#9B59B6",
    "surprised": "#F39C12",
    "disgusted": "#27AE60",
    "neutral":   "#95A5A6",
    "excited":   "#FF6B35",
}

# ─────────────────────────── HELPERS ────────────────────────────

def api_get(path: str) -> dict | None:
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(path: str, json_data: dict = None, files=None) -> dict | None:
    try:
        r = requests.post(
            f"{API_BASE}{path}",
            json=json_data,
            files=files,
            timeout=60,  # models can take a moment to load first time
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
        return None
    except requests.exceptions.HTTPError as e:
        detail = e.response.json().get("detail", str(e))
        st.error(f"API Error {e.response.status_code}: {detail}")
        return None
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None


def save_session(user_id, input_mode, emotion, confidence, tracks):
    """Silently save session to MongoDB via API."""
    payload = {
        "user_id": user_id,
        "input_mode": input_mode,
        "detected_emotion": emotion,
        "confidence": confidence,
        "tracks_recommended": [
            {"name": t["name"], "artist": t["artist"], "url": t.get("url"), "image": t.get("image"), "listeners": t.get("listeners")}
            for t in tracks
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }
    requests.post(f"{API_BASE}/api/history/", json=payload, timeout=10)


def render_track_card(track: dict, idx: int):
    """Render a single track as a styled card."""
    with st.container():
        cols = st.columns([1, 6, 2])
        with cols[0]:
            st.markdown(f"**#{idx}**")
        with cols[1]:
            name = track.get("name", "Unknown")
            artist = track.get("artist", "Unknown")
            url = track.get("url", "#")
            st.markdown(f"**[{name}]({url})**  \n*{artist}*")
        with cols[2]:
            listeners = track.get("listeners", 0)
            if listeners:
                st.caption(f"👥 {listeners:,}")


# ─────────────────────────── PAGES ────────────────────────────

def page_detect():
    st.header("🎭 Detect Your Mood")
    st.caption("Tell us how you feel — by typing or showing your face — and we'll build your playlist.")

    user_id = st.session_state.get("user_id", "guest")

    # ── Input mode tabs ──
    tab_text, tab_image = st.tabs(["💬 Text Input", "📷 Facial Image"])

    # ── TEXT TAB ──
    with tab_text:
        st.subheader("How are you feeling right now?")
        text_input = st.text_area(
            "Describe your mood, thoughts, or anything on your mind:",
            placeholder="e.g. I just got some really exciting news and can't stop smiling!",
            height=120,
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            detect_text_btn = st.button("🔍 Detect Emotion", use_container_width=True, key="text_detect")

        if detect_text_btn:
            if not text_input.strip():
                st.warning("Please enter some text first.")
            else:
                with st.spinner("Analysing your text with NLP..."):
                    result = api_post("/api/emotion/text", json_data={"text": text_input, "user_id": user_id})

                if result:
                    st.session_state["last_emotion"] = result["emotion"]
                    st.session_state["last_confidence"] = result["confidence"]
                    st.session_state["last_mode"] = "text"

                    emotion = result["emotion"]
                    confidence = result["confidence"]
                    emoji = EMOTION_EMOJI.get(emotion, "🎵")
                    color = EMOTION_COLOR.get(emotion, "#888")

                    st.markdown(
                        f"""
                        <div style="background:{color}22; border-left: 4px solid {color};
                                    padding: 16px; border-radius: 8px; margin-top: 12px;">
                            <h2 style="margin:0;">{emoji} {emotion.capitalize()}</h2>
                            <p style="margin:4px 0 0 0; color:#666;">Confidence: {confidence*100:.1f}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Emotion bar chart
                    raw = result.get("raw_scores", {})
                    if raw:
                        import pandas as pd
                        df = pd.DataFrame({"Emotion": list(raw.keys()), "Score": list(raw.values())})
                        df = df.sort_values("Score", ascending=True)
                        st.bar_chart(df.set_index("Emotion"))

                    st.success("Emotion detected! Head to the **Playlist** tab to get your music. 🎵")

    # ── IMAGE TAB ──
    with tab_image:
        st.subheader("Show us your face")
        st.caption("Upload a clear photo of your face. Works best with good lighting and a forward-facing pose.")

        uploaded = st.file_uploader("Upload facial image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

        if uploaded:
            st.image(uploaded, caption="Your uploaded image", width=300)

            if st.button("🔍 Detect Emotion from Face", use_container_width=False, key="img_detect"):
                with st.spinner("Running FER-2013 CNN model on your face..."):
                    files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                    result = api_post("/api/emotion/image", files=files)

                if result:
                    st.session_state["last_emotion"] = result["emotion"]
                    st.session_state["last_confidence"] = result["confidence"]
                    st.session_state["last_mode"] = "image"

                    emotion = result["emotion"]
                    confidence = result["confidence"]
                    emoji = EMOTION_EMOJI.get(emotion, "🎵")
                    color = EMOTION_COLOR.get(emotion, "#888")

                    st.markdown(
                        f"""
                        <div style="background:{color}22; border-left: 4px solid {color};
                                    padding: 16px; border-radius: 8px; margin-top: 12px;">
                            <h2 style="margin:0;">{emoji} {emotion.capitalize()}</h2>
                            <p style="margin:4px 0 0 0; color:#666;">Confidence: {confidence*100:.1f}%</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # All emotion scores
                    all_e = result.get("all_emotions", {})
                    if all_e:
                        import pandas as pd
                        df = pd.DataFrame({"Emotion": list(all_e.keys()), "Score": list(all_e.values())})
                        df = df.sort_values("Score", ascending=True)
                        st.bar_chart(df.set_index("Emotion"))

                    st.success("Emotion detected! Head to the **Playlist** tab to get your music. 🎵")


def page_playlist():
    st.header("🎵 Your Playlist")

    user_id = st.session_state.get("user_id", "guest")
    emotion = st.session_state.get("last_emotion", None)
    confidence = st.session_state.get("last_confidence", 0.0)
    mode = st.session_state.get("last_mode", "text")

    # Manual override
    st.subheader("Current Mood")
    if emotion:
        emoji = EMOTION_EMOJI.get(emotion, "🎵")
        color = EMOTION_COLOR.get(emotion, "#888")
        st.markdown(
            f'<span style="background:{color}33; padding:6px 16px; border-radius:20px; font-size:1.1em;">'
            f'{emoji} <b>{emotion.capitalize()}</b> — {confidence*100:.0f}% confidence</span>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No emotion detected yet. Go to **Detect Mood** first, or pick one manually below.")

    # Manual emotion override
    with st.expander("🎛️ Override emotion manually"):
        manual_emotion = st.selectbox(
            "Choose emotion:",
            options=list(EMOTION_EMOJI.keys()),
            format_func=lambda e: f"{EMOTION_EMOJI[e]} {e.capitalize()}",
        )
        if st.button("Use this emotion"):
            emotion = manual_emotion
            confidence = 1.0
            mode = "manual"
            st.session_state["last_emotion"] = emotion
            st.session_state["last_confidence"] = confidence
            st.session_state["last_mode"] = mode
            st.rerun()

    st.divider()

    limit = st.slider("Number of tracks", min_value=5, max_value=30, value=10, step=5)

    if st.button("🎶 Generate Playlist", use_container_width=True, type="primary", disabled=not emotion):
        with st.spinner("Fetching tracks from LastFM..."):
            result = api_post(
                "/api/music/recommend",
                json_data={"emotion": emotion, "user_id": user_id, "limit": limit},
            )

        if result:
            label = result.get("playlist_label", "Your Playlist")
            tracks = result.get("tracks", [])
            tag = result.get("mood_tag", "")

            st.subheader(label)
            st.caption(f"LastFM tag: `{tag}` · {len(tracks)} tracks")
            st.divider()

            for i, track in enumerate(tracks, 1):
                render_track_card(track, i)
                st.divider()

            # Auto-save session
            try:
                save_session(user_id, mode, emotion, confidence, tracks)
            except Exception:
                pass  # silently fail

            st.session_state["last_tracks"] = tracks


def page_history():
    st.header("📋 Session History")

    user_id = st.session_state.get("user_id", "guest")
    st.caption(f"Showing history for user: **{user_id}**")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear History", type="secondary"):
            r = requests.delete(f"{API_BASE}/api/history/{user_id}", timeout=10)
            if r.ok:
                st.success(f"Cleared {r.json().get('deleted_count', 0)} sessions.")
                st.rerun()

    data = api_get(f"/api/history/{user_id}?limit=20")

    if data is None:
        return

    sessions = data.get("sessions", [])
    total = data.get("total", 0)

    if not sessions:
        st.info("No sessions yet. Detect your mood and generate a playlist to get started!")
        return

    st.caption(f"Total sessions: {total}")

    for s in sessions:
        ts = s.get("timestamp", "")
        emotion = s.get("detected_emotion", "?")
        confidence = s.get("confidence", 0)
        mode = s.get("input_mode", "?")
        tracks = s.get("tracks_recommended", [])
        emoji = EMOTION_EMOJI.get(emotion, "🎵")

        with st.expander(f"{emoji} {emotion.capitalize()} · {mode} input · {ts[:16] if ts else ''}"):
            st.markdown(f"**Confidence:** {confidence*100:.0f}%")
            st.markdown(f"**Tracks recommended:** {len(tracks)}")
            for t in tracks[:5]:
                st.markdown(f"- {t.get('name', '?')} — *{t.get('artist', '?')}*")
            if len(tracks) > 5:
                st.caption(f"...and {len(tracks)-5} more")


def page_settings():
    st.header("⚙️ Settings")

    st.subheader("User Profile")
    user_id = st.text_input(
        "User ID (your name or any identifier):",
        value=st.session_state.get("user_id", "guest"),
    )
    if st.button("Save"):
        st.session_state["user_id"] = user_id
        st.success(f"User ID set to: **{user_id}**")

    st.divider()
    st.subheader("Backend Health")
    if st.button("Check API Health"):
        result = api_get("/api/health")
        if result:
            st.json(result)

    st.divider()
    st.subheader("About MoodTunes")
    st.markdown("""
    **MoodTunes** detects your emotion from text or facial expressions and generates a personalized music playlist.

    | Component | Technology |
    |---|---|
    | Text Emotion | DistilRoBERTa (HuggingFace) |
    | Face Emotion | DeepFace CNN (FER-2013 dataset) |
    | Music Data | LastFM API |
    | Backend | FastAPI + Uvicorn |
    | Database | MongoDB (Motor async) |
    | Frontend | Streamlit |
    """)


# ─────────────────────────── LAYOUT ────────────────────────────

def main():
    st.set_page_config(
        page_title="MoodTunes",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Session defaults
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = "guest"

    # Sidebar navigation
    with st.sidebar:
        st.markdown("# 🎵 MoodTunes")
        st.caption("Emotion-Powered Music")
        st.divider()

        page = st.radio(
            "Navigate",
            options=["🎭 Detect Mood", "🎵 Playlist", "📋 History", "⚙️ Settings"],
            label_visibility="collapsed",
        )

        st.divider()
        emotion = st.session_state.get("last_emotion")
        if emotion:
            emoji = EMOTION_EMOJI.get(emotion, "🎵")
            color = EMOTION_COLOR.get(emotion, "#888")
            st.markdown(
                f'<p style="background:{color}22; padding:8px 12px; border-radius:8px; margin:0;">'
                f'Current mood: {emoji} <b>{emotion.capitalize()}</b></p>',
                unsafe_allow_html=True,
            )

        st.divider()
        st.caption(f"👤 {st.session_state.get('user_id', 'guest')}")
        st.caption("Backend: `localhost:8000`")

    # Route pages
    if page == "🎭 Detect Mood":
        page_detect()
    elif page == "🎵 Playlist":
        page_playlist()
    elif page == "📋 History":
        page_history()
    elif page == "⚙️ Settings":
        page_settings()


if __name__ == "__main__":
    main()

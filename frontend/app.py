import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://localhost:8000/generate-series"

st.set_page_config(
    page_title="ArcEngine",
    layout="wide"
)

# ------------------------------
# ZONE 1: CONTROL PANEL (SIDEBAR)
# ------------------------------

st.sidebar.title("ArcEngine Control Panel")

concept = st.sidebar.text_area(
    "Core Story Concept",
    placeholder="A hacker finds a file predicting crimes..."
)

moods = [
    "Gritty Cyberpunk",
    "Lighthearted Comedy",
    "True Crime",
    "Sci-Fi Thriller",
    "Dark Mystery",
    "Custom..."
]

selected_mood = st.sidebar.selectbox("Director's Mood", moods)

if selected_mood == "Custom...":
    mood = st.sidebar.text_input("Enter Custom Mood")
else:
    mood = selected_mood

generate = st.sidebar.button("Generate Series Arc")

# ------------------------------
# MAIN PAGE TITLE
# ------------------------------

st.title("🎬 ArcEngine Episodic Intelligence")

# ------------------------------
# API CALL
# ------------------------------

data = None

if generate and concept:

    with st.spinner("Generating series..."):

        response = requests.post(
            API_URL,
            json={
                "concept": concept,
                "mood": mood
            }
        )

        data = response.json()

# ------------------------------
# ZONE 2: ANALYTICS DASHBOARD
# ------------------------------

if data:

    st.header("Analytics Dashboard")

    episodes = data["episodes"]

    emotion_scores = []
    cliff_scores = []

    for ep in episodes:
        emotion_scores.append(ep["emotion_intensity"])
        cliff_scores.append(ep["cliffhanger_score"])

    avg_emotion = sum(emotion_scores) / len(emotion_scores)
    avg_cliff = sum(cliff_scores) / len(cliff_scores)

    brand_safety = data.get("brand_safety", "Safe")

    col1, col2, col3 = st.columns(3)

    col1.metric("Avg Emotion", round(avg_emotion, 2))
    col2.metric("Cliffhanger Score", round(avg_cliff, 2))
    col3.metric("Brand Safety", brand_safety)

    # Narrative tension graph

    df = pd.DataFrame({
        "Episode": list(range(1, len(emotion_scores)+1)),
        "Emotion": emotion_scores,
        "Cliffhanger": cliff_scores
    })

    fig = px.line(
        df,
        x="Episode",
        y=["Emotion", "Cliffhanger"],
        markers=True,
        title="Narrative Tension Curve"
    )

    st.plotly_chart(fig, width="stretch")

# ------------------------------
# ZONE 3: SCRIPT BREAKDOWN
# ------------------------------

    st.header("Episode Script Breakdown")

    for ep in episodes:

        with st.expander(f"Episode {ep['episode_number']}"):

            st.subheader("Title")
            st.write(ep["title"])

            st.subheader("Hook")
            st.write(ep.get("open_loop", "N/A"))

            st.subheader("Summary")
            st.write(ep["summary"])

            st.subheader("Cliffhanger")
            st.write(ep.get("cliffhanger_action", "N/A"))

            st.subheader("Emotion Tag")
            st.write(ep["emotion_tag"])

            if ep.get("continuity_warning"):
                st.warning(ep.get("continuity_warning"))
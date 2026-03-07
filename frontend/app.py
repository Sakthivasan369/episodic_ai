import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json

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

# Number of Episodes (5-8)
num_episodes = st.sidebar.number_input(
    "Number of Episodes",
    min_value=5,
    max_value=8,
    value=5,
    step=1
)

# Director's Mood
mood_presets = [
    "Gritty Cyberpunk",
    "Lighthearted Comedy",
    "True Crime",
    "Sci-Fi Thriller",
    "Dark Mystery"
]

selected_preset = st.sidebar.selectbox("Mood Presets", ["Custom"] + mood_presets)

if selected_preset == "Custom":
    mood = st.sidebar.text_input("Director's Mood", placeholder="Enter custom mood name...")
else:
    mood = st.sidebar.text_input("Director's Mood", value=selected_preset)

generate = st.sidebar.button("Generate Series Arc")

# ------------------------------
# MAIN PAGE TITLE
# ------------------------------

st.title("🎬 ArcEngine Episodic Intelligence")

# ------------------------------
# API CALL
# ------------------------------

# Initialize session state for data if not present
if "data" not in st.session_state:
    st.session_state.data = None

if generate and concept:

    with st.spinner("Generating series..."):

        response = requests.post(
            API_URL,
            json={
                "concept": concept,
                "mood": mood,
                "num_episodes": num_episodes
            }
        )

        if response.status_code == 200:
            st.session_state.data = response.json()
        else:
            error_data = response.json()
            error_detail = error_data.get("detail", "Unknown error occurred")
            st.error(f"API Error ({response.status_code}): {error_detail}")

# Download Button in Sidebar if data exists
if st.session_state.data:
    st.sidebar.divider()
    st.sidebar.subheader("Export Data")
    
    json_string = json.dumps(st.session_state.data, indent=2)
    st.sidebar.download_button(
        label="Download Series Arc (JSON)",
        data=json_string,
        file_name="series_arc.json",
        mime="application/json"
    )

# ------------------------------
# ZONE 2: ANALYTICS DASHBOARD
# ------------------------------

data = st.session_state.data

if data:

    st.header("Analytics Dashboard")

    episodes = data.get("episodes", [])
    
    if not episodes:
        st.warning("No episodes generated. Please check the API logs.")
    else:
        emotion_scores = []
        cliff_scores = []

        for ep in episodes:
            emotion_scores.append(ep.get("emotion_intensity", 0))
            cliff_scores.append(ep.get("cliffhanger_score", 0))

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

            with st.expander(f"Episode {ep.get('episode_number', 'N/A')}"):

                st.subheader("Title")
                st.write(ep.get("title", "N/A"))

                st.subheader("Hook")
                st.write(ep.get("open_loop", "N/A"))

                st.subheader("Summary")
                st.write(ep.get("summary", "N/A"))

                st.subheader("Cliffhanger")
                st.write(ep.get("cliffhanger_action", "N/A"))

                st.subheader("Emotion Tag")
                st.write(ep.get("emotion_tag", "N/A"))

                st.subheader("SEO Hashtags")
                hashtags = ep.get("seo_hashtags", [])
                if hashtags:
                    st.write(" ".join([f"#{tag}" if not tag.startswith("#") else tag for tag in hashtags]))
                else:
                    st.write("N/A")
                
                # Show Script Doctor Advice if available
                advice = ep.get("director_advice")
                if advice:
                    st.info(f"**Director's Advice:** {advice}")

                if ep.get("continuity_warning"):
                    st.warning(ep.get("continuity_warning"))

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os

BASE_URL = os.environ.get("API_URL", "http://localhost:8000")
API_URL = f"{BASE_URL}/generate-series"
HEALTH_URL = f"{BASE_URL}/"

st.set_page_config(
    page_title="ArcEngine",
    layout="wide"
)

# ------------------------------
# ZONE 1: CONTROL PANEL (SIDEBAR)
# ------------------------------

st.sidebar.title("ArcEngine Control Panel")

# Health Check Status
try:
    health_resp = requests.get(HEALTH_URL, timeout=5)
    if health_resp.status_code == 200:
        st.sidebar.success("🟢 Backend Online")
    else:
        st.sidebar.error("🔴 Backend Error")
except:
    st.sidebar.error("🔴 Backend Offline")

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
# JUDGES INFORMATION BOX
# ------------------------------

with st.expander("ℹ️ Technical Implementation Details (For Judges)"):
    st.markdown("""
    ### Our Engineering Process & Full Features
    Throughout the development of **ArcEngine**, we implemented and established several advanced AI features that are fully functional in our local environment:
    
    *   **🎭 Emotion Analysis:** Uses `j-hartmann/emotion-english-distilroberta-base` to analyze the psychological tone of each episode.
    *   **📈 Cliffhanger Scoring:** Uses `facebook/bart-large-mnli` (Zero-shot classification) to quantify narrative tension and retention probability.
    *   **🏷️ SEO & Hashtag Engine:** BERT-based Named Entity Recognition (NER) to generate relevant viral tags.
    *   **🩺 DSPy Script Doctor:** A self-correcting logic layer that analyzes low-tension episodes and provides AI-driven "Director Advice" to improve the script.
    *   **🛡️ Brand Safety:** Toxic-BERT implementation to ensure content complies with platform guidelines.
    *   **🔄 Character Continuity:** Maintains consistent protagonist traits and primary goals across the entire generated arc.

    **Note on Hosted Version:**
    As students utilizing free-tier hosting (Railway/HF), we encountered strict **RAM limits (512MB - 1GB)**. Loading multiple heavy Transformer models (BART, BERT, RoBERTa) simultaneously exceeds these limits. 
    
    In this hosted demonstration, we have offloaded heavy LLM tasks to Groq's API and used lightweight logic for analytics to ensure stability. 
    
    **Please see the sample below to view the full JSON output from our local version with all models active.**
    """)
    
    try:
        with open("series_arc.json", "r") as f:
            sample_data = json.load(f)
        st.subheader("Sample Full Output (Local Version)")
        st.json(sample_data)
    except Exception as e:
        st.info("Sample output file (series_arc.json) not found in root.")

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
            },
            timeout=600
        )

        if response.status_code == 200:
            st.session_state.data = response.json()
        else:
            error_data = response.json()
            error_detail = error_data.get("detail", "Unknown error occurred")
            st.error(f"API Error ({response.status_code}): {error_detail}")

# Download Buttons in Sidebar if data exists
if st.session_state.data:
    st.sidebar.divider()
    st.sidebar.subheader("Export Data")
    
    # JSON Export
    json_string = json.dumps(st.session_state.data, indent=2)
    st.sidebar.download_button(
        label="Download as JSON",
        data=json_string,
        file_name="series_arc.json",
        mime="application/json"
    )

    # Text Export
    data = st.session_state.data
    text_content = f"SERIES TITLE: {data.get('series_title', 'N/A')}\n"
    text_content += f"MOOD: {mood}\n"
    text_content += "="*30 + "\n\n"
    
    for ep in data.get("episodes", []):
        text_content += f"EPISODE {ep.get('episode_number')}: {ep.get('click_title', ep.get('title'))}\n"
        text_content += f"VIRAL HOOK: {ep.get('viral_hook')}\n"
        text_content += f"SUMMARY: {ep.get('summary')}\n"
        text_content += f"CLIFFHANGER: {ep.get('cliffhanger_action')}\n"
        if ep.get('director_advice'):
            text_content += f"DIRECTOR ADVICE: {ep.get('director_advice')}\n"
        text_content += "-"*20 + "\n\n"

    st.sidebar.download_button(
        label="Download as TXT",
        data=text_content,
        file_name="series_arc.txt",
        mime="text/plain"
    )

# ------------------------------
# ZONE 3: SCRIPT BREAKDOWN
# ------------------------------

data = st.session_state.data

if data:

    st.header("Episode Script Breakdown")

    episodes = data.get("episodes", [])
    
    if not episodes:
        st.warning("No episodes generated. Please check the API logs.")
    else:
        for ep in episodes:

            with st.expander(f"Episode {ep.get('episode_number', 'N/A')}"):

                st.subheader("Viral Title")
                st.write(ep.get("click_title", "N/A"))

                st.subheader("Viral Hook")
                st.write(ep.get("viral_hook", "N/A"))

                st.subheader("Title (Original)")
                st.write(ep.get("title", "N/A"))

                st.subheader("Hook (Original)")
                st.write(ep.get("open_loop", "N/A"))

                st.subheader("Summary")
                st.write(ep.get("summary", "N/A"))

                st.subheader("Cliffhanger")
                st.write(ep.get("cliffhanger_action", "N/A"))

                st.subheader("Emotion Tag")
                st.write(ep.get("emotion_tag", "N/A"))
                
                # Show Script Doctor Advice if available
                advice = ep.get("director_advice")
                if advice:
                    st.info(f"**Director's Advice:** {advice}")

                if ep.get("continuity_warning"):
                    st.warning(ep.get("continuity_warning"))

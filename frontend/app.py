import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import json
import os

BASE_URL = os.environ.get("API_URL", "http://localhost:8001")
API_URL = f"{BASE_URL}/generate-series"

st.set_page_config(
    page_title="ArcEngine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a rich, appealing UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .stButton>button {
        background: linear-gradient(135deg, #F97316 0%, #EA580C 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(249, 115, 22, 0.5);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #F97316, #FCD34D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #1E293B;
        border-radius: 8px;
        font-weight: 600;
        border: 1px solid #334155;
    }
    
    /* Card-like containers for script breakdown */
    .script-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    
    .tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background-color: #334155;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        color: #94A3B8;
    }
    
    .gradient-text {
        background: linear-gradient(45deg, #F97316, #FCD34D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar layout
with st.sidebar:
    st.markdown("<h2 class='gradient-text'>🎬 ArcEngine</h2>", unsafe_allow_html=True)
    st.caption("AI-Powered Episodic Intelligence")
    st.divider()
    
    concept = st.text_area(
        "🧠 Core Story Concept",
        placeholder="A hacker finds a file predicting crimes...",
        help="Briefly describe the main plot or premise of your series."
    )
    
    num_episodes = st.slider("🎞️ Number of Episodes", min_value=5, max_value=8, value=5)
    
    mood_presets = [
        "Gritty Cyberpunk",
        "Lighthearted Comedy",
        "True Crime",
        "Sci-Fi Thriller",
        "Dark Mystery",
        "Custom"
    ]
    selected_preset = st.selectbox("🎭 Director's Mood", mood_presets)
    
    if selected_preset == "Custom":
        mood = st.text_input("Custom Mood", placeholder="Enter custom mood name...")
    else:
        mood = selected_preset
        
    generate = st.button("🚀 Generate Series Arc", use_container_width=True)

# Main Title Area
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Design Your Next <span class='gradient-text'>Viral Series</span></h1>", unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = None

if generate and concept:
    with st.status("🧠 ArcEngine is crafting your narrative...", expanded=True) as status:
        st.write("Analyzing concept...")
        try:
            response = requests.post(
                API_URL,
                json={"concept": concept, "mood": mood, "num_episodes": num_episodes},
                timeout=600
            )
            if response.status_code == 200:
                st.session_state.data = response.json()
                status.update(label="Series generated successfully!", state="complete", expanded=False)
            else:
                error_detail = response.json().get("detail", "Unknown error")
                status.update(label=f"Error: {error_detail}", state="error", expanded=True)
        except Exception as e:
             status.update(label=f"Connection Error: {str(e)}", state="error", expanded=True)

data = st.session_state.data

if data:
    st.success(f"**Series Title:** {data.get('series_title', 'Untitled')}")
    
    # Export options in a nice row
    st.sidebar.divider()
    st.sidebar.subheader("📥 Export Data")
    
    # Text Export prep
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

    col_dl1, col_dl2 = st.sidebar.columns(2)
    with col_dl1:
        st.download_button("JSON", json.dumps(data, indent=2), "series_arc.json", "application/json", use_container_width=True)
    with col_dl2:
        st.download_button("TXT", text_content, "series_arc.txt", "text/plain", use_container_width=True)

    # Tabs for modern layout
    tab1, tab2 = st.tabs(["📊 Analytics Dashboard", "📝 Script Breakdown"])
    
    episodes = data.get("episodes", [])
    
    with tab1:
        if not episodes:
            st.warning("No episodes generated.")
        else:
            emotion_scores = [ep.get("emotion_intensity", 0) for ep in episodes]
            cliff_scores = [ep.get("cliffhanger_score", 0) for ep in episodes]
            
            avg_emotion = sum(emotion_scores) / len(emotion_scores) if emotion_scores else 0
            avg_cliff = sum(cliff_scores) / len(cliff_scores) if cliff_scores else 0
            
            # Key Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Episodes", len(episodes))
            m2.metric("Avg Emotion Intensity", f"{avg_emotion:.2f}")
            m3.metric("Avg Cliffhanger Score", f"{avg_cliff:.2f}")
            
            st.divider()
            
            # Interactive Chart
            st.subheader("📈 Narrative Tension Curve")
            df = pd.DataFrame({
                "Episode": [f"Ep {i+1}" for i in range(len(emotion_scores))],
                "Emotion Intensity": emotion_scores,
                "Cliffhanger Score": cliff_scores
            })
            
            fig = px.line(
                df, x="Episode", y=["Emotion Intensity", "Cliffhanger Score"],
                markers=True,
                color_discrete_sequence=["#F97316", "#3B82F6"]
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#F8FAFC"),
                legend_title_text="Metrics",
                hovermode="x unified"
            )
            fig.update_xaxes(showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="#334155")
            
            st.plotly_chart(fig, use_container_width=True)
            
    with tab2:
        for ep in episodes:
            with st.expander(f"🎬 Episode {ep.get('episode_number')}: {ep.get('click_title', ep.get('title'))}", expanded=(ep.get('episode_number')==1)):
                
                st.markdown(f'''
                <div class="script-card">
                    <h4>🔥 The Hook</h4>
                    <p><em>"{ep.get('viral_hook', ep.get('open_loop', 'N/A'))}"</em></p>
                    <hr style="border-color: #334155;">
                    <h4>📜 Summary</h4>
                    <p>{ep.get('summary', 'N/A')}</p>
                    <hr style="border-color: #334155;">
                    <h4>⚡ Cliffhanger</h4>
                    <p>{ep.get('cliffhanger_action', 'N/A')}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Tags
                st.markdown("**Tags:**")
                tags_html = ""
                if ep.get('emotion_tag'):
                    tags_html += f"<span class='tag'>🎭 {ep.get('emotion_tag')}</span>"
                for tag in ep.get("seo_hashtags", []):
                    tags_html += f"<span class='tag'>{tag}</span>"
                st.markdown(tags_html, unsafe_allow_html=True)
                st.write("") # small spacing
                
                # Alerts
                if ep.get("director_advice"):
                    st.info(f"💡 **Director's Advice:** {ep.get('director_advice')}")
                if not ep.get("is_brand_safe", True):
                    st.error(f"🚨 **Safety Warning:** {ep.get('safety_warning', 'Content flagged.')}")
                if ep.get("continuity_warning"):
                    st.warning(f"⚠️ **Continuity:** {ep.get('continuity_warning')}")

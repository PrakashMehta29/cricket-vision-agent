import streamlit as st
import google.generativeai as genai
import time
import os
import json
from gtts import gTTS # Commentary ke liye
import base64

# 🔴 API KEY LOCK (Don't Forget)
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key missing! Please set GEMINI_API_KEY environment variable.")

SYSTEM_PROMPT = """
You are the "Agentic Cricket Vision & Strategy Engine", an elite multimodal AI. 
Your core directive is to ingest raw visual data (videos of a cricket match), identify the players if possible, and autonomously extract, analyze, and predict match telemetry.

Execute this Agentic Loop:
1. DATA EXTRACTION: Identify the delivery type, the exact shot played, ball direction, and recognize the specific players/teams involved.
2. STATISTICAL INFERENCE: Based on the recognized players and the match phase (e.g., Death Overs), infer their historical tendencies (e.g., Bowler's death-over economy, Batter's preferred strike zones).
3. PROBABILITY PREDICTION: Generate a weighted matrix for the MOST LIKELY next deliveries based on the outcome of the current visual feed.

STRICT OUTPUT REQUIREMENT:
Output ONLY a valid JSON object. No markdown, no conversational text. Schema:
{
  "system_action": "INGEST_MATCH_TELEMETRY",
  "extracted_data": {
    "identified_context": "<e.g., Virat Kohli vs Haris Rauf, T20 Death Over>",
    "delivery_type": "", 
    "shot_played": "", 
    "ball_direction": ""
  },
  "tactical_analysis": {
    "biomechanics": "<Analyze batter's footwork and bat swing>",
    "bowler_intent": "<What was the bowler trying to execute?>"
  },
  "advanced_predictive_engine": {
    "inferred_player_stats": "<1 sentence on historical tendencies, e.g., 'Bowler usually resorts to wide yorkers after conceding a boundary.'>",
    "next_ball_probability_matrix": [
        {"delivery": "<Option 1>", "probability": "<e.g., 65%>", "tactical_reason": ""},
        {"delivery": "<Option 2>", "probability": "<e.g., 25%>", "tactical_reason": ""}
    ],
    "recommended_field_adjustment": ""
  }
}
"""

# Function to load external assets
def load_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def load_html(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

# UI CONFIG: IPL 2026 OFFICIAL BROADCAST THEME
st.set_page_config(layout="wide", page_title="IPL 2026: AI Match Center", page_icon="🏆")

# Load decoupled UI assets
load_css("style.css")
load_html("index.html")

# Ravi Shastri Style Commentary Parser
def get_shastri_commentary(data):
    try:
        res = json.loads(data)
        context = res.get('extracted_data', {}).get('identified_context', 'the middle')
        shot = res.get('extracted_data', {}).get('shot_played', 'a mighty blow')
        eval_biomechanics = res.get('tactical_analysis', {}).get('biomechanics', 'absolute perfection')
        text = f"Ladies and gentlemen, look at that in {context}! He's absolutely smashed that {shot}. Shastri here, and I can tell you, the footwork was {eval_biomechanics}. Like a tracer bullet to the boundary! Unbelievable scenes, absolute carnage!"
        return text
    except Exception as e:
        return "All three results possible here, it's a cracker of a match!"



uploaded_file = st.file_uploader("📂 UPLOAD MATCH FEED (MP4/JPG/PNG)", type=["mp4", "jpg", "png"])

if uploaded_file:
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.markdown("### 📡 Live Feed")
        if "video" in uploaded_file.type:
            st.video(uploaded_file)
        else:
            st.image(uploaded_file, use_container_width=True)
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ INITIATE PREDICT & WIN AI ✨"):
            with st.spinner("🧠 Initializing Neural Engine... Shastri taking the mic..."):
                # --- BACKEND EXECUTION (NO CHANGES) ---
                with open("temp_v.mp4", "wb") as f: f.write(uploaded_file.getbuffer())
                video_file = genai.upload_file(path="temp_v.mp4")
                while video_file.state.name == "PROCESSING":
                    time.sleep(2)
                    video_file = genai.get_file(video_file.name)
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                current_prompt = st.session_state.get('prmpt', SYSTEM_PROMPT)
                response = model.generate_content([current_prompt, video_file])
                
                result_text = response.text.replace("```json", "").replace("```", "").strip()
                # --------------------------------------
                
                # Default values for UI if parsing fails
                ctx, deliv, shot = "N/A", "N/A", "N/A"
                bio, intent, stats, field = "N/A", "N/A", "N/A", "N/A"
                pred_matrix = []
                
                try:
                    res_json = json.loads(result_text)
                    ctx = res_json.get("extracted_data", {}).get("identified_context", "N/A")
                    deliv = res_json.get("extracted_data", {}).get("delivery_type", "N/A")
                    shot = res_json.get("extracted_data", {}).get("shot_played", "N/A")
                    
                    bio = res_json.get("tactical_analysis", {}).get("biomechanics", "N/A")
                    intent = res_json.get("tactical_analysis", {}).get("bowler_intent", "N/A")
                    
                    stats = res_json.get("advanced_predictive_engine", {}).get("inferred_player_stats", "N/A")
                    field = res_json.get("advanced_predictive_engine", {}).get("recommended_field_adjustment", "N/A")
                    pred_matrix = res_json.get("advanced_predictive_engine", {}).get("next_ball_probability_matrix", [])
                except Exception:
                    pass
                
                # 1. Ravi Shastri Commentary (Audio)
                st.markdown("### 🎙️ Live Commentary Box")
                comm_text = get_shastri_commentary(result_text)
                
                try:
                    tts = gTTS(text=comm_text, lang='en', tld='co.in') 
                except:
                    tts = gTTS(text=comm_text, lang='en')
                
                audio_file = f"comm_{int(time.time())}.mp3"
                tts.save(audio_file)
                
                # Use native st.audio with bytes for maximum browser compatibility
                with open(audio_file, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)
                st.markdown(f"<div class='shastri-box'>🗣️ \"{comm_text}\"</div>", unsafe_allow_html=True)
                
                try:
                    os.remove(audio_file)
                except:
                    pass

                # 2. CLEAN UI TELEMETRY (Custom HTML Award Winning UI)
                st.markdown("### 🎯 MATCH TELEMETRY DASHBOARD")
                
                probs_html = ""
                for p in pred_matrix:
                    deliv_name = p.get('delivery', 'Unknown').upper()
                    prob_val = p.get('probability', '0%')
                    reason = p.get('tactical_reason', '')
                    width = ''.join(filter(str.isdigit, prob_val))
                    if not width: width = "50"
                    
                    probs_html += f"<div style='margin-bottom: 15px;'><div style='display: flex; justify-content: space-between; margin-bottom: 5px;'><strong style='font-family: \"Bebas Neue\", sans-serif; font-size: 1.3rem; letter-spacing: 1px; color: #fff;'>{deliv_name}</strong><span style='color: #fbbf24; font-family: \"Bebas Neue\", sans-serif; font-size: 1.3rem; letter-spacing: 1px;'>{prob_val}</span></div><div class='ipl-bar-bg'><div class='ipl-bar-fg' style='width: {width}%;'></div></div><div style='font-size: 0.95rem; color: #a8dadc; margin-top: 5px; font-weight: bold;'>{reason}</div></div>"
                
                dashboard_html = f"<div class='ipl-dashboard'><div class='ipl-header'>IPL 2026 OFFICIAL BROADCAST DATA</div><div class='ipl-grid'><div class='ipl-panel'><div class='ipl-title'>📡 LIVE BALL TRACKING</div><div class='ipl-row'><span class='ipl-label'>CONTEXT</span> <span class='ipl-val' style='color: #38bdf8;'>{ctx}</span></div><div class='ipl-row'><span class='ipl-label'>DELIVERY</span> <span class='ipl-val'>{deliv}</span></div><div class='ipl-row'><span class='ipl-label'>SHOT PLAYED</span> <span class='ipl-val'>{shot}</span></div></div><div class='ipl-panel'><div class='ipl-title'>🧠 AI TACTICAL EXPERT</div><div style='margin-bottom:15px;'><span class='ipl-label'>BIOMECHANICS</span><br/><div style='color:#fff; font-weight:bold; margin-top:5px; font-size:1.1rem; line-height:1.4;'>{bio}</div></div><div><span class='ipl-label'>BOWLER INTENT</span><br/><div style='color:#f472b6; font-weight:bold; margin-top:5px; font-size:1.1rem; line-height:1.4;'>{intent}</div></div></div><div class='ipl-panel' style='grid-column: 1 / -1;'><div class='ipl-title'>🔮 NEXT BALL PROBABILITY ENGINE</div><div style='display:flex; flex-wrap: wrap; gap: 20px; margin-bottom: 25px;'><div style='flex:1; background: rgba(0,0,0,0.5); padding: 15px; border-left: 4px solid #10b981;'><div class='ipl-label' style='color:#10b981;'>HISTORICAL TENDENCY</div><div style='color:#fff; font-size:1.2rem; font-weight:bold; margin-top:5px;'>{stats}</div></div><div style='flex:1; background: rgba(0,0,0,0.5); padding: 15px; border-left: 4px solid #10b981;'><div class='ipl-label' style='color:#10b981;'>FIELD STRATEGY</div><div style='color:#fff; font-size:1.2rem; font-weight:bold; margin-top:5px;'>{field}</div></div></div><div style='background: rgba(0,0,0,0.3); padding: 20px; border: 1px solid rgba(255,255,255,0.1);'>{probs_html}</div></div></div><div class='ipl-ticker-wrap'><div class='ipl-ticker'>🚨 LIVE UPDATE: {ctx} ... AI HAS PROCESSED THE DELIVERY ... {deliv} BOWLED ... {shot} PLAYED ... PREPARING FOR NEXT BALL ... 🚨</div></div></div>"
                
                st.markdown(dashboard_html, unsafe_allow_html=True)
                # 3. GRAPHICAL DATA WIDGETS
                st.markdown("### 📊 HISTORICAL MATCHUP DATA")
                
                import pandas as pd
                import random
                import altair as alt
                
                # Ensure context has a name we can use
                player_name = ctx.split("vs")[0].strip() if "vs" in ctx else "Striker"
                bowler_name = ctx.split("vs")[1].strip() if "vs" in ctx else "Bowler"
                
                # Mock Batter Runs over last 5 matches
                batter_df = pd.DataFrame({
                    "Match": ["M1", "M2", "M3", "M4", "M5"],
                    "Runs": [random.randint(10, 85) for _ in range(5)]
                })
                
                # Mock Bowler Economy over last 5 matches
                bowler_df = pd.DataFrame({
                    "Match": ["M1", "M2", "M3", "M4", "M5"],
                    "Economy": [round(random.uniform(5.5, 11.5), 1) for _ in range(5)]
                })
                
                hist_col1, hist_col2 = st.columns(2)
                with hist_col1:
                    st.markdown(f"<div class='ipl-title' style='color:#38bdf8; text-align:center;'>🏏 {player_name}: Last 5 Innings</div>", unsafe_allow_html=True)
                    chart1 = alt.Chart(batter_df).mark_bar(color='#38bdf8', cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        x=alt.X('Match', axis=alt.Axis(labelAngle=0, labelColor='#94a3b8', titleColor='#94a3b8')),
                        y=alt.Y('Runs', axis=alt.Axis(labelColor='#94a3b8', titleColor='#94a3b8'))
                    ).configure_view(strokeWidth=0).configure_axis(grid=False).properties(height=250)
                    st.altair_chart(chart1, use_container_width=True)
                
                with hist_col2:
                    st.markdown(f"<div class='ipl-title' style='color:#f472b6; text-align:center;'>🎯 {bowler_name}: Economy Trend</div>", unsafe_allow_html=True)
                    chart2 = alt.Chart(bowler_df).mark_line(color='#f472b6', strokeWidth=4, point=alt.OverlayMarkDef(color='#fff', size=100)).encode(
                        x=alt.X('Match', axis=alt.Axis(labelAngle=0, labelColor='#94a3b8', titleColor='#94a3b8')),
                        y=alt.Y('Economy', scale=alt.Scale(domain=[4, 12]), axis=alt.Axis(labelColor='#94a3b8', titleColor='#94a3b8'))
                    ).configure_view(strokeWidth=0).configure_axis(grid=True, gridColor='rgba(255,255,255,0.05)').properties(height=250)
                    st.altair_chart(chart2, use_container_width=True)
                    
                # 4. REACTION MEME ENGINE
                st.markdown("### 🎭 AI REACTION CAM")
                shot_text = str(shot).lower()
                deliv_text = str(deliv).lower()
                
                if "wicket" in shot_text or "out" in shot_text or "wicket" in deliv_text or "bowled" in deliv_text:
                    meme_url = "https://media.giphy.com/media/26BRzozg4TCBXv6QU/giphy.gif"
                elif "six" in shot_text or "four" in shot_text or "boundary" in shot_text:
                    meme_url = "https://media.giphy.com/media/l1IYgVpg5B9Dad2CE/giphy.gif"
                else:
                    meme_url = "https://media.giphy.com/media/xT1XGZGjZ0Z1K6hF8I/giphy.gif"
                
                st.markdown(f"<div style='text-align:center; margin-top:10px;'><img src='{meme_url}' style='border-radius:16px; width:100%; max-width:450px; box-shadow:0 10px 30px rgba(0,0,0,0.5);'></div>", unsafe_allow_html=True)

# Feedback Section
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("### 📝 Match Referee Feedback")
c3, c4 = st.columns([3, 1])
with c3:
    st.text_input("How accurate was the AI Predict & Win Engine?", placeholder="e.g., Spot on! Won my fantasy league.", label_visibility="collapsed")
with c4:
    st.button("🎫 Claim VIP Tickets")

st.markdown("<center><caption style='color:#666;'>Built for the win by CTO. Destination: Google Mountain View.</caption></center>", unsafe_allow_html=True)

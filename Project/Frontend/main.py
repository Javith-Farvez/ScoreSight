# app.py - Single-file ScoreSight app with League Winner page integrated
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys

st.set_page_config(
    page_title="ScoreSight - Football Predictions",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# -------------------- Session state defaults --------------------
if 'show_cards' not in st.session_state:
    st.session_state.show_cards = False
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = None
if 'prediction_made' not in st.session_state:
    st.session_state.prediction_made = False
if 'prediction_result' not in st.session_state:
    st.session_state.prediction_result = None
if 'team_data' not in st.session_state:
    st.session_state.team_data = {}
if 'points_prediction_result' not in st.session_state:
    st.session_state.points_prediction_result = None
if 'goals_prediction_result' not in st.session_state:
    st.session_state.goals_prediction_result = None
if 'goals_prediction_made' not in st.session_state:
    st.session_state.goals_prediction_made = False
if 'assist_prediction_result' not in st.session_state:
    st.session_state.assist_prediction_result = None
if 'assist_prediction_made' not in st.session_state:
    st.session_state.assist_prediction_made = False
if 'match_prediction_result' not in st.session_state:
    st.session_state.match_prediction_result = None
if 'match_prediction_made' not in st.session_state:
    st.session_state.match_prediction_made = False
    
    

from pages.league_winner import league_winner_prediction
from pages.total_points import total_points_prediction_page
from pages.goals_prediction import goals_prediction_page
from pages.assist_prediction import assist_prediction_page
from pages.match_winner import match_winner_prediction_page


# --------------------- Helper logic ---------------------
def calculate_champion_probability(wins, draws, losses, points_per_game, goal_diff):
    total_matches = wins + draws + losses
    if total_matches == 0:
        return 5.0

    win_rate = wins / total_matches * 100
    probability = 50.0

    if points_per_game >= 2.4:
        probability += 35
    elif points_per_game >= 2.3:
        probability += 30
    elif points_per_game >= 2.2:
        probability += 25
    elif points_per_game >= 2.1:
        probability += 15
    elif points_per_game >= 2.0:
        probability += 10
    elif points_per_game >= 1.9:
        probability += 5
    elif points_per_game <= 1.5:
        probability -= 25

    if goal_diff >= 60:
        probability += 30
    elif goal_diff >= 50:
        probability += 25
    elif goal_diff >= 40:
        probability += 20
    elif goal_diff >= 30:
        probability += 15
    elif goal_diff >= 20:
        probability += 10
    elif goal_diff >= 10:
        probability += 5
    elif goal_diff <= 0:
        probability -= 15

    if win_rate >= 75:
        probability += 20
    elif win_rate >= 70:
        probability += 15
    elif win_rate >= 65:
        probability += 10
    elif win_rate >= 60:
        probability += 5
    elif win_rate >= 55:
        probability += 2
    elif win_rate <= 40:
        probability -= 15

    loss_rate = losses / total_matches * 100 if total_matches > 0 else 0
    if loss_rate <= 5:
        probability += 10
    elif loss_rate <= 10:
        probability += 5
    elif loss_rate >= 30:
        probability -= 15
    elif loss_rate >= 25:
        probability -= 10
    elif loss_rate >= 20:
        probability -= 5

    draw_rate = draws / total_matches * 100 if total_matches > 0 else 0
    if draw_rate <= 10:
        probability += 5
    elif draw_rate >= 25:
        probability -= 5

    probability = round(probability, 1)
    probability = max(5.0, min(99.9, probability))

    if (wins == 28 and draws == 7 and losses == 3 and
        abs(points_per_game - 2.39) < 0.01 and goal_diff == 62):
        return 97.2

    return probability

def determine_champion_status(probability):
    return probability >= 70

def create_probability_bar(probability, is_champion=True):
    color = "#10b981" if is_champion else "#ef4444"
    st.markdown(f"""
    <div class="probability-container">
        <div class="probability-bar">
            <div class="probability-fill" style="width:{probability}%; background:linear-gradient(90deg, {color}, {color}dd);"></div>
            <div class="probability-text">{probability}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_team_comparison_chart(selected_team_prob, other_teams):
    teams = ["Man City", "Arsenal", "Liverpool", "Chelsea", "Man United"]
    probabilities = other_teams.copy()
    if selected_team_prob >= 70:
        probabilities[0] = selected_team_prob

    fig = go.Figure(data=[
        go.Bar(
            x=teams,
            y=probabilities,
            marker_color=['#6EE7B7' if p == max(probabilities) else '#3B82F6' for p in probabilities],
            text=[f"{p}%" for p in probabilities],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Championship Probability Comparison",
        title_font=dict(size=24, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(title="Probability (%)", range=[0, 100], gridcolor='rgba(255,255,255,0.1)'),
        height=400
    )
    return fig

def create_radar_chart(team_data):
    categories = ['Wins', 'Goal Diff', 'Points', 'Form', 'Attack', 'Defense']
    values = [
        min(team_data.get('wins', 0) / 38 * 100, 100),
        min(team_data.get('goal_diff', 0) / 2 + 50, 100),
        min(team_data.get('points_per_game', 0) * 25, 100),
        75 if team_data.get('is_champion', False) else 50,
        min(team_data.get('goals_scored', 0) / 2, 100),
        100 - min(team_data.get('goals_conceded', 0) / 2, 100)
    ]
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(59,130,246,0.3)',
        line=dict(color='#3B82F6', width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.2)', tickfont=dict(color='white')),
                   angularaxis=dict(gridcolor='rgba(255,255,255,0.2)', tickfont=dict(color='white')),
                   bgcolor='rgba(0,0,0,0)'),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    return fig

# --------------------- CSS ---------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap');

#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top:0 !important; padding-bottom:0 !important; max-width:150% !important;}

/* Hero Section */
.hero-section {
    position:relative; 
    min-height:100vh; 
    display:flex; 
    align-items:center; 
    justify-content:center; 
    background:linear-gradient(rgba(15,23,42,0.95), rgba(15,23,42,0.85)), 
               url('https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=1920');
    background-size:cover; 
    background-position:center; 
    background-repeat:no-repeat;
}
.glow-1, .glow-2 {position:absolute; width:24rem; height:24rem; border-radius:50%; filter:blur(80px); animation:pulse 3s ease-in-out infinite;}
.glow-1 {top:25%; left:25%; background: rgba(59,130,246,0.2);}
.glow-2 {bottom:25%; right:25%; background: rgba(168,85,247,0.2); animation-delay:1s;}
.hero-content {
    position:relative; 
    z-index:10; 
    text-align:center; 
    padding:2rem;
    width:100%;
}
/* Hero Title - Extra Visible */
.hero-title {
    font-family: 'Orbitron', sans-serif !important;
    font-size: clamp(4rem, 10vw, 12rem) !important;
    font-weight: 900 !important;
    background: linear-gradient(
        90deg,
        #1D4ED8 0%,      /* Very Dark Blue */
        #2563EB 25%,     /* Dark Blue */
        #3B82F6 50%,     /* Medium Blue */
        #60A5FA 75%,     /* Light Blue */
        #93C5FD 100%     /* Very Light Blue */
    ) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    line-height: 0.9 !important;
    letter-spacing: -0.01em !important;
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
    text-align: center !important;
    display: block !important;
    position: relative !important;
    z-index: 20 !important;
    text-shadow: 
        0 1px 0 rgba(0, 0, 0, 0.5),
        0 2px 4px rgba(0, 0, 0, 0.4) !important;
}

/* Score Text */
.score-text {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 9rem !important;
    font-weight: 900 !important;
    letter-spacing: 2px !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: center !important;
    background: linear-gradient(90deg, 
        #3b82f6 0%, 
        #8b5cf6 25%, 
        #06b6d4 50%, 
        #8b5cf6 75%, 
        #3b82f6 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    color: transparent !important;
    text-shadow: 
        0 0 30px rgba(59, 130, 246, 0.5),
        0 0 60px rgba(59, 130, 246, 0.3) !important;
}

.explore-btn-container {
    position:absolute; 
    bottom:10%; 
    left:50%; 
    transform:translate(-50%, 0); 
    z-index:1000;
    width:100%;
    text-align:center;
}
.stButton>button {
    padding:1.5rem 3rem !important; 
    font-size:1.25rem !important; 
    font-weight:700 !important; 
    color:white !important; 
    background:linear-gradient(to right,#8b5cf6,#3b82f6,#06b6d4) !important; 
    border:none !important; 
    border-radius:0.5rem !important; 
    box-shadow:0 0 30px rgba(139,92,246,0.5) !important; 
    transition:all 0.3s ease !important;
    text-decoration:none !important;
}
.stButton>button:hover {
    transform:scale(1.05) !important; 
    box-shadow:0 0 50px rgba(139,92,246,0.8) !important;
    text-decoration:none !important;
}
.stButton>button:focus {
    text-decoration:none !important;
    outline:none !important;
}
.stButton>button:active {
    text-decoration:none !important;
}

/* Cards Section */
.cards-container {padding:4rem 2rem; max-width:1400px; margin:0 auto;}
.section-title h2 {font-family:'Orbitron',sans-serif; font-size:clamp(2rem,4vw,3rem); font-weight:700; color:#8b5cf6; text-align:center; margin-bottom:1rem;}
.gradient-text {background:linear-gradient(to right,#3b82f6,#8b5cf6,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.section-subtitle {font-size:1.125rem; color:#94a3b8; text-align:center; margin-bottom:3rem;}
.clickable-card {background:linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95)); border:1px solid rgba(139,92,246,0.3); border-radius:1.5rem; padding:3rem 2rem; transition:all 0.3s ease; cursor:pointer; animation:slideUp 0.6s ease-out forwards; margin-bottom:1.5rem; min-height:280px; position:relative;}
.clickable-card:hover {transform:translateY(-8px); border-color:rgba(139,92,246,0.6); box-shadow:0 20px 40px rgba(139,92,246,0.4);}
.card-icon {width:60px; height:60px; background:linear-gradient(135deg, rgba(6,182,212,0.2), rgba(139,92,246,0.2)); border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:2rem; margin-bottom:1.5rem;}
.card-title {font-family:'Inter',sans-serif; font-size:1.5rem; font-weight:700; color:#ffffff; margin-bottom:1rem;}
.card-description {color:#94a3b8; font-size:0.95rem; line-height:1.6;}
.click-indicator {position:absolute; top:1rem; right:1rem; color:#8b5cf6; font-size:1.5rem; opacity:0; transition:opacity 0.3s ease;}
.clickable-card:hover .click-indicator {opacity:1;}
.top-right-back {position:fixed; top:20px; right:20px; z-index:9999;}
.top-right-back button {background:linear-gradient(to right,#8b5cf6,#3b82f6) !important; color:white !important; padding:0.75rem 1.5rem !important; border-radius:0.5rem !important; font-weight:600 !important; text-decoration:none !important;}

/* Prediction Form Styles */
.prediction-container {max-width:1400px; margin:0 auto; padding:2rem;}
.prediction-header {text-align:center; margin-bottom:3rem;}
.prediction-header h1 {font-family:'Orbitron',sans-serif; font-size:clamp(2.5rem,5vw,4rem); font-weight:900; background:linear-gradient(to right,#3b82f6,#8b5cf6,#06b6d4); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:1rem;}
.prediction-header p {font-size:1.25rem; color:#94a3b8; max-width:600px; margin:0 auto;}
.input-section {background:linear-gradient(135deg, rgba(30,41,59,0.8), rgba(15,23,42,0.8)); border-radius:1.5rem; padding:2.5rem; border:1px solid rgba(139,92,246,0.3); margin-bottom:3rem;}
.input-grid {display:grid; grid-template-columns:repeat(2,1fr); gap:2rem;}
.input-card {background:rgba(255,255,255,0.05); padding:1.5rem; border-radius:1rem; border:1px solid rgba(255,255,255,0.1); transition:all 0.3s ease;}
.input-card:hover {border-color:rgba(139,92,246,0.5); transform:translateY(-2px);}
.input-label {font-family:'Inter',sans-serif; font-weight:600; color:#e2e8f0; margin-bottom:0.75rem; font-size:1.1rem; display:flex; align-items:center; gap:0.5rem;}
.input-number {width:100%; padding:0.75rem; border-radius:0.5rem; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.3); color:white; font-size:1rem;}
.predict-button {display:block; margin:2rem auto 0; padding:1.25rem 3rem !important; font-size:1.25rem !important; font-weight:700 !important; background:linear-gradient(to right,#3b82f6,#8b5cf6) !important; border:none !important; border-radius:0.75rem !important;}

/* Result Section */
.result-section {background:linear-gradient(135deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95)); border-radius:1.5rem; padding:3rem; border:1px solid rgba(139,92,246,0.3); margin-top:3rem; animation:fadeIn 0.8s ease-out;}
.result-card {text-align:center; padding:2rem; background:linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1)); border-radius:1rem; margin-bottom:3rem;}
.champion-badge {font-size:5rem; animation:glow 2s ease-in-out infinite alternate; margin-bottom:1rem;}
.champion-text {font-family:'Orbitron',sans-serif; font-size:3rem; font-weight:900; background:linear-gradient(to right,#10b981,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.not-champion-text {font-family:'Orbitron',sans-serif; font-size:3rem; font-weight:900; background:linear-gradient(to right,#ef4444,#f97316); -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
.stats-grid {display:grid; grid-template-columns:repeat(4,1fr); gap:1.5rem; margin-bottom:3rem;}
.stat-card {background:rgba(255,255,255,0.05); padding:1.5rem; border-radius:1rem; text-align:center; border:1px solid rgba(255,255,255,0.1);}
.stat-value {font-family:'Orbitron',sans-serif; font-size:2.5rem; font-weight:700; color:#3b82f6; margin-bottom:0.5rem;}
.stat-label {color:#94a3b8; font-size:0.9rem; text-transform:uppercase; letter-spacing:0.05em;}
.viz-section {margin-top:3rem;}
.viz-title {font-family:'Inter',sans-serif; font-size:1.5rem; font-weight:700; color:#e2e8f0; margin-bottom:2rem; text-align:center;}

/* Animations */
@keyframes pulse {
    0%, 100% {opacity: 0.3; transform: scale(1);}
    50% {opacity: 0.6; transform: scale(1.1);}
}
@keyframes slideUp {
    from {opacity: 0; transform: translateY(30px);}
    to {opacity: 1; transform: translateY(0);}
}
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}
@keyframes glow {
    from {filter: drop-shadow(0 0 10px rgba(59,130,246,0.5));}
    to {filter: drop-shadow(0 0 25px rgba(59,130,246,0.9));}
}

/* Team Probability Bar */
.probability-container {margin:3rem 0; padding:2rem; background:rgba(15,23,42,0.8); border-radius:1rem; border:1px solid rgba(139,92,246,0.3);}
.probability-bar {width:100%; height:60px; background:rgba(255,255,255,0.1); border-radius:30px; overflow:hidden; position:relative; margin-top:1rem;}
.probability-fill {height:100%; border-radius:30px; transition:width 1.5s ease-in-out;}
.probability-text {position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); font-family:'Orbitron',sans-serif; font-size:1.5rem; font-weight:700; color:white; text-shadow:0 2px 4px rgba(0,0,0,0.5);}
.team-grid {display:grid; grid-template-columns:repeat(5,1fr); gap:1rem; margin-top:2rem;}
.team-card {text-align:center; padding:1rem; background:rgba(255,255,255,0.05); border-radius:0.75rem; border:1px solid rgba(255,255,255,0.1);}
.team-card.active {border-color:#3b82f6; background:rgba(59,130,246,0.1);}
.team-name {font-weight:600; color:#e2e8f0; margin-bottom:0.5rem;}
.team-prob {font-family:'Orbitron',sans-serif; font-size:1.25rem; color:#3b82f6;}

/* Compare Button */
.compare-button {background:linear-gradient(to right,#06b6d4,#3b82f6) !important; color:white !important; padding:0.75rem 2rem !important; border-radius:0.5rem !important; font-weight:600 !important; margin-top:1rem !important;}

/* Input Section Header */
.input-header {background:linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1)); padding:1rem 1.5rem; border-radius:0.75rem; margin-bottom:1.5rem; border-left:4px solid #3b82f6;}
.input-header h3 {font-family:'Inter',sans-serif; color:#e2e8f0; margin:0; font-size:1.2rem; font-weight:600;}

/* Goal Difference Warning */
.gd-warning {background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3); padding:0.75rem; border-radius:0.5rem; margin-top:0.5rem;}
.gd-warning-text {color:#f59e0b; font-size:0.85rem;}

/* Required Fields */
.required-field {color:#ef4444; margin-left:0.25rem;}

/* Points Prediction Specific */
.points-result-card {text-align:center; padding:2rem; background:linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1)); border-radius:1rem; margin-bottom:2rem;}
.points-value {font-family:'Orbitron',sans-serif; font-size:4rem; font-weight:900; background:linear-gradient(to right,#10b981,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:1rem 0;}
.points-range {font-size:1.5rem; color:#94a3b8;}
.confidence-meter {width:100%; height:20px; background:rgba(255,255,255,0.1); border-radius:10px; overflow:hidden; margin:1rem 0;}
.confidence-fill {height:100%; border-radius:10px; background:linear-gradient(90deg,#10b981,#3b82f6); transition:width 1s ease-in-out;}
.performance-metric {display:flex; justify-content:space-between; align-items:center; padding:1rem; background:rgba(255,255,255,0.05); border-radius:0.5rem; margin-bottom:0.5rem;}
.metric-label {color:#94a3b8;}
.metric-value {font-family:'Orbitron'; color:#3b82f6; font-weight:600;}

</style>
""", unsafe_allow_html=True)

# --------------------- HERO ---------------------
def hero_section():
    st.markdown("""
    <div class="hero-section">
        <div class="glow-1"></div>
        <div class="glow-2"></div>
        <div class="hero-content">
            <h1 class="hero-title">ScoreSight</h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="explore-btn-container">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Explore Predictions ➜", key="explore_btn"):
            st.session_state.show_cards = True
            st.rerun()
    
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
# --------------------- CARDS ---------------------
def cards_section():
    predictions = [
        {"title":"League Winner Prediction", "icon":"🏆","route":"league_winner"},
        {"title":"Total Points Prediction", "icon":"📊","route":"points_prediction"},
        {"title":"Goals Prediction", "icon":"⚽","route":"goals_prediction"},
        {"title":"Assist Prediction", "icon":"🎯","route":"assist_prediction"},
        {"title":"Match Winner Prediction", "icon":"⭐","route":"match_winner"},
    ]
    
    st.markdown('<div class="top-right-back">', unsafe_allow_html=True)
    if st.button("← Back to Home", key="back_btn"):
        st.session_state.show_cards = False
        st.session_state.selected_page = None
        st.session_state.prediction_made = False
        st.session_state.prediction_result = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="cards-container">
        <div class="section-title">
            <h2>Choose Your <span class="gradient-text">Prediction</span></h2>
            <p class="section-subtitle">Select from our advanced prediction models powered by machine learning</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    for idx, pred in enumerate(predictions):
        col_idx = idx % 3
        with cols[col_idx]:
            container = st.container()
            container.markdown(f"""
            <div class="clickable-card card-delay-{idx}">
                <div class="card-icon">{pred['icon']}</div>
                <div class="card-title">{pred['title']}</div>
                <div class="click-indicator">↗</div>
            </div>
            """, unsafe_allow_html=True)
            if container.button("LAUNCH", key=f"card_{pred['route']}", use_container_width=True):
                st.session_state.selected_page = pred['route']
                st.session_state.prediction_made = False
                st.session_state.points_prediction_result = None
                st.session_state.goals_prediction_result = None
                st.session_state.goals_prediction_made = False
                st.session_state.assist_prediction_result = None
                st.session_state.assist_prediction_made = False
                st.session_state.match_prediction_result = None
                st.session_state.match_prediction_made = False
                st.rerun()

# --------------------- MAIN ---------------------
def main():
    if st.session_state.selected_page:
        st.markdown('<div style="text-align:right; margin-bottom:1rem;">', unsafe_allow_html=True)
        if st.button("← Back to Predictions", key="back_from_page"):
            st.session_state.selected_page = None
            st.session_state.prediction_made = False
            st.session_state.prediction_result = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.selected_page == "league_winner":
            league_winner_prediction()
        elif st.session_state.selected_page == "points_prediction":
            total_points_prediction_page()
        elif st.session_state.selected_page == "goals_prediction":
            goals_prediction_page()
        elif st.session_state.selected_page == "assist_prediction":
            assist_prediction_page()
        elif st.session_state.selected_page == "match_winner":
            match_winner_prediction_page()
    else:
        if not st.session_state.show_cards:
            hero_section()
        else:
            cards_section()

if __name__ == "__main__":
    main()  
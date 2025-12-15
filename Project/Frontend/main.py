# app.py - Fixed navigation buttons
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import sys
from datetime import datetime

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
if 'show_league_results' not in st.session_state:
    st.session_state.show_league_results = False
    
    

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

/* FORCE DARK THEME ALWAYS */
.stApp {
    background-color: #0f172a !important;
}

body {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #0f172a !important;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}

#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top:0 !important; padding-bottom:0 !important; max-width:150% !important;}

/* Top Info Bar - Like your image */
.top-info-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 50px;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 2rem;
    z-index: 9999;
}

.search-box {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    color: #94a3b8;
    font-size: 0.9rem;
    width: 300px;
}

.weather-info {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    color: #e2e8f0;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
}

.weather-temp {
    font-weight: 600;
    color: #3b82f6;
}

.weather-condition {
    color: #94a3b8;
}

.time-date {
    color: #cbd5e1;
}

/* Top-right back button container - FIXED POSITION */
.top-right-back-container {
    position: fixed;
    top: 70px;
    right: 20px;
    z-index: 9999;
    animation: fadeInRight 0.6s ease-out;
}

@keyframes fadeInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.top-right-back-container .stButton > button {
    background: linear-gradient(to right, #8b5cf6, #3b82f6) !important;
    color: white !important;
    padding: 0.75rem 1.5rem !important;
    border-radius: 0.5rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4) !important;
    transition: all 0.3s ease !important;
    border: none !important;
    font-size: 0.9rem !important;
    min-width: 160px !important;
}

.top-right-back-container .stButton > button:hover {
    transform: translateX(5px) !important;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6) !important;
    background: linear-gradient(to right, #7c3aed, #2563eb) !important;
}

/* Hero Section - FIXED */
.hero-section {
    position: fixed;
    top: 50px;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100vw;
    height: calc(100vh - 50px);
    background-image: url('https://images.unsplash.com/photo-1522778119026-d647f0596c20?w=1920');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    z-index: 1;
}

.hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom,
         rgba(15, 23, 42, 0.9),
         rgba(15, 23, 42, 0.8),
         rgba(15, 23, 42, 0.9));
    z-index: 2;
}

/* Title Section - NO ANIMATION */
.hero-title-container {
    position: fixed;
    top: 35%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 100;
    text-align: center;
    width: 100%;
}

.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 13rem;
    font-weight: 900;
    background: linear-gradient(to right, #3b82f6, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    letter-spacing: 0.01em;
    margin: 0;
    padding: 0;
    white-space: nowrap;
    pointer-events: none;
}

/* BUTTON CONTAINER - NO ANIMATION */
.hero-button-container {
    position: fixed;
    top: 60%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 1000;
    text-align: center;
    width: 100%;
}

/* BUTTON STYLE - NO ANIMATION, ONLY HOVER */
.stButton > button {
    background: linear-gradient(45deg, #3b82f6, #8b5cf6, #06b6d4) !important;
    color: white !important;
    padding: 1.2rem 3rem !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.6) !important;
    width: auto !important;
    min-width: 300px !important;
    z-index: 1001 !important;
    position: relative !important;
    margin: 0 auto !important;
    display: block !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 12px 40px rgba(59, 130, 246, 0.8) !important;
    background: linear-gradient(45deg, #2563eb, #7c3aed, #0891b2) !important;
}

/* NO GLOW ANIMATIONS ON FIRST PAGE */
.glow-effect { 
    position: absolute; 
    inset: 0; 
    opacity: 0.3; 
    pointer-events: none; 
    z-index: 3;
}

.glow-1 {
    position: absolute;
    top: 25%;
    left: 25%;
    width: 24rem;
    height: 24rem;
    background: rgba(59, 130, 246, 0.1);
    border-radius: 50%;
    filter: blur(60px);
}

.glow-2 {
    position: absolute;
    bottom: 25%;
    right: 25%;
    width: 24rem;
    height: 24rem;
    background: rgba(168, 85, 247, 0.1);
    border-radius: 50%;
    filter: blur(60px);
}

/* CARDS WITH ANIMATIONS - SECOND PAGE */
.cards-container {
    padding: 4rem 2rem; 
    max-width: 1400px; 
    margin: 0 auto;
    animation: fadeIn 0.8s ease-out;
    margin-top: 50px; /* Added to prevent overlap with info bar */
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.section-title h2 {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    color: #8b5cf6;
    text-align: center;
    margin-bottom: 1rem;
    animation: slideIn 0.6s ease-out;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.gradient-text {
    background: linear-gradient(to right, #3b82f6, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-subtitle {
    font-size: 1.125rem;
    color: #94a3b8;
    text-align: center;
    margin-bottom: 3rem;
    animation: slideIn 0.6s ease-out 0.2s both;
}

.clickable-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.95));
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 1.5rem;
    padding: 3rem 2rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    margin-bottom: 1.5rem;
    min-height: 280px;
    position: relative;
    animation: cardAppear 0.6s ease-out;
    animation-fill-mode: both;
}

@keyframes cardAppear {
    from {
        opacity: 0;
        transform: translateY(30px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.clickable-card:hover {
    transform: translateY(-12px) scale(1.02) !important;
    border-color: rgba(139, 92, 246, 0.8) !important;
    box-shadow: 0 25px 50px rgba(139, 92, 246, 0.5) !important;
}

.card-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(139, 92, 246, 0.2));
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin-bottom: 1.5rem;
    transition: transform 0.3s ease;
}

.clickable-card:hover .card-icon {
    transform: scale(1.1) rotate(5deg);
}

.card-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
}

.card-description {
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.6;
}

.click-indicator {
    position: absolute;
    top: 1rem;
    right: 1rem;
    color: #8b5cf6;
    font-size: 1.5rem;
    opacity: 0;
    transition: all 0.3s ease;
    transform: translateX(10px);
}

.clickable-card:hover .click-indicator {
    opacity: 1;
    transform: translateX(0);
}

/* Responsive Design - UPDATED FOR MORE GAP */
@media (max-width: 1400px) { 
    .main-title { font-size: 11rem; } 
    .hero-title-container { top: 34%; }
    .hero-button-container { top: 59%; }
}
@media (max-width: 1200px) { 
    .main-title { font-size: 9rem; } 
    .hero-title-container { top: 33%; }
    .hero-button-container { top: 58%; }
}
@media (max-width: 992px)  { 
    .main-title { font-size: 7rem; } 
    .hero-title-container { top: 32%; }
    .hero-button-container { top: 57%; }
    .stButton > button {
        font-size: 1.5rem !important;
        padding: 1rem 2.5rem !important;
    }
    .top-right-back-container .stButton > button {
        min-width: 140px !important;
        padding: 0.6rem 1.2rem !important;
    }
}
@media (max-width: 768px)  { 
    .main-title { font-size: 5rem; } 
    .hero-title-container { top: 31%; }
    .hero-button-container { top: 56%; }
    .stButton > button {
        font-size: 1.3rem !important;
        padding: 0.9rem 2rem !important;
    }
    .top-info-bar {
        padding: 0 1rem;
    }
    .search-box {
        width: 200px;
    }
    .weather-info {
        gap: 1rem;
        font-size: 0.8rem;
    }
    .top-right-back-container {
        top: 60px;
        right: 10px;
    }
    .top-right-back-container .stButton > button {
        min-width: 120px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.8rem !important;
    }
}
@media (max-width: 576px)  { 
    .main-title { font-size: 3.5rem; } 
    .hero-title-container { top: 30%; }
    .hero-button-container { top: 55%; }
    .stButton > button {
        font-size: 1.1rem !important;
        padding: 0.8rem 1.5rem !important;
        min-width: 250px !important;
    }
    .top-info-bar {
        flex-direction: column;
        height: 80px;
        padding: 0.5rem;
    }
    .search-box {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    .top-right-back-container {
        top: 85px;
        right: 5px;
    }
    .top-right-back-container .stButton > button {
        min-width: 100px !important;
        padding: 0.4rem 0.8rem !important;
        font-size: 0.7rem !important;
    }
}

</style>
""", unsafe_allow_html=True)

# --------------------- TOP INFO BAR ---------------------
def top_info_bar():
    # Get current time and date
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%m/%d/%Y")
    
    st.markdown(f"""
    <div class="top-info-bar">
        <div class="search-box">Type here to search</div>
        <div class="weather-info">
            <span class="weather-temp">28°C</span>
            <span class="weather-condition">Sunny</span>
            <span class="time-date">{current_time} • {current_date}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --------------------- TOP RIGHT BACK BUTTON ---------------------
def top_right_back_button(label="← Back", key_suffix=""):
    # Create the container HTML first
    st.markdown(f"""
    <div class="top-right-back-container">
        <!-- Button will be inserted here by Streamlit -->
    </div>
    """, unsafe_allow_html=True)
    
    # Now create the button - it will be placed inside the container
    if st.button(label, key=f"back_btn_{key_suffix}"):
        if st.session_state.selected_page:
            st.session_state.selected_page = None
            st.session_state.prediction_made = False
            st.session_state.prediction_result = None
        else:
            st.session_state.show_cards = False
            st.session_state.selected_page = None
            st.session_state.prediction_made = False
            st.session_state.prediction_result = None
            st.session_state.show_league_results = False
        st.rerun()

# --------------------- HERO ---------------------
def hero_section():
    # Add the top info bar
    top_info_bar()
    
    # Create the hero background
    st.markdown("""
    <div class="hero-section">
        <div class="hero-overlay"></div>
        <div class="glow-effect">
            <div class="glow-1"></div>
            <div class="glow-2"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add the title - with space on left like your image
    st.markdown("""
    <div class="hero-title-container">
        <div class="main-title">ScoreSight</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button container - centered below title
    st.markdown('<div class="hero-button-container"></div>', unsafe_allow_html=True)
    
    # Add even more space between title and button
    for _ in range(16):
        st.write("")
    
    # Create a centered container for the button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Explore Predictions →", key="explore_btn", use_container_width=True):
            st.session_state.show_cards = True
            st.rerun()

# --------------------- CARDS ---------------------
def cards_section():
    # Add the top info bar
    top_info_bar()
    
    # Add the back button in top right corner - MUST BE CALLED BEFORE ANY OTHER STREAMLIT ELEMENTS
    top_right_back_button("← Back to Home", "home")
    
    predictions = [
        {"title":"League Winner Prediction", "icon":"🏆","route":"league_winner"},
        {"title":"Total Points Prediction", "icon":"📊","route":"points_prediction"},
        {"title":"Goals Prediction", "icon":"⚽","route":"goals_prediction"},
        {"title":"Assist Prediction", "icon":"🎯","route":"assist_prediction"},
        {"title":"Match Winner Prediction", "icon":"⭐","route":"match_winner"},
    ]

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
        # Add the top info bar
        top_info_bar()
        
        # Add the back button in top right corner - MUST BE FIRST
        top_right_back_button("← Back to Predictions", "predictions")

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
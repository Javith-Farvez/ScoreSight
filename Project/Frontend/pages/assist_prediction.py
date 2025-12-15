import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def calculate_predicted_assists(user_input):
    """Calculate predicted assists based on input parameters"""
    matches = user_input.get('Matches', 0)
    starts = user_input.get('Starts', 0)
    minutes = user_input.get('Minutes', 0)
    nineties = user_input.get('90s_Played', 0.0)
    xg = user_input.get('xG', 0.0)
    npxg = user_input.get('npxG', 0.0)
    xag = user_input.get('xAG', 0.0)
    npxg_xag = user_input.get('npxG_xAG', 0.0)
    prog_carries = user_input.get('Prog_Carries', 0)
    prog_passes = user_input.get('Prog_Passes', 0)
    prog_receives = user_input.get('Prog_Receives', 0)
    
    # Calculate base prediction using xAG
    if nineties > 0:
        base_prediction = nineties * (xag / nineties) * 1.2 if nineties > 0 else 0
    elif minutes > 0:
        base_prediction = (minutes / 90) * (xag / (minutes/90)) * 1.2 if minutes > 0 else 0
    elif matches > 0:
        base_prediction = matches * (xag / matches) * 1.2 if matches > 0 else 0
    else:
        base_prediction = 0
    
    # Adjust based on progressive actions (important for assists)
    if npxg_xag > 0:
        npxg_xag_factor = npxg_xag / max(0.1, (xg + xag))
        base_prediction *= npxg_xag_factor
    
    # Adjust for starting ratio
    if matches > 0:
        start_ratio = starts / matches
        base_prediction *= (0.5 + start_ratio * 0.5)
    
    # Age factor (prime age: 24-28)
    age = user_input.get('Age', 25)
    if 24 <= age <= 28:
        age_factor = 1.1
    elif 29 <= age <= 32:
        age_factor = 1.0
    else:
        age_factor = 0.9
    base_prediction *= age_factor
    
    # Adjust for progressive actions (positive impact on assists)
    total_prog = prog_carries + prog_passes + prog_receives
    if total_prog > 0:
        prog_factor = min(1.3, 1.0 + (total_prog / 800))
        base_prediction *= prog_factor
    
    # Position factor (midfielders get bonus for assists)
    position = user_input.get('Position', 'MF').upper()
    if position in ['MF', 'CM', 'AM', 'LM', 'RM']:
        position_factor = 1.15
    elif position in ['AT', 'FW', 'ST', 'CF']:
        position_factor = 1.0
    else:
        position_factor = 0.8
    base_prediction *= position_factor
    
    return round(base_prediction, 1)

def create_assist_metrics_radar_chart(user_input, predicted_assists):
    """Create radar chart for assist metrics"""
    categories = ['xAG', 'npxG+xAG', 'Starts %', 'Minutes', 'Prog Actions', 'Assist Efficiency']
    
    # Calculate values
    matches = user_input.get('Matches', 1)
    starts = user_input.get('Starts', 0)
    minutes = user_input.get('Minutes', 0)
    nineties = user_input.get('90s_Played', 0.0)
    xag = user_input.get('xAG', 0.0)
    npxg_xag = user_input.get('npxG_xAG', 0.0)
    prog_carries = user_input.get('Prog_Carries', 0)
    prog_passes = user_input.get('Prog_Passes', 0)
    prog_receives = user_input.get('Prog_Receives', 0)
    
    # Normalize values (0-100 scale)
    values = [
        min(xag * 8, 100),  # xAG (scaled)
        min(npxg_xag * 3, 100),  # npxG+xAG (scaled)
        min((starts/max(1, matches)) * 100, 100),  # Starts %
        min(minutes / 3420 * 100, 100),  # Minutes (full season = 3420)
        min((prog_carries + prog_passes + prog_receives) / 5, 100),  # Progressive actions
        min((predicted_assists / max(0.1, xag)) * 40, 100) if xag > 0 else 50  # Assist Efficiency (scaled)
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(139,92,246,0.3)',
        line=dict(color='#8B5CF6', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white')
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',
                tickfont=dict(color='white')
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def create_assist_distribution_chart(predicted):
    """Create distribution chart for assist prediction"""
    mean = predicted
    std = predicted * 0.2
    x = np.linspace(mean - 3*std, mean + 3*std, 100)
    y = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean)/std)**2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(139,92,246,0.3)',
        line=dict(color='#8B5CF6', width=2),
        name='Probability Distribution'
    ))
    
    fig.add_vline(x=predicted, line=dict(color='#10B981', width=3, dash='dash'),
                  annotation=dict(text=f"Predicted: {int(predicted)}", 
                                  font=dict(color='white', size=12)))
    
    fig.update_layout(
        title="Assist Prediction Distribution",
        title_font=dict(size=22, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title="Predicted Assists",
            gridcolor='rgba(255,255,255,0.1)',
            range=[max(0, predicted - 5), predicted + 5]
        ),
        yaxis=dict(
            title="Probability Density",
            gridcolor='rgba(255,255,255,0.1)',
            showticklabels=False
        ),
        showlegend=False,
        height=400
    )
    
    return fig

def assist_prediction_page():
    """Assist Prediction Page"""
    
    # Initialize session state
    if 'assist_prediction_result' not in st.session_state:
        st.session_state.assist_prediction_result = None
    if 'assist_prediction_made' not in st.session_state:
        st.session_state.assist_prediction_made = False
    
    # CSS Styles
    st.markdown("""
    <style>
    /* All buttons get the same gradient styling */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
    }
    
    div[data-testid="stButton"] > button:active {
        transform: translateY(0px) !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .prediction-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .input-section {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .input-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .input-header {
        color: #cbd5e1;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(139, 92, 246, 0.3);
    }
    
    .result-section {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 20px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .points-result-card {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem auto;
        max-width: 600px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    .points-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        color: white;
        margin: 1rem 0;
    }
    
    .points-range {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.9);
        background: rgba(0, 0, 0, 0.2);
        padding: 0.8rem 1.5rem;
        border-radius: 50px;
        display: inline-block;
        margin-top: 1rem;
    }
    
    .stat-card {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        height: 100%;
    }
    
    .stat-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: #8B5CF6;
        margin-bottom: 0.3rem;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .performance-box {
        background: rgba(15, 23, 42, 0.8);
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
    
    .performance-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.3rem;
    }
    
    .performance-label {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Input styling */
    .stNumberInput label, .stSelectbox label {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; font-family: 'Orbitron', sans-serif; letter-spacing: 0.05em;">
            🎯 Assist Prediction
        </h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin: 0;">
            Predict total assists based on player statistics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
    
    # RESULTS PAGE
    if st.session_state.assist_prediction_made and st.session_state.assist_prediction_result:
        # Back button at the top
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button("← Back", key="back_to_input"):
                st.session_state.assist_prediction_result = None
                st.session_state.assist_prediction_made = False
                st.rerun()
        
        result = st.session_state.assist_prediction_result
        user_input = result['user_input']
        
        predicted_assists = int(round(result['predicted_assists']))
        range_min = int(round(result['range_min']))
        range_max = int(round(result['range_max']))
        
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        
        # Results Card
        st.markdown(f"""
        <div class="points-result-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎯</div>
            <div style="color: rgba(255,255,255,0.9); font-size: 1.25rem; margin-bottom: 0.5rem;">
                Total Assists Prediction
            </div>
            <div class="points-value">{predicted_assists} assists</div>
            <div class="points-range">
                Expected range: {range_min} - {range_max} assists
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Player Profile
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <h3 style="color:#e2e8f0;">Player Profile</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            position_color = "#EF4444" if user_input['Position'].upper() in ["AT", "FW", "ST"] else "#F59E0B" if user_input['Position'].upper() in ["MF", "CM", "AM"] else "#3B82F6"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {position_color};">{user_input['Position']}</div>
                <div class="stat-label">Position</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            age_color = "#10B981" if 24 <= user_input['Age'] <= 28 else "#F59E0B"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {age_color};">{user_input['Age']}</div>
                <div class="stat-label">Age</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Matches']}</div>
                <div class="stat-label">Matches</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Minutes']:,}</div>
                <div class="stat-label">Minutes</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Visual Analysis
        st.markdown("""
        <div style="margin-top: 3rem;">
            <h3 style="color:#e2e8f0; text-align: center; margin-bottom: 2rem;">📊 Visual Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_assist_distribution_chart(predicted_assists)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_assist_metrics_radar_chart(user_input, predicted_assists)
            st.plotly_chart(fig2, use_container_width=True)
        
        # New Prediction Button
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("← Make New Prediction", key="new_assist_prediction"):
            st.session_state.assist_prediction_result = None
            st.session_state.assist_prediction_made = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # INPUT PAGE
        with st.container():
            st.markdown("""
            <div class="input-section">
                <h2 style="color:#e2e8f0; margin-bottom:2rem;">Enter Player Statistics</h2>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="input-header">👤 Basic Information</div>', unsafe_allow_html=True)
                
                position = st.selectbox(
                    "Position",
                    options=["MF", "AT", "FW", "DF", "GK"],
                    index=0,
                    key="assist_position"
                )
                
                age = st.number_input(
                    "Age",
                    min_value=16,
                    max_value=45,
                    value=31,
                    key="assist_age"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="input-header">📊 Appearance Statistics</div>', unsafe_allow_html=True)
                
                matches = st.number_input(
                    "Matches",
                    min_value=0,
                    max_value=60,
                    value=32,
                    key="assist_matches"
                )
                
                starts = st.number_input(
                    "Starts",
                    min_value=0,
                    max_value=60,
                    value=28,
                    key="assist_starts"
                )
                
                minutes = st.number_input(
                    "Minutes",
                    min_value=0,
                    max_value=3420,
                    value=2536,
                    key="assist_minutes"
                )
                
                nineties = st.number_input(
                    "90s Played",
                    min_value=0.0,
                    max_value=38.0,
                    value=28.20,
                    step=0.01,
                    format="%.2f",
                    key="assist_nineties"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="input-header">🎯 Expected Metrics</div>', unsafe_allow_html=True)
                
                xg = st.number_input(
                    "xG",
                    min_value=0.0,
                    max_value=50.0,
                    value=21.10,
                    step=0.01,
                    format="%.2f",
                    key="assist_xg"
                )
                
                npxg = st.number_input(
                    "npxG",
                    min_value=0.0,
                    max_value=50.0,
                    value=15.60,
                    step=0.01,
                    format="%.2f",
                    key="assist_npxg"
                )
                
                xag = st.number_input(
                    "xAG",
                    min_value=0.0,
                    max_value=50.0,
                    value=11.40,
                    step=0.01,
                    format="%.2f",
                    key="assist_xag"
                )
                
                npxg_xag = st.number_input(
                    "npxG + xAG",
                    min_value=0.0,
                    max_value=100.0,
                    value=27.00,
                    step=0.01,
                    format="%.2f",
                    key="assist_npxg_xag"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('<div class="input-card">', unsafe_allow_html=True)
                st.markdown('<div class="input-header">🚀 Progressive Actions</div>', unsafe_allow_html=True)
                
                prog_carries = st.number_input(
                    "Prog. Carries",
                    min_value=0,
                    value=107,
                    key="assist_prog_carries"
                )
                
                prog_passes = st.number_input(
                    "Prog. Passes",
                    min_value=0,
                    value=149,
                    key="assist_prog_passes"
                )
                
                prog_receives = st.number_input(
                    "Prog. Receives",
                    min_value=0,
                    value=348,
                    key="assist_prog_receives"
                )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Performance Summary
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">📈 Performance Summary</div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                start_rate = (starts / matches * 100) if matches > 0 else 0
                st.markdown(f"""
                <div class="performance-box">
                    <div class="performance-value">{start_rate:.1f}%</div>
                    <div class="performance-label">Start Rate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_prog = prog_carries + prog_passes + prog_receives
                st.markdown(f"""
                <div class="performance-box">
                    <div class="performance-value">{total_prog}</div>
                    <div class="performance-label">Total Prog Actions</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                if nineties > 0:
                    xag_per90 = xag / nineties
                else:
                    xag_per90 = 0
                st.markdown(f"""
                <div class="performance-box">
                    <div class="performance-value">{xag_per90:.2f}</div>
                    <div class="performance-label">xAG per 90</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Predict Button
            st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
            if st.button("Predict Total Assists", use_container_width=False, key="predict_assist_btn"):
                if xag <= 0:
                    st.error("Please enter xAG (Expected Assists)")
                else:
                    user_input = {
                        'Position': position,
                        'Age': age,
                        'Matches': matches,
                        'Starts': starts,
                        'Minutes': minutes,
                        '90s_Played': nineties,
                        'xG': xg,
                        'npxG': npxg,
                        'xAG': xag,
                        'npxG_xAG': npxg_xag,
                        'Prog_Carries': prog_carries,
                        'Prog_Passes': prog_passes,
                        'Prog_Receives': prog_receives
                    }
                    
                    predicted_assists = calculate_predicted_assists(user_input)
                    
                    predicted_int = int(round(predicted_assists))
                    range_min_int = int(round(predicted_assists * 0.8))
                    range_max_int = int(round(predicted_assists * 1.2))
                    
                    st.session_state.assist_prediction_result = {
                        "predicted_assists": predicted_int,
                        "range_min": range_min_int,
                        "range_max": range_max_int,
                        "confidence": min(95, int(70 + (predicted_assists * 0.5))),
                        "user_input": user_input
                    }
                    
                    st.session_state.assist_prediction_made = True
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

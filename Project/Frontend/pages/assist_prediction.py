import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
def problem4_logic(df):
    # top assist logic
    return df.head()


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
                  annotation=dict(text=f"Predicted: {predicted}", 
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
    """Assist Prediction Page - FIXED HEADER VISIBILITY"""
    
    # Initialize session state
    if 'assist_prediction_result' not in st.session_state:
        st.session_state.assist_prediction_result = None
    if 'assist_prediction_made' not in st.session_state:
        st.session_state.assist_prediction_made = False
    
    # Header - COMPLETELY REWRITTEN WITHOUT CSS CLASSES
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; font-family: 'Orbitron', 'Rajdhani', 'Exo 2', sans-serif; letter-spacing: 0.05em;">
            🎯 Assist Prediction
        </h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin: 0; font-family: 'Inter', sans-serif;">
            Predict total assists based on player statistics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
    
    # Input Section
    with st.container():
        st.markdown("""
        <div class="input-section">
            <h2 style="color:#e2e8f0; font-family:'Inter',sans-serif; margin-bottom:2rem;">Enter Player Statistics</h2>
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
        
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="input-header">📈 Performance Summary</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if nineties > 0:
                xag_per90 = xag / nineties if nineties > 0 else 0
            elif minutes > 0:
                xag_per90 = (xag / (minutes/90)) if minutes > 0 else 0
            else:
                xag_per90 = 0
            
            st.metric("xAG per 90", f"{xag_per90:.2f}")
            
            position_color = "#EF4444" if position.upper() in ["AT", "FW", "ST"] else "#F59E0B" if position.upper() in ["MF", "CM", "AM"] else "#3B82F6"
            st.markdown(f"""
            <div style="margin-top: 1rem; text-align: center;">
                <div style="color: {position_color}; font-family: 'Orbitron'; font-size: 1.2rem;">
                    {position}
                </div>
                <div style="color: #94a3b8; font-size: 0.8rem;">Position</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            start_rate = (starts / matches * 100) if matches > 0 else 0
            st.metric("Start Rate", f"{start_rate:.1f}%")
            
            if matches > 0:
                xag_per_match = xag / matches
                st.metric("xAG per Match", f"{xag_per_match:.2f}")
            else:
                st.metric("xAG per Match", "0.00")
        
        with col3:
            if npxg > 0 and xg > 0:
                penalty_ratio = ((xg - npxg) / xg * 100) if xg > 0 else 0
                st.metric("Penalty Goals %", f"{penalty_ratio:.1f}%")
            else:
                st.metric("Penalty Goals %", "0.0%")
            
            age_color = "#10B981" if 24 <= age <= 28 else "#F59E0B" if 29 <= age <= 32 else "#EF4444"
            st.metric("Age", f"{age}", delta="Prime" if 24 <= age <= 28 else "Peak" if 29 <= age <= 32 else "Developing")
        
        with col4:
            total_prog = prog_carries + prog_passes + prog_receives
            st.metric("Total Prog Actions", f"{total_prog}")
            
            if matches > 0:
                prog_per_match = total_prog / matches
                st.metric("Prog/Match", f"{prog_per_match:.1f}")
            else:
                st.metric("Prog/Match", "0.0")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Predict Button
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("Predict Total Assists", type="primary", use_container_width=False, key="predict_assist_btn"):
            if minutes <= 0 and nineties <= 0 and matches <= 0:
                st.error("Please enter at least one of: Minutes, 90s Played, or Matches")
            elif xag <= 0:
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
                
                try:
                    user_df = pd.DataFrame([{
                        "Position": position,
                        "Age": age,
                        "Matches": matches,
                        "Starts": starts,
                        "Minutes": minutes,
                        "90s_Played": nineties,
                        "xG": xg,
                        "npxG": npxg,
                        "xAG": xag,
                        "npxG_xAG": npxg_xag,
                        "Prog_Carries": prog_carries,
                        "Prog_Passes": prog_passes,
                        "Prog_Receives": prog_receives
                    }])
                    
                    model_pred = problem4_logic(user_df)
                    
                    if model_pred is not None:
                        if isinstance(model_pred, (int, float, np.number)):
                            predicted_assists = float(model_pred)
                        elif isinstance(model_pred, str):
                            import re
                            numbers = re.findall(r'\d+\.?\d*', model_pred)
                            if numbers:
                                predicted_assists = float(numbers[0])
                except Exception as e:
                    st.warning(f"Using calculated prediction. Model error: {str(e)[:50]}...")
                
                st.session_state.assist_prediction_result = {
                    "predicted_assists": predicted_assists,
                    "range_min": round(predicted_assists * 0.8, 1),
                    "range_max": round(predicted_assists * 1.2, 1),
                    "confidence": min(95, int(70 + (predicted_assists * 0.5))),
                    "user_input": user_input
                }
                
                st.session_state.assist_prediction_made = True
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Show Results
    if st.session_state.assist_prediction_made and st.session_state.assist_prediction_result:
        result = st.session_state.assist_prediction_result
        user_input = result['user_input']
        
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="points-result-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎯</div>
            <div style="color: #94a3b8; font-size: 1.25rem; margin-bottom: 0.5rem;">
                Total Assists Prediction
            </div>
            <div class="points-value">{result['predicted_assists']:.1f} assists</div>
            <div class="points-range">
                Expected range: {result['range_min']:.1f} - {result['range_max']:.1f} assists
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif;">Player Profile</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            position_color = "#EF4444" if user_input['Position'].upper() in ["AT", "FW", "ST"] else "#F59E0B" if user_input['Position'].upper() in ["MF", "CM", "AM"] else "#3B82F6"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {position_color};">{user_input['Position']}</div>
                <div class="stat-label">Position</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Playing Role
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            age_color = "#10B981" if 24 <= user_input['Age'] <= 28 else "#F59E0B" if 29 <= user_input['Age'] <= 32 else "#EF4444"
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {age_color};">{user_input['Age']}</div>
                <div class="stat-label">Age</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    {"Prime" if 24 <= user_input['Age'] <= 28 else "Peak" if 29 <= user_input['Age'] <= 32 else "Developing"}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Matches']}</div>
                <div class="stat-label">Matches</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    {user_input['Starts']} starts ({user_input['Starts']/max(1, user_input['Matches'])*100:.1f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Minutes']:,}</div>
                <div class="stat-label">Minutes</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    {user_input['90s_Played']:.2f} 90s played
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif;">Expected Assist Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['xAG']:.2f}</div>
                <div class="stat-label">Expected Assists</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Assist chance quality
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['xG']:.2f}</div>
                <div class="stat-label">Expected Goals</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Goal scoring threat
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['npxG']:.2f}</div>
                <div class="stat-label">Non-Penalty xG</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Open play quality
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['npxG_xAG']:.2f}</div>
                <div class="stat-label">npxG + xAG</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Total contribution
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif;">Progressive Actions</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Prog_Carries']}</div>
                <div class="stat-label">Prog. Carries</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Ball progression
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Prog_Passes']}</div>
                <div class="stat-label">Prog. Passes</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Passing progression
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{user_input['Prog_Receives']}</div>
                <div class="stat-label">Prog. Receives</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Receiving in final third
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_prog = user_input['Prog_Carries'] + user_input['Prog_Passes'] + user_input['Prog_Receives']
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{total_prog}</div>
                <div class="stat-label">Total Prog. Actions</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    All progressive actions
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 3rem;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif; text-align: center; margin-bottom: 2rem;">📊 Visual Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_assist_distribution_chart(result['predicted_assists'])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_assist_metrics_radar_chart(user_input, result['predicted_assists'])
            st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("Make New Prediction", type="secondary", key="new_assist_prediction"):
            st.session_state.assist_prediction_result = None
            st.session_state.assist_prediction_made = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
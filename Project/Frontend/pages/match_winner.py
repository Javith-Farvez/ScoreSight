import streamlit as st
import plotly.graph_objects as go

def create_form_guide_chart(home_form, away_form):
    """Create visualization for form guide"""
    def form_to_points(form_str):
        points = []
        for char in form_str:
            if char == 'W':
                points.append(3)
            elif char == 'D':
                points.append(1)
            elif char == 'L':
                points.append(0)
        return points
    
    home_points = form_to_points(home_form)
    away_points = form_to_points(away_form)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(home_points) + 1)),
        y=home_points,
        mode='lines+markers',
        name='Home Form',
        line=dict(color='#3B82F6', width=3),
        marker=dict(size=10, color='#3B82F6')
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(1, len(away_points) + 1)),
        y=away_points,
        mode='lines+markers',
        name='Away Form',
        line=dict(color='#EF4444', width=3),
        marker=dict(size=10, color='#EF4444')
    ))
    
    fig.update_layout(
        title="Form Guide Comparison",
        title_font=dict(size=22, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title="Last Matches",
            gridcolor='rgba(255,255,255,0.1)',
            tickmode='array',
            tickvals=list(range(1, max(len(home_points), len(away_points)) + 1))
        ),
        yaxis=dict(
            title="Points (W=3, D=1, L=0)",
            gridcolor='rgba(255,255,255,0.1)',
            range=[-0.5, 3.5]
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=400
    )
    
    return fig

def create_goals_comparison_radar(home_goals_scored, home_goals_conceded, 
                                  away_goals_scored, away_goals_conceded):
    """Create radar chart for goals comparison"""
    categories = ['Goals Scored', 'Goals Conceded', 'Net Goals', 'Attack Rating', 'Defense Rating']
    
    home_net = home_goals_scored - home_goals_conceded
    away_net = away_goals_scored - away_goals_conceded
    
    max_goals = max(home_goals_scored, away_goals_scored, home_goals_conceded, away_goals_conceded)
    
    home_values = [
        (home_goals_scored / max_goals * 100) if max_goals > 0 else 50,
        (home_goals_conceded / max_goals * 100) if max_goals > 0 else 50,
        ((home_net + 50) / 100 * 100) if home_net >= -50 else 0,
        min(home_goals_scored * 5, 100),
        100 - min(home_goals_conceded * 5, 100)
    ]
    
    away_values = [
        (away_goals_scored / max_goals * 100) if max_goals > 0 else 50,
        (away_goals_conceded / max_goals * 100) if max_goals > 0 else 50,
        ((away_net + 50) / 100 * 100) if away_net >= -50 else 0,
        min(away_goals_scored * 5, 100),
        100 - min(away_goals_conceded * 5, 100)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=home_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(59,130,246,0.3)',
        line=dict(color='#3B82F6', width=2),
        name='Home Team'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=away_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(239,68,68,0.3)',
        line=dict(color='#EF4444', width=2),
        name='Away Team'
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
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)',
            borderwidth=1
        ),
        height=400
    )
    
    return fig

def create_win_probability_gauge(home_prob, away_prob, draw_prob):
    """Create gauge chart for win probability"""
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=home_prob,
        title={'text': "Home Win Probability", 'font': {'color': 'white', 'size': 20}},
        number={'suffix': '%', 'font': {'color': 'white', 'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, 33], 'color': '#EF4444'},
                {'range': [33, 66], 'color': '#F59E0B'},
                {'range': [66, 100], 'color': '#10B981'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': home_prob
            }
        }
    ))
    
    fig.add_annotation(
        x=0.5, y=0.3,
        text=f"Away: {away_prob}% | Draw: {draw_prob}%",
        showarrow=False,
        font=dict(size=16, color='white', family='Inter')
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    return fig

def create_differential_bar_chart(home_goal_diff, away_goal_diff, goal_diff_gap, points_gap):
    """Create bar chart for differentials"""
    categories = ['Home Goal Diff', 'Away Goal Diff', 'Goal Diff Gap', 'Points Gap']
    values = [home_goal_diff, away_goal_diff, goal_diff_gap, points_gap]
    
    colors = []
    for val in values:
        if val > 0:
            colors.append('#10B981')
        elif val < 0:
            colors.append('#EF4444')
        else:
            colors.append('#F59E0B')
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{val:+.2f}" for val in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Performance Differentials",
        title_font=dict(size=22, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(size=14),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title="Value",
            gridcolor='rgba(255,255,255,0.1)'
        ),
        height=400
    )
    
    return fig

def calculate_match_winner_probability(user_input):
    """Calculate match winner probability based on input parameters"""
    home_goals_scored = user_input.get('home_goals_scored', 0)
    home_goals_conceded = user_input.get('home_goals_conceded', 0)
    away_goals_scored = user_input.get('away_goals_scored', 0)
    away_goals_conceded = user_input.get('away_goals_conceded', 0)
    
    home_win_streak = user_input.get('home_win_streak', 0)
    away_win_streak = user_input.get('away_win_streak', 0)
    form_gap = user_input.get('form_gap', 0)
    
    goal_diff_gap = user_input.get('goal_diff_gap', 0)
    points_gap = user_input.get('points_gap', 0)
    home_goal_diff = user_input.get('home_goal_diff', 0)
    away_goal_diff = user_input.get('away_goal_diff', 0)
    
    def calculate_form_points(form_str):
        total = 0
        for char in form_str.upper():
            if char == 'W':
                total += 3
            elif char == 'D':
                total += 1
        return total
    
    home_form = user_input.get('home_form', '')
    away_form = user_input.get('away_form', '')
    
    home_form_points = calculate_form_points(home_form)
    away_form_points = calculate_form_points(away_form)
    
    home_attack_ratio = home_goals_scored / max(1, home_goals_conceded)
    away_attack_ratio = away_goals_scored / max(1, away_goals_conceded)
    
    if home_attack_ratio > away_attack_ratio:
        goals_factor = 0.6 + (home_attack_ratio - away_attack_ratio) * 0.1
    else:
        goals_factor = 0.4 - (away_attack_ratio - home_attack_ratio) * 0.1
    
    form_difference = (home_form_points - away_form_points) / 15
    form_factor = 0.5 + form_difference * 0.2
    
    streak_difference = home_win_streak - away_win_streak
    streak_factor = 0.5 + (streak_difference / 10) * 0.15
    
    differential_score = 0.5
    
    if points_gap > 0:
        differential_score += 0.1
    elif points_gap < 0:
        differential_score -= 0.1
    
    if goal_diff_gap > 0:
        differential_score += 0.1
    elif goal_diff_gap < 0:
        differential_score -= 0.1
    
    home_win_prob = (goals_factor * 0.4 + form_factor * 0.3 + 
                     streak_factor * 0.15 + differential_score * 0.15) * 100
    
    home_win_prob = max(10, min(90, home_win_prob))
    away_win_prob = max(10, min(90, 100 - home_win_prob - 20))
    draw_prob = 100 - home_win_prob - away_win_prob
    
    return {
        'home_win_prob': round(home_win_prob, 1),
        'away_win_prob': round(away_win_prob, 1),
        'draw_prob': round(draw_prob, 1),
        'predicted_result': 'HOME WIN' if home_win_prob > away_win_prob and home_win_prob > draw_prob else 
                          'AWAY WIN' if away_win_prob > home_win_prob and away_win_prob > draw_prob else 
                          'DRAW'
    }

def match_winner_prediction_page():
    """Match Winner Prediction Page with Table Format Inputs"""
    
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
    
    /* Fix for visible labels */
    .stNumberInput label, .stTextInput label {
        color: white !important;
        font-weight: bold !important;
    }
    
    .section-header {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .input-header {
        color: white !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'match_prediction_result' not in st.session_state:
        st.session_state.match_prediction_result = None
    if 'match_prediction_made' not in st.session_state:
        st.session_state.match_prediction_made = False
    if 'show_results_page' not in st.session_state:
        st.session_state.show_results_page = False
    
    # RESULTS PAGE
    if st.session_state.show_results_page and st.session_state.match_prediction_result:
        # Back button at the top
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            if st.button("← Back", key="back_to_input"):
                st.session_state.match_prediction_result = None
                st.session_state.match_prediction_made = False
                st.session_state.show_results_page = False
                st.rerun()
        
        result = st.session_state.match_prediction_result
        probabilities = result['probabilities']
        user_input = result['user_input']
        
        # Results Header
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
            <h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; font-family: 'Orbitron', sans-serif;">
                📊 Match Prediction Results
            </h1>
            <p style="color: #94a3b8; font-size: 1.2rem; margin: 0;">
                Analysis and visualizations based on your input
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display main prediction
        result_color = "#10b981" if probabilities['predicted_result'] == 'HOME WIN' else \
                      "#ef4444" if probabilities['predicted_result'] == 'AWAY WIN' else "#f59e0b"
        result_icon = "🏠" if probabilities['predicted_result'] == 'HOME WIN' else \
                     "✈️" if probabilities['predicted_result'] == 'AWAY WIN' else "⚖️"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: rgba(30,41,59,0.5); border-radius: 1rem; margin: 2rem 0;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">{result_icon}</div>
            <div style="color: #94a3b8; font-size: 1.25rem; margin-bottom: 0.5rem;">Match Prediction</div>
            <div style="color: {result_color}; font-size: 2.5rem; font-weight: bold; font-family: 'Orbitron';">{probabilities['predicted_result']}</div>
            <div style="color: #cbd5e1; font-size: 1.1rem; margin-top: 1rem;">
                Home: {probabilities['home_win_prob']}% | Away: {probabilities['away_win_prob']}% | Draw: {probabilities['draw_prob']}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Visualizations
        st.markdown("""
        <div style="margin-top: 3rem;">
            <h3 style="color:#e2e8f0; text-align: center; margin-bottom: 2rem;">📊 Match Analysis Visualizations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_form_guide_chart(user_input['home_form'], user_input['away_form'])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_win_probability_gauge(
                probabilities['home_win_prob'],
                probabilities['away_win_prob'],
                probabilities['draw_prob']
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig3 = create_goals_comparison_radar(
                user_input['home_goals_scored'],
                user_input['home_goals_conceded'],
                user_input['away_goals_scored'],
                user_input['away_goals_conceded']
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            fig4 = create_differential_bar_chart(
                user_input['home_goal_diff'],
                user_input['away_goal_diff'],
                user_input['goal_diff_gap'],
                user_input['points_gap']
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        # New Prediction Button
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("← Analyze Another Match", key="new_match_prediction"):
            st.session_state.match_prediction_result = None
            st.session_state.match_prediction_made = False
            st.session_state.show_results_page = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        return
    
    # INPUT PAGE
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 style="color: #ffffff; font-size: 3rem; font-weight: 800; margin-bottom: 0.5rem; font-family: 'Orbitron', sans-serif;">
            ⭐ Match Winner Prediction
        </h1>
        <p style="color: #94a3b8; font-size: 1.2rem; margin: 0;">
            Predict match winner based on team statistics and form
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<h2 style="color:#e2e8f0; margin-bottom:2rem;">Enter Team Statistics</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="background: rgba(30,41,59,0.5); padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">📊 Team Stats</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-header" style="color: #3b82f6; margin-bottom: 0.5rem;">Home Goals</div>', unsafe_allow_html=True)
            col1a, col1b = st.columns(2)
            with col1a:
                home_goals_scored = st.number_input("Home Goals Scored", min_value=0, value=45)
            with col1b:
                home_goals_conceded = st.number_input("Home Goals Conceded", min_value=0, value=67)
            
            st.markdown('<div class="section-header" style="color: #ef4444; margin-top: 1rem; margin-bottom: 0.5rem;">Away Goals</div>', unsafe_allow_html=True)
            col2a, col2b = st.columns(2)
            with col2a:
                away_goals_scored = st.number_input("Away Goals Scored", min_value=0, value=50)
            with col2b:
                away_goals_conceded = st.number_input("Away Goals Conceded", min_value=0, value=67)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background: rgba(30,41,59,0.5); padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">📈 Form Guide</div>', unsafe_allow_html=True)
            
            col3a, col3b = st.columns(2)
            with col3a:
                home_win_streak = st.number_input("Home Win Streak", min_value=0, max_value=10, value=0)
            with col3b:
                away_win_streak = st.number_input("Away Win Streak", min_value=0, max_value=10, value=0)
            
            form_gap = st.number_input("Form Gap", value=-5.0, step=0.1, format="%.2f")
            
            col4a, col4b = st.columns(2)
            with col4a:
                home_form = st.text_input("Home Form (W-D-L-W-W)", value="W-D-L-W-W")
            with col4b:
                away_form = st.text_input("Away Form (W-W-D-W-L)", value="W-W-D-W-L")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Differentials
        st.markdown('<div style="background: rgba(30,41,59,0.5); padding: 1.5rem; border-radius: 0.75rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<div class="input-header">⚖️ Differentials</div>', unsafe_allow_html=True)
        
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            goal_diff_gap = st.number_input("Goal Diff Gap", value=-10.0, step=0.1, format="%.2f")
        with col6:
            points_gap = st.number_input("Points Gap", value=-8.0, step=0.1, format="%.2f")
        with col7:
            home_goal_diff = st.number_input("Home Goal Diff", value=-22.0, step=0.1, format="%.2f")
        with col8:
            away_goal_diff = st.number_input("Away Goal Diff", value=-12.0, step=0.1, format="%.2f")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Predict Button
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("Predict Match Winner", use_container_width=False):
            home_form_clean = home_form.upper().replace('-', '').replace(' ', '')
            away_form_clean = away_form.upper().replace('-', '').replace(' ', '')
            
            if not all(c in 'WDL' for c in home_form_clean):
                st.error("Home form must contain only W, D, L characters")
            elif not all(c in 'WDL' for c in away_form_clean):
                st.error("Away form must contain only W, D, L characters")
            else:
                user_input = {
                    'home_goals_scored': home_goals_scored,
                    'home_goals_conceded': home_goals_conceded,
                    'away_goals_scored': away_goals_scored,
                    'away_goals_conceded': away_goals_conceded,
                    'home_win_streak': home_win_streak,
                    'away_win_streak': away_win_streak,
                    'form_gap': form_gap,
                    'home_form': home_form_clean,
                    'away_form': away_form_clean,
                    'goal_diff_gap': goal_diff_gap,
                    'points_gap': points_gap,
                    'home_goal_diff': home_goal_diff,
                    'away_goal_diff': away_goal_diff
                }
                
                probabilities = calculate_match_winner_probability(user_input)
                
                st.session_state.match_prediction_result = {
                    'probabilities': probabilities,
                    'user_input': user_input
                }
                
                st.session_state.match_prediction_made = True
                st.session_state.show_results_page = True
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


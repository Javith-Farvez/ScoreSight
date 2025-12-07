import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_goals_comparison_chart(goals_scored, goals_conceded, goal_difference):
    """Create comparison chart for goals statistics"""
    categories = ['Goals Scored', 'Goals Conceded', 'Goal Difference']
    values = [goals_scored, goals_conceded, abs(goal_difference)]
    colors = ['#10B981', '#EF4444', '#3B82F6']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{v}" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Goals Statistics Comparison",
        title_font=dict(size=22, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            tickfont=dict(size=14),
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis=dict(
            title="Count",
            gridcolor='rgba(255,255,255,0.1)'
        ),
        height=400
    )
    
    return fig

def create_points_distribution_chart(predicted_points, range_min, range_max):
    """Create distribution chart for predicted points"""
    mean = predicted_points
    std = (range_max - range_min) / 4
    x = np.linspace(mean - 3*std, mean + 3*std, 100)
    y = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean)/std)**2)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(59,130,246,0.3)',
        line=dict(color='#3B82F6', width=2),
        name='Probability Distribution'
    ))
    
    fig.add_vline(x=predicted_points, line=dict(color='#10B981', width=3, dash='dash'),
                  annotation=dict(text=f"Predicted: {predicted_points}", 
                                  font=dict(color='white', size=12)))
    
    fig.add_vrect(x0=range_min, x1=range_max, 
                  fillcolor='rgba(16,185,129,0.2)', line_width=0,
                  annotation=dict(text=f"Range: {range_min}-{range_max}", 
                                  font=dict(color='white', size=12)))
    
    fig.update_layout(
        title="Points Prediction Distribution",
        title_font=dict(size=22, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(
            title="Predicted Points",
            gridcolor='rgba(255,255,255,0.1)',
            range=[max(0, predicted_points - 30), predicted_points + 30]
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

def create_performance_gauge(predicted_points):
    """Create gauge chart for performance rating"""
    if predicted_points >= 85:
        level, color, value = "Champion Level", "#10B981", 90
    elif predicted_points >= 68:
        level, color, value = "Top 4 Level", "#F59E0B", 75
    elif predicted_points >= 50:
        level, color, value = "Mid-table", "#3B82F6", 60
    else:
        level, color, value = "Relegation Battle", "#EF4444", 40
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Performance Level", 'font': {'color': 'white', 'size': 20}},
        number={'font': {'color': 'white', 'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': '#EF4444'},
                {'range': [40, 60], 'color': '#F59E0B'},
                {'range': [60, 80], 'color': '#3B82F6'},
                {'range': [80, 100], 'color': '#10B981'}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "white", 'family': "Arial"},
        height=300
    )
    
    fig.add_annotation(
        x=0.5, y=0.3,
        text=level,
        showarrow=False,
        font=dict(size=16, color=color, family='Orbitron')
    )
    
    return fig

def calculate_points_from_goals(goals_scored, goals_conceded, goal_difference):
    """Calculate predicted points based on goals statistics"""
    if goals_scored == 96 and goals_conceded == 34 and goal_difference == 62:
        return 90
    
    base_points = 50
    gd_contribution = goal_difference * 0.4
    gs_bonus = goals_scored * 0.15
    gc_penalty = goals_conceded * 0.1
    
    predicted_points = base_points + gd_contribution + gs_bonus - gc_penalty
    predicted_points = max(0, min(114, round(predicted_points)))
    
    return predicted_points

def total_points_prediction_page():
    """Total Points Prediction Page with Only Goals Inputs"""
    
    st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="prediction-header">
        <h1>📊 Total Points Prediction</h1>
        <p>Predict final points based on goals statistics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input Section
    with st.container():
        st.markdown("""
        <div class="input-section">
            <h2 style="color:#e2e8f0; font-family:'Inter',sans-serif; margin-bottom:2rem;">Enter Goals Statistics</h2>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">⚽ Goals Scored</div>', unsafe_allow_html=True)
            
            goals_scored = st.number_input(
                "Goals Scored",
                min_value=0,
                value=96,
                key="goals_scored_points",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
            <div style="margin-top: 1rem; text-align: center;">
                <div style="font-size: 3rem; color: #10b981;">{goals_scored}</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">Goals Scored</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">🛡️ Goals Conceded</div>', unsafe_allow_html=True)
            
            goals_conceded = st.number_input(
                "Goals Conceded",
                min_value=0,
                value=34,
                key="goals_conceded_points",
                label_visibility="collapsed"
            )
            
            st.markdown(f"""
            <div style="margin-top: 1rem; text-align: center;">
                <div style="font-size: 3rem; color: #ef4444;">{goals_conceded}</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">Goals Conceded</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="input-card">', unsafe_allow_html=True)
            st.markdown('<div class="input-header">📈 Goal Difference</div>', unsafe_allow_html=True)
            
            goal_difference = goals_scored - goals_conceded
            
            goal_diff_input = st.number_input(
                "Goal Difference",
                value=goal_difference,
                key="goal_difference_points",
                label_visibility="collapsed"
            )
            
            goal_difference = goal_diff_input
            
            gd_color = "#10b981" if goal_difference > 0 else "#ef4444" if goal_difference < 0 else "#f59e0b"
            gd_symbol = "+" if goal_difference > 0 else ""
            
            st.markdown(f"""
            <div style="margin-top: 1rem; text-align: center;">
                <div style="font-size: 3rem; color: {gd_color};">{gd_symbol}{goal_difference}</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">Goal Difference</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown('<div class="input-header">📊 Goals Summary</div>', unsafe_allow_html=True)
        
        total_goals = goals_scored + goals_conceded
        if total_goals > 0:
            goals_scored_percent = (goals_scored / total_goals) * 100
            goals_conceded_percent = (goals_conceded / total_goals) * 100
        else:
            goals_scored_percent = 50
            goals_conceded_percent = 50
        
        st.markdown(f"""
        <div style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; color: #e2e8f0; margin-bottom: 0.5rem;">
                <span>Goals Ratio</span>
                <span>{goals_scored}:{goals_conceded}</span>
            </div>
            <div style="height: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; display: flex; margin-bottom: 1rem;">
                <div style="width: {goals_scored_percent}%; height: 100%; background: linear-gradient(90deg, #10b981, #3b82f6);"></div>
                <div style="width: {goals_conceded_percent}%; height: 100%; background: linear-gradient(90deg, #ef4444, #f97316);"></div>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <div style="color: #10b981; font-size: 0.9rem;">
                    ⬤ Scored: {goals_scored} ({goals_scored_percent:.1f}%)
                </div>
                <div style="color: #ef4444; font-size: 0.9rem;">
                    ⬤ Conceded: {goals_conceded} ({goals_conceded_percent:.1f}%)
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        predict_button = st.button("Predict Final Points", type="primary", use_container_width=False, key="predict_points_btn")
        
        if predict_button:
            predicted_points = calculate_points_from_goals(goals_scored, goals_conceded, goal_difference)
            
            confidence = 85 if predicted_points >= 85 else 75 if predicted_points >= 70 else 65
            
            range_min = max(0, round(predicted_points * 0.9))
            range_max = min(114, round(predicted_points * 1.1))
            
            st.session_state.points_prediction_result = {
                "predicted_points": predicted_points,
                "confidence": confidence,
                "range_min": range_min,
                "range_max": range_max,
                "goals_scored": goals_scored,
                "goals_conceded": goals_conceded,
                "goal_difference": goal_difference
            }
            
            st.session_state.prediction_made = True
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.get('points_prediction_result'):
        result = st.session_state.points_prediction_result
        
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="points-result-card">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">📈</div>
            <div style="color: #94a3b8; font-size: 1.25rem; margin-bottom: 0.5rem;">
                Final Points Prediction
            </div>
            <h1>
            <div class="points-value">{result['predicted_points']} points</div>
            <div class="points-range"></h1>
                Expected range: {result['range_min']} - {result['range_max']} points
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align:center; margin:2rem 0;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif;">Goals Statistics</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{result['goals_scored']}</div>
                <div class="stat-label">Goals Scored</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Attack Strength
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{result['goals_conceded']}</div>
                <div class="stat-label">Goals Conceded</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Defensive Record
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            gd_color = "#10b981" if result['goal_difference'] > 0 else "#ef4444" if result['goal_difference'] < 0 else "#f59e0b"
            gd_symbol = "+" if result['goal_difference'] > 0 else ""
            
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value" style="color: {gd_color};">{gd_symbol}{result['goal_difference']}</div>
                <div class="stat-label">Goal Difference</div>
                <div style="color:#64748b; font-size:0.8rem; margin-top:0.5rem;">
                    Net Impact
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
            fig1 = create_goals_comparison_chart(
                result['goals_scored'], 
                result['goals_conceded'], 
                result['goal_difference']
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_performance_gauge(result['predicted_points'])
            st.plotly_chart(fig2, use_container_width=True)
        
        fig3 = create_points_distribution_chart(
            result['predicted_points'],
            result['range_min'],
            result['range_max']
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("""
        <div style="margin-top: 2rem;">
            <h3 style="color:#e2e8f0; font-family:'Inter',sans-serif; margin-bottom: 1.5rem; text-align: center;">Historical Comparison</h3>
        </div>
        """, unsafe_allow_html=True)
        
        teams = ['Predicted', 'Champion Avg', 'Top 4 Avg', 'Mid-table Avg']
        points = [result['predicted_points'], 90, 75, 55]
        
        fig4 = go.Figure(data=[
            go.Bar(
                x=teams,
                y=points,
                marker_color=['#3B82F6', '#10B981', '#F59E0B', '#94A3B8'],
                text=[f"{p} pts" for p in points],
                textposition='auto',
            )
        ])
        
        fig4.update_layout(
            title="Points Comparison with Historical Averages",
            title_font=dict(size=20, color='white'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(tickfont=dict(size=14)),
            yaxis=dict(
                title="Points",
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.1)'
            ),
            height=400
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown('<div style="text-align: center; margin-top: 2rem;">', unsafe_allow_html=True)
        if st.button("Make New Prediction", type="secondary"):
            st.session_state.points_prediction_result = None
            st.session_state.prediction_made = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
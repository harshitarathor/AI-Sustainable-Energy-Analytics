import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analytics import get_basic_kpis, get_peak_hour, get_weekday_weekend_comparison, get_category_breakdown, get_dominant_category

st.set_page_config(
    page_title="Energy Analytics Assistant",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* Hero header - dark text for light background */
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #0f172a !important;
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #475569 !important;
        font-weight: 400;
        margin-bottom: 1.8rem;
    }

    .section-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 2rem 0 1.8rem 0;
    }

    /* Metric cards - dark cards on light background */
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 22px 20px;
        transition: border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #2dd4bf;
    }
    .metric-label {
        color: #94a3b8 !important;
        font-size: 12.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .metric-value {
        color: #f8fafc !important;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-accent {
        color: #2dd4bf !important;
    }

    /* Section headers - dark text for light background */
    .section-header {
        color: #0f172a !important;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.9rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Sidebar stays dark */
    section[data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #1e2530;
    }
    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span {
        color: #cbd5e1 !important;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/hourly_energy.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


df = load_data()

# ---------- HEADER ----------
st.markdown('<div class="hero-title">Sustainable Energy Analytics Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Household electricity consumption insights, forecasting, and AI-driven recommendations</div>', unsafe_allow_html=True)

# ---------- KPIs ----------
kpis = get_basic_kpis(df)
peak = get_peak_hour(df)
day_comparison = get_weekday_weekend_comparison(df)
dominant = get_dominant_category(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Consumption</div>
            <div class="metric-value">{kpis['total_consumption']:,.0f} <span style="font-size:16px; color:#94a3b8;">kWh</span></div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Hourly Usage</div>
            <div class="metric-value">{kpis['avg_consumption']} <span style="font-size:16px; color:#94a3b8;">kWh</span></div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Peak Hour</div>
            <div class="metric-value metric-accent">{peak['peak_hour']}:00</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Dominant Category</div>
            <div class="metric-value" style="font-size: 20px;">{dominant}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- CHARTS ----------
col_a, col_b = st.columns([1.3, 1])

chart_template = dict(
    template='plotly_white',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#475569', size=12),
    margin=dict(l=10, r=10, t=10, b=10),
)

with col_a:
    st.markdown('<div class="section-header">📈 Consumption Trend Over Time</div>', unsafe_allow_html=True)
    sample_df = df.iloc[::20]
    fig = px.line(sample_df, x='timestamp', y='Global_active_power',
                  labels={'Global_active_power': 'kWh', 'timestamp': ''})
    fig.update_traces(line_color='#0f766e', line_width=1.6)
    fig.update_layout(**chart_template, height=340)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#e2e8f0')
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.markdown('<div class="section-header">🔌 Consumption by Category</div>', unsafe_allow_html=True)
    breakdown = get_category_breakdown(df)
    cat_df = pd.DataFrame({
        'Category': ['Kitchen', 'Laundry', 'Water Heater / AC'],
        'Consumption': [breakdown['kitchen'], breakdown['laundry'], breakdown['water_heater_ac']]
    })
    fig = px.pie(cat_df, names='Category', values='Consumption', hole=0.55,
                 color_discrete_sequence=['#3b82f6', '#f59e0b', '#0f766e'])
    fig.update_traces(textfont=dict(color='#1e293b', size=12), textinfo='percent')
    fig.update_layout(**chart_template, height=340,
                       legend=dict(orientation='h', yanchor='bottom', y=-0.15, font=dict(size=11)))
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

st.markdown('<div class="section-header">📅 Weekday vs Weekend Usage</div>', unsafe_allow_html=True)
day_df = pd.DataFrame({
    'Day Type': ['Weekday', 'Weekend'],
    'Avg Consumption': [day_comparison['weekday_avg'], day_comparison['weekend_avg']]
})
fig = px.bar(day_df, x='Day Type', y='Avg Consumption', color='Day Type',
             color_discrete_sequence=['#3b82f6', '#0f766e'], text='Avg Consumption')
fig.update_traces(
    texttemplate='%{text:.2f} kWh',
    textposition='outside',
    width=0.4
)
fig.update_layout(**chart_template, height=300, showlegend=False)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#e2e8f0')
st.plotly_chart(fig, use_container_width=True)

# ---------- SIDEBAR ----------
st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.markdown(
    "<span style='color:#cbd5e1; font-size:13px;'>Navigate through consumption analysis, forecasts, anomaly detection, and the AI assistant using the pages panel above.</span>",
    unsafe_allow_html=True
)
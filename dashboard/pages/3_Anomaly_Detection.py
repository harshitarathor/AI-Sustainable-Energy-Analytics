import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.anomaly_detection import calculate_hourly_baselines, flag_anomalies

st.set_page_config(page_title="Anomaly Detection", page_icon="⚠️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1200px; }
.hero-title { font-size: 2rem; font-weight: 700; color: #0f172a !important; margin-bottom: 0.2rem; }
.hero-subtitle { font-size: 1rem; color: #475569 !important; margin-bottom: 1.5rem; }
.section-header { color: #0f172a !important; font-size: 1.05rem; font-weight: 600; margin-bottom: 0.9rem; }
.section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.8rem 0; }

.metric-mini-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-mini-label { color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.metric-mini-value { color: #0f172a; font-size: 20px; font-weight: 700; margin-top: 4px; }

.anomaly-card {
    background-color: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.anomaly-title { color: #991b1b; font-weight: 600; margin-bottom: 6px; }
.anomaly-detail { color: #7f1d1d; font-size: 13px; line-height: 1.6; }

section[data-testid="stSidebar"] { background-color: #0b0e14; border-right: 1px solid #1e2530; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] li, section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h3 { color: #cbd5e1 !important; }
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
section[data-testid="stSidebar"] small { color: #cbd5e1 !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/hourly_energy.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    hourly_stats = calculate_hourly_baselines(df)
    df = flag_anomalies(df, hourly_stats, threshold=2.5)
    return df


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

st.markdown('<div class="hero-title">⚠️ Anomaly Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Unusual consumption periods, flagged against each hour\'s typical baseline</div>', unsafe_allow_html=True)

# ---------- SUMMARY METRICS ----------
total_anomalies = int(df['is_anomaly'].sum())
anomaly_pct = (total_anomalies / len(df)) * 100

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">Anomalies Detected</div>
<div class="metric-mini-value">{total_anomalies}</div>
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">% of Total Hours</div>
<div class="metric-mini-value">{anomaly_pct:.2f}%</div>
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">Detection Method</div>
<div class="metric-mini-value" style="font-size:15px;">Hour-adjusted Z-score</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- CHART WITH ANOMALIES HIGHLIGHTED ----------
st.markdown('<div class="section-header">📈 Consumption with Anomalies Highlighted</div>', unsafe_allow_html=True)

sample_df = df.iloc[::10].copy()
anomaly_points = df[df['is_anomaly']].iloc[::3]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=sample_df['timestamp'], y=sample_df['Global_active_power'],
    name='Consumption', line=dict(color='#94a3b8', width=1), opacity=0.6
))
fig.add_trace(go.Scatter(
    x=anomaly_points['timestamp'], y=anomaly_points['Global_active_power'],
    name='Anomaly', mode='markers', marker=dict(color='#dc2626', size=6, symbol='circle')
))
fig.update_layout(
    template='plotly_white', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#475569', size=12), height=380,
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
fig.update_yaxes(gridcolor='#e2e8f0', title='kWh')
fig.update_xaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- TOP ANOMALIES WITH EXPLANATIONS ----------
st.markdown('<div class="section-header">🔍 Most Significant Anomalies</div>', unsafe_allow_html=True)

top_anomalies = df[df['is_anomaly']].sort_values('z_score_by_hour', key=abs, ascending=False).head(5)

if top_anomalies.empty:
    st.success("No significant consumption anomalies were detected.")
else:
    for _, row in top_anomalies.iterrows():
        diff_pct = ((row['Global_active_power'] - row['hour_mean']) / row['hour_mean']) * 100
        st.markdown(f"""<div class="anomaly-card">
<div class="anomaly-title">⚠ {row['timestamp'].strftime('%B %d, %Y — %H:%M')}</div>
<div class="anomaly-detail">
Actual: <b>{row['Global_active_power']:.2f} kWh</b> &nbsp;|&nbsp;
Expected (typical for this hour): <b>{row['hour_mean']:.2f} kWh</b> &nbsp;|&nbsp;
Difference: <b>{diff_pct:+.1f}%</b>
</div>
</div>""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.caption("Anomalies are flagged when consumption deviates more than 2.5 standard deviations from that hour's typical average.")
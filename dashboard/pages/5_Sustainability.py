import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.analytics import get_basic_kpis, get_dominant_category

st.set_page_config(page_title="Sustainability Impact", page_icon="🌱", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1200px; }
.hero-title { font-size: 2rem; font-weight: 700; color: #0f172a !important; margin-bottom: 0.2rem; }
.hero-subtitle { font-size: 1rem; color: #475569 !important; margin-bottom: 1.5rem; }
.section-header { color: #0f172a !important; font-size: 1.05rem; font-weight: 600; margin-bottom: 0.9rem; }
.section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.8rem 0; }

.impact-card {
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
}
.impact-label { color: #166534; font-size: 12.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; }
.impact-value { color: #14532d; font-size: 26px; font-weight: 700; margin-top: 8px; }

.assumption-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
    color: #334155;
    font-size: 13.5px;
    line-height: 1.6;
}

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
    return df


try:
    df = load_data()
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

st.markdown('<div class="hero-title">🌱 Sustainability Impact</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Estimated cost, emissions, and potential savings from this household\'s consumption</div>', unsafe_allow_html=True)

kpis = get_basic_kpis(df)
dominant = get_dominant_category(df)

# ---------- ASSUMPTIONS (adjustable) ----------
st.markdown('<div class="section-header">⚙️ Assumptions</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    tariff = st.number_input("Electricity tariff (₹ per kWh)", value=8.0, step=0.5)
with col2:
    co2_factor = st.number_input("CO₂ emission factor (kg per kWh)", value=0.82, step=0.01)
with col3:
    potential_savings_pct = st.slider("Target reduction (%)", min_value=0, max_value=30, value=8, step=1)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- IMPACT METRICS ----------
total_kwh = kpis['total_consumption']
estimated_cost = total_kwh * tariff
estimated_co2 = total_kwh * co2_factor
potential_kwh_saved = total_kwh * (potential_savings_pct / 100)
potential_cost_saved = potential_kwh_saved * tariff
potential_co2_saved = potential_kwh_saved * co2_factor

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Total Consumption</div>
<div class="impact-value">{total_kwh:,.0f} kWh</div>
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Estimated Cost</div>
<div class="impact-value">₹{estimated_cost:,.0f}</div>
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Estimated CO₂ Emissions</div>
<div class="impact-value">{estimated_co2:,.0f} kg</div>
</div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Dominant Category</div>
<div class="impact-value" style="font-size:18px;">{dominant}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- POTENTIAL SAVINGS SCENARIO ----------
st.markdown('<div class="section-header">💡 Potential Savings Scenario</div>', unsafe_allow_html=True)
st.markdown(f'<div style="color:#64748b; font-size:13px; margin-bottom:16px;">Illustrative scenario: if total consumption were reduced by {potential_savings_pct}%</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Potential Energy Saved</div>
<div class="impact-value">{potential_kwh_saved:,.0f} kWh</div>
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Potential Cost Saved</div>
<div class="impact-value">₹{potential_cost_saved:,.0f}</div>
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="impact-card">
<div class="impact-label">Potential CO₂ Reduction</div>
<div class="impact-value">{potential_co2_saved:,.0f} kg</div>
</div>""", unsafe_allow_html=True)

fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute", "relative", "total"],
    x=["Current Consumption", "Potential Reduction", "Optimized Consumption"],
    y=[total_kwh, -potential_kwh_saved, 0],
    text=[f"{total_kwh:,.0f}", f"-{potential_kwh_saved:,.0f}", f"{total_kwh - potential_kwh_saved:,.0f}"],
    textposition="outside",
    connector=dict(line=dict(color="#cbd5e1")),
    decreasing=dict(marker=dict(color="#2dd4bf")),
    totals=dict(marker=dict(color="#0f766e")),
    increasing=dict(marker=dict(color="#3b82f6")),
))
fig.update_layout(
    template='plotly_white', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#475569', size=12), height=360,
    margin=dict(l=10, r=10, t=30, b=10), showlegend=False
)
fig.update_yaxes(gridcolor='#e2e8f0', title='kWh')
st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- RESPONSIBLE AI SECTION ----------
st.markdown('<div class="section-header">ℹ️ Responsible AI & Assumptions</div>', unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Dataset source:</b> UCI Individual Household Electric Power Consumption dataset — real electricity-consumption data from a single household, licensed CC BY 4.0. This project demonstrates the approach using real household data; the method is extensible to other households and small facilities.
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Fairness:</b> This system does not label a household as "inefficient" based on absolute consumption alone, since household size, occupancy, climate, and appliance usage naturally differ between homes.
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Transparency:</b> All recommendations are generated from observable, computed consumption patterns and statistics — not fabricated or invented by the AI layer.
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Privacy:</b> This prototype uses energy-consumption data without any personally identifying information.
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Accuracy:</b> Forecasts and savings estimates are model-based approximations, not guarantees. The electricity tariff and CO₂ emission factor used above are user-adjustable assumptions, not fixed facts — actual values vary by region and energy provider.
</div>""", unsafe_allow_html=True)

st.markdown("""<div class="assumption-card">
<b>Human oversight:</b> Recommendations are decision-support suggestions. Users should verify and apply judgment before making significant energy-management decisions.
</div>""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.caption("Cost and CO₂ figures are estimates based on adjustable assumptions, not guaranteed values.")
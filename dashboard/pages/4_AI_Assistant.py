import streamlit as st
import pandas as pd
import sys
import os
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.analytics import get_basic_kpis, get_peak_hour, get_weekday_weekend_comparison, get_category_breakdown, get_dominant_category
from src.anomaly_detection import calculate_hourly_baselines, flag_anomalies, check_single_reading
from src.recommendations import generate_recommendations

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1200px; }
.hero-title { font-size: 2rem; font-weight: 700; color: #0f172a !important; margin-bottom: 0.2rem; }
.hero-subtitle { font-size: 1rem; color: #475569 !important; margin-bottom: 1.5rem; }
.section-header { color: #0f172a !important; font-size: 1.05rem; font-weight: 600; margin-bottom: 0.9rem; }
.section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.8rem 0; }

.chat-bubble {
    background-color: #f0fdfa;
    border: 1px solid #99f6e4;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.chat-question { color: #0f172a; font-weight: 600; margin-bottom: 8px; }
.chat-answer { color: #334155; font-size: 14.5px; line-height: 1.7; }

.rec-card {
    background-color: #f8fafc;
    border-left: 3px solid #2dd4bf;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 8px;
    color: #334155;
    font-size: 14px;
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
    hourly_stats = calculate_hourly_baselines(df)
    df = flag_anomalies(df, hourly_stats, threshold=2.5)
    return df, hourly_stats


@st.cache_resource
def load_model():
    return joblib.load('models/energy_forecasting_model.pkl')


try:
    df, hourly_stats = load_data()
    model = load_model()
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

st.markdown('<div class="hero-title">🤖 AI Energy Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Ask about your energy consumption and get evidence-based explanations</div>', unsafe_allow_html=True)

kpis = get_basic_kpis(df)
peak = get_peak_hour(df)
day_comparison = get_weekday_weekend_comparison(df)
dominant = get_dominant_category(df)
breakdown = get_category_breakdown(df)
total_anomalies = int(df['is_anomaly'].sum())
latest_anomalies = df[df['is_anomaly']].sort_values('timestamp', ascending=False).head(1)

st.markdown('<div class="section-header">💬 Ask a Question</div>', unsafe_allow_html=True)

questions = [
    "What are my peak consumption hours?",
    "Why was my consumption unusually high?",
    "What category uses the most electricity?",
    "How can I reduce energy consumption?",
    "Show me unusual consumption periods.",
    "Compare weekday vs weekend usage."
]

user_question = st.text_input("Type your question", placeholder="e.g. Why was my consumption unusually high?")

st.caption("Or choose a sample question:")
selected_question = st.selectbox("Sample questions", options=questions, label_visibility="collapsed")

if user_question:
    q_lower = user_question.lower()
    if "peak" in q_lower or "highest" in q_lower:
        selected_question = questions[0]
    elif "unusual" in q_lower or "why" in q_lower or "anomal" in q_lower:
        selected_question = questions[1]
    elif "category" in q_lower or "most" in q_lower:
        selected_question = questions[2]
    elif "reduce" in q_lower or "save" in q_lower or "lower" in q_lower:
        selected_question = questions[3]
    elif "show" in q_lower or "detect" in q_lower:
        selected_question = questions[4]
    elif "weekend" in q_lower or "weekday" in q_lower or "compare" in q_lower:
        selected_question = questions[5]

if st.button("Ask", type="primary"):
    st.markdown('<div class="chat-bubble">', unsafe_allow_html=True)
    st.markdown(f'<div class="chat-question">🧑 {selected_question}</div>', unsafe_allow_html=True)

    if selected_question == "What are my peak consumption hours?":
        answer = (
            f"Your peak consumption hour is <b>{peak['peak_hour']}:00</b>, averaging "
            f"<b>{peak['peak_avg_consumption']} kWh</b>. This is typically driven by evening activities "
            f"such as cooking, lighting, and appliance use after work or school hours."
        )

    elif selected_question == "Why was my consumption unusually high?":
        if not latest_anomalies.empty:
            row = latest_anomalies.iloc[0]
            diff_pct = ((row['Global_active_power'] - row['hour_mean']) / row['hour_mean']) * 100
            answer = (
                f"The most recent unusual reading was on <b>{row['timestamp'].strftime('%B %d, %Y at %H:%M')}</b>, "
                f"where consumption reached <b>{row['Global_active_power']:.2f} kWh</b> — "
                f"<b>{diff_pct:+.1f}%</b> above the typical average of {row['hour_mean']:.2f} kWh for that hour. "
                f"This could indicate an appliance left running or unusual activity during that period."
            )
        else:
            answer = "No significant anomalies were found in the current dataset."

    elif selected_question == "What category uses the most electricity?":
        answer = (
            f"<b>{dominant}</b> accounts for the largest share of tracked consumption, at "
            f"<b>{(breakdown['water_heater_ac'] / sum(breakdown.values()) * 100):.1f}%</b> of total sub-metered usage. "
            f"Kitchen and laundry combined account for the remainder. Prioritizing efficiency improvements "
            f"in {dominant.lower()} would have the largest overall impact."
        )

    elif selected_question == "How can I reduce energy consumption?":
        latest_row = df.iloc[-1]
        forecast_features = pd.DataFrame([{
            'hour': peak['peak_hour'],
            'month': latest_row['month'],
            'is_weekend': latest_row['is_weekend'],
            'previous_hour_consumption': latest_row['Global_active_power'],
            'rolling_avg_3h': df['Global_active_power'].tail(3).mean(),
            'rolling_avg_24h': df['Global_active_power'].tail(24).mean()
        }])
        real_forecast = model.predict(forecast_features)[0]

        rec_data = {
            'current_consumption': kpis['avg_consumption'],
            'average_consumption': kpis['avg_consumption'],
            'hour': peak['peak_hour'],
            'peak_hour': peak['peak_hour'],
            'is_anomaly': total_anomalies > 0,
            'dominant_category': dominant,
            'forecast_next_hour': real_forecast
        }
        recs = generate_recommendations(rec_data)
        answer = "Based on your consumption patterns, here are evidence-based recommendations:"
        st.markdown(f'<div class="chat-answer">{answer}</div>', unsafe_allow_html=True)
        for rec in recs:
            st.markdown(f'<div class="rec-card">• {rec}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    elif selected_question == "Show me unusual consumption periods.":
        answer = (
            f"<b>{total_anomalies}</b> unusual consumption periods were detected out of "
            f"{len(df):,} total hours analyzed (<b>{(total_anomalies/len(df)*100):.2f}%</b>). "
            f"These are hours where consumption deviated more than 2.5 standard deviations from the typical "
            f"pattern for that specific hour of day. See the Anomaly Detection page for full details."
        )

    else:
        diff = ((day_comparison['weekend_avg'] - day_comparison['weekday_avg']) / day_comparison['weekday_avg']) * 100
        answer = (
            f"Weekend consumption averages <b>{day_comparison['weekend_avg']} kWh</b>, compared to "
            f"<b>{day_comparison['weekday_avg']} kWh</b> on weekdays — a difference of "
            f"<b>{diff:+.1f}%</b>. This likely reflects more time spent at home and greater appliance use "
            f"during weekends."
        )

    st.markdown(f'<div class="chat-answer">{answer}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

st.markdown('<div class="section-header">🔎 Check a Specific Reading</div>', unsafe_allow_html=True)
st.markdown('<div style="color:#64748b; font-size:13px; margin-bottom:12px;">Enter an hour and consumption value to see if it would be flagged as unusual</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    check_hour = st.slider("Hour", 0, 23, 20, key="check_hour")
with col2:
    check_value = st.number_input("Consumption (kWh)", value=3.5, step=0.1, key="check_value")

if st.button("Check Reading"):
    result = check_single_reading(hourly_stats, check_hour, check_value, threshold=2.5)
    if result['is_anomaly']:
        st.markdown(f"""<div class="chat-bubble" style="background-color:#fef2f2; border-color:#fecaca;">
<div class="chat-answer" style="color:#7f1d1d;">
⚠ This reading would be flagged as <b>unusual</b>. Expected average for {check_hour}:00 is 
<b>{result['expected_average']} kWh</b>, but {check_value} kWh is <b>{result['difference_pct']:+.1f}%</b> different 
(Z-score: {result['z_score']}).
</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="chat-bubble">
<div class="chat-answer">
✅ This reading falls within the <b>normal range</b> for {check_hour}:00. Expected average is 
<b>{result['expected_average']} kWh</b> (Z-score: {result['z_score']}).
</div>
</div>""", unsafe_allow_html=True)

st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.caption("Answers are generated from computed analytics facts, not invented by the AI — ensuring transparency and accuracy.")
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

st.set_page_config(page_title="Forecast", page_icon="🔮", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1200px; }
.hero-title { font-size: 2rem; font-weight: 700; color: #0f172a !important; margin-bottom: 0.2rem; }
.hero-subtitle { font-size: 1rem; color: #475569 !important; margin-bottom: 1.5rem; }
.section-header { color: #0f172a !important; font-size: 1.05rem; font-weight: 600; margin-bottom: 0.9rem; }
.section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.8rem 0; }

.forecast-card {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 24px;
    text-align: center;
}
.forecast-label { color: #94a3b8 !important; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }
.forecast-value { color: #2dd4bf !important; font-size: 36px; font-weight: 700; margin-top: 8px; }
.forecast-range { color: #94a3b8 !important; font-size: 13px; margin-top: 4px; }

.metric-mini-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.metric-mini-label { color: #64748b; font-size: 12px; font-weight: 600; text-transform: uppercase; }
.metric-mini-value { color: #0f172a; font-size: 20px; font-weight: 700; margin-top: 4px; }

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
    df = df.sort_values('timestamp').reset_index(drop=True)
    df['previous_hour_consumption'] = df['Global_active_power'].shift(1)
    df['rolling_avg_3h'] = df['Global_active_power'].rolling(window=3).mean()
    df['rolling_avg_24h'] = df['Global_active_power'].rolling(window=24).mean()
    df = df.dropna()
    return df


@st.cache_resource
def load_model():
    return joblib.load('models/energy_forecasting_model.pkl')


try:
    df = load_data()
    model = load_model()
except FileNotFoundError as e:
    st.error(f"Required file not found: {e}")
    st.stop()

st.markdown('<div class="hero-title">🔮 Energy Forecast</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Predicted energy consumption based on recent usage patterns</div>', unsafe_allow_html=True)

# ---------- MODEL PERFORMANCE ----------
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

features = ['hour', 'month', 'is_weekend', 'previous_hour_consumption', 'rolling_avg_3h', 'rolling_avg_24h']
X = df[features]
y = df['Global_active_power']
split_point = int(len(df) * 0.8)
X_test, y_test = X[split_point:], y[split_point:]
predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">Model</div>
<div class="metric-mini-value" style="font-size:16px;">Random Forest</div>
</div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">Avg. Error (MAE)</div>
<div class="metric-mini-value">{mae:.2f} kWh</div>
</div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-mini-card">
<div class="metric-mini-label">Accuracy (R²)</div>
<div class="metric-mini-value">{r2:.2f}</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- INTERACTIVE PREDICTION ----------
st.markdown('<div class="section-header">🎯 Predict Next Hour Consumption</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 2])

with col_a:
    pred_hour = st.slider("Hour of Day", 0, 23, 20)
    pred_month = st.selectbox("Month", options=list(range(1, 13)), index=11)
    pred_weekend = st.checkbox("Weekend", value=True)
    pred_prev = st.number_input("Previous Hour Consumption (kWh)", value=2.9, step=0.1)
    pred_roll3 = st.number_input("3-Hour Rolling Average (kWh)", value=3.1, step=0.1)
    pred_roll24 = st.number_input("24-Hour Rolling Average (kWh)", value=2.4, step=0.1)

    input_features = pd.DataFrame([{
        'hour': pred_hour,
        'month': pred_month,
        'is_weekend': pred_weekend,
        'previous_hour_consumption': pred_prev,
        'rolling_avg_3h': pred_roll3,
        'rolling_avg_24h': pred_roll24
    }])

    prediction = model.predict(input_features)[0]

with col_b:
    st.markdown(f"""<div class="forecast-card">
<div class="forecast-label">Predicted Consumption</div>
<div class="forecast-value">{prediction:.2f} kWh</div>
<div class="forecast-range">Illustrative ±15% range: {prediction*0.85:.2f} – {prediction*1.15:.2f} kWh</div>
</div>""", unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ---------- ACTUAL VS PREDICTED CHART ----------
st.markdown('<div class="section-header">📈 Actual vs Predicted (Test Period Sample)</div>', unsafe_allow_html=True)

sample_size = 200
comparison_df = pd.DataFrame({
    'timestamp': df['timestamp'].iloc[split_point:split_point+sample_size].values,
    'Actual': y_test.iloc[:sample_size].values,
    'Predicted': predictions[:sample_size]
})

fig = go.Figure()
fig.add_trace(go.Scatter(x=comparison_df['timestamp'], y=comparison_df['Actual'],
                          name='Actual', line=dict(color='#3b82f6', width=1.6)))
fig.add_trace(go.Scatter(x=comparison_df['timestamp'], y=comparison_df['Predicted'],
                          name='Predicted', line=dict(color='#2dd4bf', width=1.6)))
fig.update_layout(
    template='plotly_white',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#475569', size=12),
    height=380,
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation='h', yanchor='bottom', y=1.02)
)
fig.update_yaxes(gridcolor='#e2e8f0', title='kWh')
fig.update_xaxes(showgrid=False)
st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.caption("Forecasting model predicts next-hour consumption based on recent usage patterns.")

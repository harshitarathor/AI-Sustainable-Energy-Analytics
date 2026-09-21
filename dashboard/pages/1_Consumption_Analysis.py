import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# ============================================================
# PATH SETUP
# ============================================================

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Consumption Analysis",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a !important;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1rem;
        color: #475569 !important;
        margin-bottom: 1.5rem;
    }

    .section-header {
        color: #0f172a !important;
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.9rem;
    }

    .section-divider {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 1.8rem 0;
    }

    .insight-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }

    .insight-title {
        color: #0f172a;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .insight-text {
        color: #475569;
        font-size: 14px;
    }

    .data-quality-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 18px;
        text-align: center;
    }

    .data-quality-value {
        font-size: 22px;
        font-weight: 700;
        color: #0f172a;
    }

    .data-quality-label {
        font-size: 12px;
        color: #64748b;
        margin-top: 4px;
    }

    section[data-testid="stSidebar"] {
        background-color: #0b0e14;
        border-right: 1px solid #1e2530;
    }

    section[data-testid="stSidebar"] h3 {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] a,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] div {
        color: #cbd5e1 !important;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] small {
        color: #cbd5e1 !important;
        opacity: 1 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    file_path = "data/processed/hourly_energy.csv"

    df = pd.read_csv(file_path)

    # Convert dates
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    if "date" in df.columns:
        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    # Remove invalid timestamps
    if "timestamp" in df.columns:
        df = df.dropna(subset=["timestamp"])

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "Energy dataset not found. Please check that "
        "'data/processed/hourly_energy.csv' exists."
    )
    st.stop()

except Exception as e:
    st.error(f"Unable to load the dataset: {e}")
    st.stop()


# ============================================================
# CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "timestamp",
    "date",
    "hour",
    "Global_active_power"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing from the dataset:"
    )

    st.write(missing_columns)

    st.stop()


# ============================================================
# CREATE DATE-RELATED COLUMNS IF NECESSARY
# ============================================================

if "hour" not in df.columns:
    df["hour"] = df["timestamp"].dt.hour

if "month" not in df.columns:
    df["month"] = df["timestamp"].dt.month

if "is_weekend" not in df.columns:
    df["is_weekend"] = (
        df["timestamp"].dt.dayofweek >= 5
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="hero-title">📊 Consumption Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="hero-subtitle">'
    'Deep-dive into energy consumption patterns across time and categories'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("### ⚡ Energy Assistant")
st.sidebar.caption("Analyze energy usage with interactive filters and visual analytics.")
st.sidebar.markdown("---")


# ============================================================
# FILTERS
# ============================================================

col1, col2, col3 = st.columns(3)


# ---------------- DATE FILTER ----------------

with col1:

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )


# ---------------- DAY TYPE ----------------

with col2:

    day_type_filter = st.selectbox(
        "Day Type",
        options=[
            "All",
            "Weekday",
            "Weekend"
        ]
    )


# ---------------- HOUR RANGE ----------------

with col3:

    hour_range = st.slider(
        "Hour Range",
        min_value=0,
        max_value=23,
        value=(0, 23)
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()


# Date filter
if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["date"] >= start_date)
        &
        (filtered_df["date"] <= end_date)
    ]


# Day type filter
if day_type_filter == "Weekday":

    filtered_df = filtered_df[
        filtered_df["is_weekend"] == False
    ]

elif day_type_filter == "Weekend":

    filtered_df = filtered_df[
        filtered_df["is_weekend"] == True
    ]


# Hour filter
filtered_df = filtered_df[
    (filtered_df["hour"] >= hour_range[0])
    &
    (filtered_df["hour"] <= hour_range[1])
]


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_df.empty:

    st.warning(
        "No data is available for the selected filters. "
        "Please choose a wider date or hour range."
    )

    st.stop()


# ============================================================
# FILTER SUMMARY
# ============================================================

st.markdown(
    f"**{len(filtered_df):,} hours** match your current filters."
)

st.markdown(
    '<hr class="section-divider">',
    unsafe_allow_html=True
)


# ============================================================
# CHART TEMPLATE
# ============================================================

chart_template = dict(
    template="plotly_white",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Inter",
        color="#475569",
        size=12
    ),
    margin=dict(
        l=10,
        r=10,
        t=10,
        b=10
    )
)


# ============================================================
# DAILY CONSUMPTION TREND
# ============================================================

st.markdown(
    '<div class="section-header">'
    '📅 Daily Consumption Trend'
    '</div>',
    unsafe_allow_html=True
)

daily = (
    filtered_df
    .groupby("date")["Global_active_power"]
    .mean()
    .reset_index()
)

daily.columns = [
    "date",
    "average_power"
]


fig = px.line(
    daily,
    x="date",
    y="average_power",
    labels={
        "date": "",
        "average_power": "Average Power"
    }
)

fig.update_traces(
    line_width=2
)

fig.update_layout(
    **chart_template,
    height=330
)

fig.update_xaxes(
    showgrid=False
)

fig.update_yaxes(
    showgrid=True,
    gridcolor="#e2e8f0"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# HOURLY + MONTHLY PATTERN
# ============================================================

st.markdown(
    '<hr class="section-divider">',
    unsafe_allow_html=True
)

col_a, col_b = st.columns(2)


# ------------------------------------------------------------
# HOURLY PATTERN
# ------------------------------------------------------------

with col_a:

    st.markdown(
        '<div class="section-header">'
        '🕐 Average Usage by Hour'
        '</div>',
        unsafe_allow_html=True
    )

    hourly = (
        filtered_df
        .groupby("hour")["Global_active_power"]
        .mean()
        .reset_index()
    )

    hourly.columns = [
        "hour",
        "average_power"
    ]

    fig = px.bar(
        hourly,
        x="hour",
        y="average_power",
        labels={
            "hour": "Hour of Day",
            "average_power": "Average Power"
        }
    )

    fig.update_layout(
        **chart_template,
        height=300
    )

    fig.update_xaxes(
        dtick=1,
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ------------------------------------------------------------
# MONTHLY PATTERN
# ------------------------------------------------------------

with col_b:

    st.markdown(
        '<div class="section-header">'
        '📆 Average Usage by Month'
        '</div>',
        unsafe_allow_html=True
    )

    monthly = (
        filtered_df
        .groupby("month")["Global_active_power"]
        .mean()
        .reset_index()
    )

    monthly.columns = [
        "month",
        "average_power"
    ]

    fig = px.bar(
        monthly,
        x="month",
        y="average_power",
        labels={
            "month": "Month",
            "average_power": "Average Power"
        }
    )

    fig.update_layout(
        **chart_template,
        height=300
    )

    fig.update_xaxes(
        dtick=1,
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# SUB-METER ANALYSIS
# ============================================================

submeter_columns = [
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3"
]

available_submeters = [
    col for col in submeter_columns
    if col in filtered_df.columns
]


if available_submeters:

    st.markdown(
        '<hr class="section-divider">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-header">'
        '🔌 Sub-meter Consumption Over Time'
        '</div>',
        unsafe_allow_html=True
    )

    category_daily = (
        filtered_df
        .groupby("date")[available_submeters]
        .sum()
        .reset_index()
    )

    category_daily.columns = ["date", "Kitchen", "Laundry", "Water Heater/AC"]

    category_melted = category_daily.melt(
        id_vars="date",
        var_name="Category",
        value_name="Consumption"
    )
    

    fig = px.line(
        category_melted,
        x="date",
        y="Consumption",
        color="Category"
    )

    fig.update_layout(
        **chart_template,
        height=340,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# AUTOMATIC KEY INSIGHTS
# ============================================================

st.markdown(
    '<hr class="section-divider">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-header">'
    '📌 Key Insights'
    '</div>',
    unsafe_allow_html=True
)


# Highest consumption hour
hour_summary = (
    filtered_df
    .groupby("hour")["Global_active_power"]
    .mean()
)

peak_hour = hour_summary.idxmax()
peak_value = hour_summary.max()


# Lowest consumption hour
lowest_hour = hour_summary.idxmin()
lowest_value = hour_summary.min()


# Weekday/weekend comparison
weekday_data = filtered_df[
    filtered_df["is_weekend"] == False
]["Global_active_power"].mean()

weekend_data = filtered_df[
    filtered_df["is_weekend"] == True
]["Global_active_power"].mean()


# Monthly maximum
month_summary = (
    filtered_df
    .groupby("month")["Global_active_power"]
    .mean()
)

highest_month = month_summary.idxmax()


insight_col1, insight_col2 = st.columns(2)


with insight_col1:

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                🕐 Peak Usage Period
            </div>
            <div class="insight-text">
                The highest average usage occurs around
                <b>{peak_hour}:00</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                📉 Lowest Usage Period
            </div>
            <div class="insight-text">
                The lowest average usage occurs around
                <b>{lowest_hour}:00</b>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with insight_col2:

    if pd.notna(weekday_data) and pd.notna(weekend_data):

        if weekend_data > weekday_data:

            day_message = (
                "Weekend usage is higher than weekday usage."
            )

        else:

            day_message = (
                "Weekday usage is higher than weekend usage."
            )

    else:

        day_message = (
            "There is not enough data to compare weekday "
            "and weekend usage."
        )


    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                📅 Day-Type Pattern
            </div>
            <div class="insight-text">
                {day_message}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="insight-card">
            <div class="insight-title">
                📆 Highest-Usage Month
            </div>
            <div class="insight-text">
                Month <b>{highest_month}</b> has the highest
                average usage in the selected data.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DATA QUALITY
# ============================================================

st.markdown(
    '<hr class="section-divider">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-header">'
    '🔎 Data Quality Overview'
    '</div>',
    unsafe_allow_html=True
)


missing_values = int(
    filtered_df.isna().sum().sum()
)

duplicate_rows = int(
    filtered_df.duplicated().sum()
)

records = len(filtered_df)


quality_col1, quality_col2, quality_col3 = st.columns(3)


with quality_col1:

    st.markdown(
        f"""
        <div class="data-quality-card">
            <div class="data-quality-value">
                {records:,}
            </div>
            <div class="data-quality-label">
                Records Analyzed
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with quality_col2:

    st.markdown(
        f"""
        <div class="data-quality-card">
            <div class="data-quality-value">
                {missing_values:,}
            </div>
            <div class="data-quality-label">
                Missing Values
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with quality_col3:

    st.markdown(
        f"""
        <div class="data-quality-card">
            <div class="data-quality-value">
                {duplicate_rows:,}
            </div>
            <div class="data-quality-label">
                Duplicate Rows
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DOWNLOAD FILTERED DATA
# ============================================================

st.markdown(
    '<hr class="section-divider">',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-header">'
    '📥 Export Analysis'
    '</div>',
    unsafe_allow_html=True
)


csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv_data,
    file_name="filtered_energy_data.csv",
    mime="text/csv"
)


# ============================================================
# SIDEBAR FOOTER
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("**About this analysis**")
st.sidebar.markdown("""
- Identifies temporal usage patterns
- Supports energy-efficiency decisions
- AI suggestions are decision-support only, not guaranteed savings
""")
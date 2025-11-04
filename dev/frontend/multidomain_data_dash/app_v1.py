import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

# Remove whitespace from the top of the page and sidebar
st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------- Data Generation -----------
@st.cache_data
def generate_data():
    date_range = pd.date_range(start="2024-01-01", end="2024-06-30")
    domains = {
        "finance": ["income", "spending", "savings", "investments", "net_worth"],
        "nutrition": ["calories", "protein", "fat", "carbs", "sugar"],
        "exercise": ["exercise_volume", "minutes_of_cardio", "sets_completed", "workout_duration", "avg_heart_rate"],
        "cooking": ["meals_cooked", "recipes_tried", "time_spent_cooking", "ingredients_used", "grocery_costs"]
    }

    records = []
    for domain, ch_list in domains.items():
        for channel in ch_list:
            values = np.random.normal(loc=100, scale=20, size=len(date_range))
            for date, value in zip(date_range, values):
                records.append({
                    "date": date,
                    "domain": domain,
                    "channel": channel,
                    "value": round(value, 2)
                })
    return pd.DataFrame(records), domains

df, domains = generate_data()

# ----------- UI Layout -----------
st.set_page_config(page_title="Central Dashboard", layout="wide", initial_sidebar_state="collapsed")

st.title("📊 Central Data Browser Dashboard")

# Sidebar controls
with st.sidebar:
    st.header("Chart Settings")
    grouping = st.radio("Group by", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"])
    chart_type = st.radio("Chart type", ["Line", "Bar", "Area"])

# column layout
col1, col2, col3 = st.columns([0.15,0.25,0.6])

# Date filter in main area
min_date = df["date"].min()
max_date = df["date"].max()
with col1:
    start_date, end_date = st.date_input("Select date range", [min_date, max_date])

# Domain and channel filters
with col2:
    selected_domains = st.multiselect("Select domain(s)", list(domains.keys()), default=list(domains.keys()))
available_channels = [c for d in selected_domains for c in domains[d]]

with col3:
    selected_channels = st.multiselect("Select channel(s)", available_channels, default=available_channels)

# ----------- Filtering Logic -----------
df_filtered = df[
    (df["domain"].isin(selected_domains)) &
    (df["channel"].isin(selected_channels)) &
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# Time grouping
if grouping == "Weekly":
    df_filtered["period"] = df_filtered["date"].dt.to_period("W").dt.start_time
elif grouping == "Monthly":
    df_filtered["period"] = df_filtered["date"].dt.to_period("M").dt.start_time
elif grouping == "Quarterly":
    df_filtered["period"] = df_filtered["date"].dt.to_period("Q").dt.start_time
elif grouping == "Yearly":
    df_filtered["period"] = df_filtered["date"].dt.to_period("Y").dt.start_time
else:
    df_filtered["period"] = df_filtered["date"]

agg_df = df_filtered.groupby(["period", "channel"]).agg({"value": "mean"}).reset_index()

# ----------- Chart Rendering -----------
if chart_type == "Line":
    chart = alt.Chart(agg_df).mark_line().encode(
        x="period:T", y="value:Q", color="channel:N", tooltip=["channel", "value", "period"]
    )
elif chart_type == "Bar":
    chart = alt.Chart(agg_df).mark_bar().encode(
        x="period:T", y="value:Q", color="channel:N", tooltip=["channel", "value", "period"]
    )
elif chart_type == "Area":
    chart = alt.Chart(agg_df).mark_area(opacity=0.6).encode(
        x="period:T", y="value:Q", color="channel:N", tooltip=["channel", "value", "period"]
    )

chart.properties(height=1200)
st.altair_chart(chart, use_container_width=True)
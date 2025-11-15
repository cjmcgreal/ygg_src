"""
Main Streamlit application entry point.
Epic Timeseries Visualization Tool

Run with: streamlit run app.py
"""

import streamlit as st
from src.timeseries.timeseries_app import render_timeseries

# Configure the page
st.set_page_config(
    page_title="Epic Timeseries Tool",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for extra slickness
st.markdown("""
<style>
    /* Make the app look more modern */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Style the main title */
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }

    /* Style buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }

    /* Style expanders */
    .streamlit-expanderHeader {
        background-color: #e9ecef;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Make metrics look better */
    [data-testid="stMetricValue"] {
        font-size: 24px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Render the main timeseries app
if __name__ == "__main__":
    render_timeseries()

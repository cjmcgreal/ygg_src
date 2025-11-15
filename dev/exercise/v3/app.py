"""
Main entry point for Exercise Tracker Streamlit application
"""

import streamlit as st
from src.exercise_app import render_exercise_app

st.set_page_config(
    page_title="Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

# Main app header
st.title("💪 Exercise Tracker")
st.write("Welcome to your personal workout tracking and progression system!")

st.markdown("""
## Features

- Intelligent progression logic (rep range and linear weight schemes)
- Automatic warmup set generation
- 1RM estimation and tracking
- Comprehensive workout history
- Metadata calculation (volume, calories, etc.)
- Backfill historical workouts
""")

st.write("---")

# Render the main exercise app
render_exercise_app()

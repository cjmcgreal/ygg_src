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

# Render the main exercise app
render_exercise_app()

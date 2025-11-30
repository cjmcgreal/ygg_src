"""
Social Media Post Selection Engine

A probabilistic post selection system with:
- Two-level hierarchy tree (topics -> subtopics)
- Recency penalties at both levels
- Effort filtering
- Post tracking and statistics

Run with: streamlit run app.py
"""

import streamlit as st

from src.selector.selector_app import render_selector


# Page configuration
st.set_page_config(
    page_title="Post Selection Engine",
    page_icon="📱",
    layout="wide"
)

# Render the main selector interface
render_selector()


if __name__ == "__main__":
    # This file is meant to be run with streamlit
    print("Run this app with: streamlit run app.py")

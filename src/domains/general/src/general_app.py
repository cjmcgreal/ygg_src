"""
General App - Main entry point with tab-based navigation
Cross-domain dashboard showing daily summaries from multiple domains
"""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import tab render functions
from exercise_tab import render_exercise_of_the_day


def render_general_app():
    """
    Main render function for the General dashboard.
    Contains tabs for daily summaries from each domain.
    """
    st.title("Daily Dashboard")

    # Create tabs for each domain
    tab_exercise, tab_placeholder = st.tabs([
        "💪 Exercise of the Day",
        "📊 More Coming Soon"
    ])

    with tab_exercise:
        render_exercise_of_the_day()

    with tab_placeholder:
        _render_placeholder()


def _render_placeholder():
    """Placeholder for future domain tabs"""
    st.header("More Features Coming Soon")
    st.info("""
    This dashboard will aggregate daily information from multiple domains:

    - **Finance Summary** - Daily spending overview
    - **Task Overview** - Today's tasks and priorities
    - **Travel Updates** - Upcoming trips

    For now, use the sidebar to navigate to individual domain pages.
    """)


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="General Dashboard",
        page_icon="🎯",
        layout="wide"
    )
    render_general_app()

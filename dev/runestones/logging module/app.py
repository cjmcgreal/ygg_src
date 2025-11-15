"""
Main Streamlit application for Runestones Framework Monitor.
This is the root app that aggregates all domain sections.
"""

import streamlit as st
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from runestones.runestones_app import render_runestones

# Configure the Streamlit page
st.set_page_config(
    page_title="Runestones Monitor",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Main application
def main():
    """
    Main application entry point.
    """
    # Render the runestones dashboard
    render_runestones()

    # Add footer
    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 20px;'>
            <small>Runestones Framework Monitor | Built with Streamlit</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

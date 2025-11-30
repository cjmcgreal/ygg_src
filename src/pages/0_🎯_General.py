"""
General Domain Page
Cross-domain dashboard - top of sidebar navigation
"""
import streamlit as st
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from domains.general.general_app import render_general_app

# Page configuration
st.set_page_config(
    page_title="Daily Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        /* Ensure tabs are visible and styled */
        .stTabs {
            margin-top: 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            padding-bottom: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding-top: 10px;
            padding-bottom: 10px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0px 0px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff;
        }
    </style>
    """, unsafe_allow_html=True)

# Render the general domain
render_general_app()

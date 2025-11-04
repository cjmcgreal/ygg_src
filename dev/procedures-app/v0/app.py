"""
Procedures Management App - Main Entry Point
A personal procedures management system for creating, executing, and analyzing repeatable task lists
"""

import streamlit as st
from src import workflow

# Page configuration
st.set_page_config(
    page_title="Procedures Management App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "browser"

if 'active_run_id' not in st.session_state:
    st.session_state.active_run_id = None

if 'edit_procedure_id' not in st.session_state:
    st.session_state.edit_procedure_id = None

# Sidebar navigation
with st.sidebar:
    st.title("📋 Procedures App")

    st.divider()

    # Navigation buttons
    if st.button("🏠 Browser", use_container_width=True):
        st.session_state.page = "browser"
        st.rerun()

    if st.button("▶️ Execute", use_container_width=True):
        st.session_state.page = "execute"
        st.rerun()

    if st.button("📜 History", use_container_width=True):
        st.session_state.page = "history"
        st.rerun()

    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.page = "analytics"
        st.rerun()

    st.divider()

    # Quick stats
    from src import analysis
    stats = analysis.get_overall_stats()

    st.metric("Total Procedures", stats['total_procedures'])
    st.metric("Total Runs", stats['total_runs'])
    st.metric("This Week", stats['runs_this_week'])

    st.divider()

    st.caption("💡 Tip: Create repeatable procedures to ensure consistency and track performance over time.")

    st.divider()

    st.caption("v0.1.0 - MVP")

# Main content area - route to appropriate page
current_page = st.session_state.page

if current_page == "browser":
    workflow.render_browser()
elif current_page == "execute":
    workflow.render_execution()
elif current_page == "history":
    workflow.render_history()
elif current_page == "analytics":
    workflow.render_analytics()
elif current_page == "editor":
    workflow.render_editor()
else:
    st.error(f"Unknown page: {current_page}")
    st.session_state.page = "browser"
    st.rerun()

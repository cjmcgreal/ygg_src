"""
Main Streamlit Application - Domain Aggregator

This is the root app.py that brings together all domain subapps.
Each domain has its own folder under domains/ with a render_{domain}_app() function.

Navigation: Sidebar for domain selection, tabs within each domain for sub-sections.
"""
import streamlit as st

# Import domain render functions
from domains.trees.trees_app import render_trees_app
from domains.exercise.exercise_app import render_exercise_app
from domains.finance.finance_app import render_finance_app
from domains.task_management.task_management_app import render_task_management_app
from domains.travel.travel_app import render_travel_app

# Page configuration
st.set_page_config(
    page_title="Personal Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        section[data-testid="stSidebar"] {
            width: 250px !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")

    # Domain selection
    selected_domain = st.radio(
        "Select Domain",
        options=["Trees", "Exercise", "Finance", "Task Manager", "Travel"],
        index=0
    )

    st.divider()
    st.caption("Each domain can have its own tabs and navigation")

# Main app title
st.title("Personal Dashboard")

# Render the selected domain
if selected_domain == "Trees":
    render_trees_app()
elif selected_domain == "Exercise":
    render_exercise_app()
elif selected_domain == "Finance":
    render_finance_app()
elif selected_domain == "Task Manager":
    render_task_management_app()
elif selected_domain == "Travel":
    render_travel_app()


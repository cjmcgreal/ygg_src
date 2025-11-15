"""
Main Streamlit Application - Home Page

This is the root app.py that serves as the home page.
Domain-specific functionality is in separate pages in the pages/ folder.

Navigation: Streamlit pages in sidebar, tabs within each domain for sub-sections.
"""
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Personal Dashboard - Home",
    page_icon="🏠",
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
    </style>
    """, unsafe_allow_html=True)

# Home page content
st.title("🏠 Personal Dashboard")

st.write("Welcome to your personal dashboard!")

st.markdown("""
## Available Domains

Use the sidebar to navigate between different domains:

- **🌳 Trees** - Tree visualization and management
- **💪 Exercise** - Exercise tracking and workout planning
- **💰 Finance** - Financial tracking and analysis
- **✅ Task Manager** - Task management and productivity
- **✈️ Travel** - Travel planning and tracking

## Getting Started

Click on any domain in the sidebar to get started!

Each domain has its own features and functionality, with tabs for organizing different sections within that domain.
""")


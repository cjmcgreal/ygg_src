"""
Exercise domain Streamlit UI component.

Demonstrates domain-level tabs for organizing sub-sections within the domain.
"""
import streamlit as st
from domains.exercise.exercise_workflow import display_exercise_data


def render_exercise_app():
    """
    Render the Exercise domain UI.

    This is the main entry point for the Exercise domain,
    called by the root app.py to display this domain's page.

    Demonstrates using tabs within a domain for sub-navigation.
    """
    st.header("Exercise Tracker")

    # Create tabs within the Exercise domain
    tab_overview, tab_data, tab_analytics = st.tabs([
        "Overview",
        "Exercise Data",
        "Analytics"
    ])

    with tab_overview:
        st.subheader("Welcome to Exercise Tracker")
        st.write("Track your exercises, view your progress, and analyze your performance.")

        st.info("📊 This domain demonstrates using tabs within a domain for organizing content.")

        # Quick stats
        st.write("**Quick Links:**")
        st.write("- View your exercise log in the 'Exercise Data' tab")
        st.write("- See analytics and trends in the 'Analytics' tab")

    with tab_data:
        st.subheader("Your Exercise Log")
        # Get and display exercise data
        display_exercise_data()

    with tab_analytics:
        st.subheader("Analytics & Insights")
        st.write("Analytics functionality coming soon...")
        st.info("This tab could show charts, trends, and insights from your exercise data.")


if __name__ == "__main__":
    # Standalone test - allows running this file directly
    print("Exercise App - Standalone Test")
    print("=" * 50)
    print("This module contains render_exercise_app() function")
    print("Run the main app.py to see the full UI")
    print("\nTo test: streamlit run app.py")

"""
Finance domain Streamlit UI component.
"""
import streamlit as st


def render_finance_app():
    """
    Render the Finance domain UI.

    This is the main entry point for the Finance domain,
    called by the root app.py to display this domain's page.
    """
    st.header("Finance Tracker")
    st.write("Finance tracking functionality coming soon...")
    st.info("This is a template domain. Implement finance_workflow, finance_logic, finance_analysis, and finance_db as needed.")


if __name__ == "__main__":
    # Standalone test
    print("Finance App - Standalone Test")
    print("=" * 50)
    print("This module contains render_finance_app() function")
    print("Run the main app.py to see the full UI")

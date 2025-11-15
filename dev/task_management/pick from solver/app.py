"""
Task Selection Algorithm Prototype - Main Entry Point

This is the main Streamlit application file that serves as the entry point
for the task selection algorithm prototype. It imports and calls the main
domain render function from the task_selection module.

The application provides a UI for:
- Managing a backlog of tasks with effort, value, and priority
- Defining bandwidth allocation and domain preferences
- Running optimization algorithms (greedy, weighted, knapsack)
- Viewing detailed explanations of algorithm decisions
- Tracking historical solver runs for comparison

To run this application:
    streamlit run app.py
"""

import streamlit as st

# Configure the Streamlit page
st.set_page_config(
    page_title="Task Selection Algorithm",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import the main domain render function
from src.task_selection.task_selection_app import render_task_selection

# Call the main render function
render_task_selection()

if __name__ == "__main__":
    # This allows the file to be run directly with: streamlit run app.py
    # The Streamlit framework will execute the code above
    pass

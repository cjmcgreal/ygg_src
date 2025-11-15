"""
Exercise workflow - API interface layer.
Orchestrates calls between UI, logic, analysis, and database.
"""
import streamlit as st
from domains.exercise.exercise_db import load_exercise_data
from domains.exercise.exercise_analysis import get_exercise_summary


def display_exercise_data():
    """
    Workflow function to display exercise data.
    Called when user views the exercise tab.
    """
    # Load data from database
    exercise_df = load_exercise_data()

    if exercise_df is not None and not exercise_df.empty:
        # Get analysis summary
        summary = get_exercise_summary(exercise_df)

        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Exercises", summary.get('total', 0))
        with col2:
            st.metric("Avg Value", f"{summary.get('average', 0):.1f}")
        with col3:
            st.metric("Max Value", summary.get('max', 0))

        # Display raw data
        st.subheader("Exercise Data")
        st.dataframe(exercise_df)
    else:
        st.info("No exercise data available. Add data to exercise_data/exercises.csv")


if __name__ == "__main__":
    # Standalone test
    print("Exercise Workflow - Standalone Test")
    print("=" * 50)
    print("Testing display_exercise_data workflow...")
    print("\nThis would orchestrate:")
    print("1. Load data from exercise_db")
    print("2. Analyze data using exercise_analysis")
    print("3. Display results in UI")

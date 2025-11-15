import streamlit as st
from exercise_workflow import get_next_workout, save_workout
from exercise_logic import generate_workout

st.set_page_config(page_title="Exercise Tracker", layout="wide")

tab1, tab2 = st.tabs(["Next Workout", "Workout Planner"])

with tab1:
    st.header("Next Workout")
    workout = get_next_workout()
    if workout is not None:
        st.dataframe(workout)
    else:
        st.info("No workout planned yet.")

with tab2:
    st.header("Plan a New Workout")
    if st.button("Generate New Workout"):
        new_workout = generate_workout()
        st.dataframe(new_workout)
        save = st.button("Save This Workout")
        if save:
            save_workout(new_workout)
            st.success("Workout saved!")

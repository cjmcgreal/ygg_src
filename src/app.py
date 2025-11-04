from domains.exercise.exercise_app import render_exercise_tab
from domains.task_management.task_man_app import render_task_man_tab
from domains.travel.travel_app import render_travel_tab
from app_cfg import (
    exercise_csv_path, 
    exercise_completed_csv_path,
    task_man_csv_path ,
    travel_csv_path
)

import streamlit as st

# Remove whitespace from the top of the page and sidebar
st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed")
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
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)


tab0, tab1, tab2, tab3, tab4 = st.tabs(["Trees","Exercise","Finance","Task Manager","Travel"])

with tab0:
    st.header("Content for Tree Tab")

with tab1:
    render_exercise_tab(
        csv_path=exercise_csv_path,
        completed_csv_path=exercise_completed_csv_path
        )

with tab2:
    st.header("Content for Finance Tab")
    st.dataframe({"col1": [1, 2], "col2": [3, 4]})

with tab3:
    render_task_man_tab(task_man_csv_path)

with tab4:
    render_travel_tab(travel_csv_path)


# with tab4:
#    st.header("Content for Tab C")


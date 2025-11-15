import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

def render_exercise_tab(
        csv_path: Path="my_steps.csv", 
        completed_csv_path: Path="completed_steps.csv"
        ):

    tab1, tab2, tab3 = st.tabs(["Next Workout","Workout Planner","demo"])

    with tab1:
        st.header("Content for Next Workout Tab")

    with tab2:
        st.header("Content for Workout Planner Tab")

    with tab3:

        # Load steps from CSV
        steps_df = pd.read_csv(csv_path)

        # Initialize session state
        if "completed_steps" not in st.session_state:
            st.session_state.completed_steps = set()
        if "step_timestamps" not in st.session_state:
            st.session_state.step_timestamps = {}

        st.title("Step Checklist")

        # Display checkboxes
        for idx, row in steps_df.iterrows():
            step_id = f"step_{idx}"
            label = row["step"] if "step" in row else str(row)

            checked = st.checkbox(label, key=step_id)

            # If newly checked, record timestamp
            if checked and idx not in st.session_state.completed_steps:
                st.session_state.completed_steps.add(idx)
                st.session_state.step_timestamps[idx] = datetime.now().isoformat()
            elif not checked and idx in st.session_state.completed_steps:
                # Allow unchecking (optional)
                st.session_state.completed_steps.remove(idx)
                st.session_state.step_timestamps.pop(idx, None)

        st.write(f"✅ {len(st.session_state.completed_steps)} of {len(steps_df)} steps completed")

        # Save button
        if st.button("Save Completed Steps"):
            completed_idxs = list(st.session_state.completed_steps)
            completed_df = steps_df.loc[completed_idxs].copy()
            completed_df["timestamp"] = completed_df.index.map(
                lambda i: st.session_state.step_timestamps.get(i, "")
            )
            completed_df.to_csv(completed_csv_path, index=False)
            st.success(f"Saved {len(completed_df)} completed steps with timestamps to {completed_csv_path}")

if __name__ == "__main__":
    render_exercise_tab()




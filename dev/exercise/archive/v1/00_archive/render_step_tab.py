import streamlit as st
import pandas as pd
from pathlib import Path

def render_step_tab(csv_path: Path, completed_csv_path: Path):
    # Load steps from CSV
    steps_df = pd.read_csv(csv_path)

    # Initialize session state for completed steps
    if "completed_steps" not in st.session_state:
        st.session_state.completed_steps = set()

    st.title("Step Checklist")

    # Display checkboxes
    for idx, row in steps_df.iterrows():
        step_id = f"step_{idx}"
        label = row["step"] if "step" in row else str(row)

        checked = st.checkbox(label, key=step_id)
        if checked:
            st.session_state.completed_steps.add(idx)
        else:
            st.session_state.completed_steps.discard(idx)

    st.write(f"✅ {len(st.session_state.completed_steps)} of {len(steps_df)} steps completed")

    # Export completed steps
    if st.button("Save Completed Steps"):
        completed_df = steps_df.loc[list(st.session_state.completed_steps)]
        completed_df.to_csv(completed_csv_path, index=False)
        st.success(f"Saved {len(completed_df)} completed steps to {completed_csv_path}")

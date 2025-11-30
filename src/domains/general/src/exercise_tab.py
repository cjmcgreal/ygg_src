"""
Exercise of the Day Tab
Displays the current workout from cycle with checkboxes and export functionality
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add exercise domain to path
domains_dir = Path(__file__).parent.parent.parent
exercise_dir = domains_dir / 'exercise'
exercise_src_dir = exercise_dir / 'src'
if str(exercise_dir) not in sys.path:
    sys.path.insert(0, str(exercise_dir))
if str(exercise_src_dir) not in sys.path:
    sys.path.insert(0, str(exercise_src_dir))

import db as exercise_db
import workflow as exercise_workflow
from logic import get_intensity_label
from markdown_utils import calculate_plate_load


def render_exercise_of_the_day():
    """
    Render the Exercise of the Day tab

    Shows:
    - Current workout from cycle
    - Workout details with checkboxes
    - Export to markdown button
    - Advance to next workout button
    """
    st.header("Exercise of the Day")

    # Get current workout from cycle
    current_workout = exercise_workflow.get_next_workout()

    if not current_workout:
        st.warning("No workouts configured yet!")
        st.info("""
        To get started:
        1. Go to **Exercise** page in the sidebar
        2. Create some exercises in the **Exercise Library** tab
        3. Create workout templates in the **Templates** tab
        4. Configure the cycle in **Cycle Config** tab
        """)
        return

    # Display workout header
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader(f"Workout {current_workout['label']}: {current_workout['name']}")
        if current_workout.get('notes'):
            st.caption(current_workout['notes'])

    with col2:
        # Cycle info
        cycle_state = exercise_db.get_cycle_state()
        active_labels = cycle_state.get('active_labels', '')
        if active_labels:
            labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]
            current_idx = cycle_state.get('current_index', 0)
            st.caption(f"Position {current_idx + 1} of {len(labels_list)}")

    st.divider()

    # Display each slot/exercise
    slots = current_workout.get('slots', [])

    if not slots:
        st.info("This template has no slots defined. Edit it in the Templates tab.")
        return

    for slot in slots:
        _render_exercise_slot(slot)
        st.divider()

    # Action buttons
    st.subheader("Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📤 Export to Markdown", type="primary"):
            try:
                filepath = exercise_workflow.export_workout_to_file(current_workout['id'])
                st.success(f"Exported to: {filepath}")

                # Also show the markdown content
                markdown = exercise_workflow.generate_workout_markdown(current_workout['id'])
                with st.expander("View Markdown"):
                    st.code(markdown, language="markdown")

            except Exception as e:
                st.error(f"Export failed: {str(e)}")

    with col2:
        if st.button("⏭️ Advance to Next"):
            exercise_workflow.advance_to_next_workout()
            st.success("Advanced to next workout!")
            st.rerun()

    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()


def _render_exercise_slot(slot: dict):
    """Render a single exercise slot with checkboxes"""
    muscle_group = slot.get('muscle_group', 'Unknown')
    intensity = slot.get('intensity', 'hypertrophy')
    num_sets = slot.get('sets', 3)

    # Check if exercise is assigned
    exercise = slot.get('exercise')
    generated_sets = slot.get('generated_sets', [])

    if not exercise:
        # No exercise assigned - show placeholder
        st.markdown(f"**{muscle_group.title()}** - {get_intensity_label(intensity)}")
        st.warning("No exercise assigned to this slot")
        st.caption("Assign an exercise in the Templates tab")
        return

    # Exercise header
    st.markdown(f"**{muscle_group.title()} - {exercise['name']}**")

    # Show intensity and goals
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption(f"Intensity: {get_intensity_label(intensity)}")

    with col2:
        working_sets = [s for s in generated_sets if s['set_type'] == 'working']
        if working_sets:
            first = working_sets[0]
            st.caption(f"Goal: {len(working_sets)} x {first['target_reps']} x {first['target_weight']:.0f} lb")

    with col3:
        last_perf = slot.get('last_performance')
        if last_perf:
            st.caption(f"Last: {last_perf.get('last_reps', '?')} x {last_perf.get('last_weight', '?')} lb")

    # Render sets with checkboxes
    if generated_sets:
        for set_info in generated_sets:
            _render_set_checkbox(exercise['name'], set_info)
    else:
        st.info("No sets generated. Check exercise configuration.")


def _render_set_checkbox(exercise_name: str, set_info: dict):
    """Render a single set as a checkbox"""
    set_type = set_info.get('set_type', 'working')
    set_number = set_info.get('set_number', 1)
    target_weight = set_info.get('target_weight', 0)
    target_reps = set_info.get('target_reps', 0)
    rest_seconds = set_info.get('rest_seconds', 0)

    # Format label
    if set_type == 'warmup':
        label = f"Warmup {set_number}"
        icon = "🔥"
    else:
        label = f"Set {set_number}"
        icon = "💪"

    # Calculate plate load
    try:
        plate_load = calculate_plate_load(target_weight)
    except:
        plate_load = ""

    # Create checkbox key
    checkbox_key = f"set_{exercise_name}_{set_type}_{set_number}"

    # Render
    col1, col2 = st.columns([3, 1])

    with col1:
        checked = st.checkbox(
            f"{icon} {label}: {target_reps} x {target_weight:.0f} lb ({plate_load})",
            key=checkbox_key,
            help=f"Rest: {rest_seconds}s"
        )

    with col2:
        if set_type == 'working':
            st.caption(f"Rest: {rest_seconds//60}:{rest_seconds%60:02d}")


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Exercise Tab Test", layout="wide")
    render_exercise_of_the_day()

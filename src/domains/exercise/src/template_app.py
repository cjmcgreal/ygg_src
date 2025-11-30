"""
Template Management UI Component
Streamlit UI for creating and managing slot-based workout templates
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import db
import workflow
from logic import get_intensity_label, INTENSITY_RANGES


# Available muscle groups for template slots
MUSCLE_GROUPS = [
    'chest', 'back', 'shoulders', 'biceps', 'triceps',
    'quadriceps', 'hamstrings', 'glutes', 'calves',
    'core', 'forearms', 'lumbar'
]

# Intensity options
INTENSITY_OPTIONS = ['strength', 'hypertrophy', 'endurance']


def render_template_manager():
    """
    Render the template management tab

    Allows users to:
    - View existing templates
    - Create new templates with slot definitions
    - Edit existing templates
    - Delete templates
    - Assign exercises to template slots
    """
    st.header("Workout Templates")
    st.caption("Define workout templates with muscle group + intensity slots")

    # Create two columns: template list and editor
    col_list, col_editor = st.columns([1, 2])

    with col_list:
        _render_template_list()

    with col_editor:
        _render_template_editor()


def _render_template_list():
    """Render the list of existing templates"""
    st.subheader("Your Templates")

    templates_df = db.get_all_workout_templates()

    if templates_df.empty:
        st.info("No templates yet. Create one to get started!")
        if st.button("➕ Create First Template", key="create_first"):
            st.session_state['editing_template_id'] = None
            st.session_state['template_mode'] = 'create'
            st.rerun()
        return

    # Display each template as a card
    for _, template in templates_df.iterrows():
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{template['label']}** - {template['name']}")

                # Parse and show slot summary
                import json
                try:
                    slots = json.loads(template['slot_definitions']) if template['slot_definitions'] else []
                    slot_summary = ', '.join([
                        f"{s.get('muscle_group', '?')} ({s.get('intensity', '?')[:3]})"
                        for s in slots[:3]
                    ])
                    if len(slots) > 3:
                        slot_summary += f" +{len(slots)-3} more"
                    st.caption(slot_summary)
                except:
                    st.caption("No slots defined")

            with col2:
                if st.button("Edit", key=f"edit_{template['id']}"):
                    st.session_state['editing_template_id'] = template['id']
                    st.session_state['template_mode'] = 'edit'
                    st.rerun()

            st.divider()

    # Create new template button
    if st.button("➕ New Template", key="create_new"):
        st.session_state['editing_template_id'] = None
        st.session_state['template_mode'] = 'create'
        st.rerun()


def _render_template_editor():
    """Render the template editor form"""
    mode = st.session_state.get('template_mode', None)
    template_id = st.session_state.get('editing_template_id')

    if not mode:
        st.info("Select a template to edit or create a new one")
        return

    if mode == 'edit' and template_id:
        st.subheader("Edit Template")
        template = db.get_workout_template_by_id(template_id)
        if not template:
            st.error("Template not found")
            return
    else:
        st.subheader("Create New Template")
        template = {
            'name': '',
            'label': '',
            'slot_definitions': [],
            'notes': ''
        }

    # Template basic info
    col1, col2 = st.columns([3, 1])
    with col1:
        name = st.text_input("Template Name", value=template.get('name', ''),
                             placeholder="e.g., Push Day, Pull Day, Legs")
    with col2:
        label = st.text_input("Label", value=template.get('label', ''),
                              placeholder="A, B, C...", max_chars=1)

    notes = st.text_area("Notes (optional)", value=template.get('notes', ''),
                         placeholder="Any notes about this template...")

    # Slot definitions
    st.subheader("Slot Definitions")
    st.caption("Define what muscle groups and intensities this workout targets")

    # Initialize slots in session state if needed
    if 'template_slots' not in st.session_state or st.session_state.get('template_slots_id') != template_id:
        st.session_state['template_slots'] = template.get('slot_definitions', [])
        st.session_state['template_slots_id'] = template_id

    slots = st.session_state['template_slots']

    # Render each slot
    for i, slot in enumerate(slots):
        with st.container():
            cols = st.columns([2, 2, 1, 1])

            with cols[0]:
                muscle_group = st.selectbox(
                    f"Muscle Group",
                    options=MUSCLE_GROUPS,
                    index=MUSCLE_GROUPS.index(slot.get('muscle_group', 'chest'))
                        if slot.get('muscle_group') in MUSCLE_GROUPS else 0,
                    key=f"slot_muscle_{i}"
                )
                slots[i]['muscle_group'] = muscle_group

            with cols[1]:
                intensity = st.selectbox(
                    f"Intensity",
                    options=INTENSITY_OPTIONS,
                    index=INTENSITY_OPTIONS.index(slot.get('intensity', 'hypertrophy'))
                        if slot.get('intensity') in INTENSITY_OPTIONS else 1,
                    key=f"slot_intensity_{i}",
                    format_func=lambda x: get_intensity_label(x)
                )
                slots[i]['intensity'] = intensity

            with cols[2]:
                num_sets = st.number_input(
                    "Sets",
                    min_value=1, max_value=10,
                    value=slot.get('sets', 3),
                    key=f"slot_sets_{i}"
                )
                slots[i]['sets'] = num_sets

            with cols[3]:
                if st.button("🗑️", key=f"remove_slot_{i}"):
                    slots.pop(i)
                    st.rerun()

            # Show exercise assignment if in edit mode
            if mode == 'edit' and template_id:
                _render_exercise_selector(template_id, i + 1, slot.get('muscle_group', ''))

        st.divider()

    # Add slot button
    if st.button("➕ Add Slot"):
        slots.append({
            'muscle_group': 'chest',
            'intensity': 'hypertrophy',
            'sets': 3,
            'slot_order': len(slots) + 1
        })
        st.rerun()

    # Action buttons
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("💾 Save Template", type="primary"):
            try:
                # Add slot_order to each slot
                for i, slot in enumerate(slots):
                    slot['slot_order'] = i + 1

                if mode == 'create':
                    new_id = workflow.handle_create_template(
                        name=name,
                        label=label,
                        slot_definitions=slots,
                        notes=notes
                    )
                    st.success(f"Template '{name}' created!")
                    st.session_state['editing_template_id'] = new_id
                    st.session_state['template_mode'] = 'edit'
                else:
                    workflow.handle_update_template(
                        template_id=template_id,
                        name=name,
                        label=label,
                        slot_definitions=slots,
                        notes=notes
                    )
                    st.success("Template updated!")

                # Clear slot cache
                del st.session_state['template_slots']
                st.rerun()

            except ValueError as e:
                st.error(str(e))

    with col2:
        if st.button("❌ Cancel"):
            st.session_state['template_mode'] = None
            st.session_state['editing_template_id'] = None
            if 'template_slots' in st.session_state:
                del st.session_state['template_slots']
            st.rerun()

    with col3:
        if mode == 'edit' and template_id:
            if st.button("🗑️ Delete", type="secondary"):
                try:
                    workflow.handle_delete_template(template_id)
                    st.success("Template deleted!")
                    st.session_state['template_mode'] = None
                    st.session_state['editing_template_id'] = None
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))


def _render_exercise_selector(template_id: int, slot_order: int, muscle_group: str):
    """Render exercise selector for a template slot"""
    # Get current selection
    selections = db.get_selections_for_template(template_id)
    current_selection = next(
        (s['exercise_id'] for s in selections if s['slot_order'] == slot_order),
        None
    )

    # Get exercises matching muscle group
    matching_exercises = workflow.get_exercises_for_muscle_group(muscle_group)

    if not matching_exercises:
        st.caption(f"No exercises found for {muscle_group}")
        return

    # Build options
    exercise_options = {ex['id']: ex['name'] for ex in matching_exercises}
    options = [None] + list(exercise_options.keys())
    format_func = lambda x: "-- Select Exercise --" if x is None else exercise_options.get(x, "Unknown")

    # Current index
    current_idx = 0
    if current_selection and current_selection in options:
        current_idx = options.index(current_selection)

    # Selectbox
    selected = st.selectbox(
        "Assign Exercise",
        options=options,
        index=current_idx,
        format_func=format_func,
        key=f"ex_select_{template_id}_{slot_order}"
    )

    # Save selection if changed
    if selected and selected != current_selection:
        try:
            workflow.handle_select_exercise_for_slot(template_id, slot_order, selected)
            st.success("Exercise assigned!")
        except ValueError as e:
            st.error(str(e))


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Template Manager Test", layout="wide")
    render_template_manager()

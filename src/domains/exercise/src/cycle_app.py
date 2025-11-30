"""
Cycle Configuration UI Component
Streamlit UI for managing workout rotation/cycling
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


def render_cycle_config():
    """
    Render the cycle configuration tab

    Allows users to:
    - View current workout cycle state
    - Configure which workouts are active
    - Reorder workout rotation
    - Reset cycle position
    """
    st.header("Workout Cycle Configuration")
    st.caption("Configure how workouts rotate in your training cycle")

    # Get current state
    cycle_state = db.get_cycle_state()
    templates_df = db.get_all_workout_templates()

    if templates_df.empty:
        st.warning("No workout templates found. Create some templates first!")
        return

    # Current cycle info
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Cycle")

        active_labels = cycle_state.get('active_labels', '')
        current_index = cycle_state.get('current_index', 0)

        if active_labels:
            labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]

            # Show rotation with current highlighted
            st.markdown("**Rotation Order:**")
            for i, label in enumerate(labels_list):
                template = db.get_workout_template_by_label(label)
                name = template['name'] if template else "Unknown"

                if i == current_index:
                    st.markdown(f"➡️ **{label}** - {name} (CURRENT)")
                else:
                    st.markdown(f"   {label} - {name}")

            st.divider()

            # Current workout display
            current_label = labels_list[current_index] if current_index < len(labels_list) else None
            if current_label:
                current_template = db.get_workout_template_by_label(current_label)
                if current_template:
                    st.metric("Next Workout", f"{current_label} - {current_template['name']}")
        else:
            st.info("No workouts in cycle. Configure active workouts below.")

    with col2:
        st.subheader("Cycle Controls")

        # Advance button
        if active_labels and st.button("⏭️ Advance to Next Workout", type="primary"):
            new_state = db.advance_cycle()
            st.success(f"Advanced to workout {new_state.get('current_label', '?')}")
            st.rerun()

        # Reset button
        if st.button("🔄 Reset to First Workout"):
            db.update_cycle_state(current_index=0)
            st.success("Reset to first workout in cycle")
            st.rerun()

    st.divider()

    # Configure active workouts
    st.subheader("Configure Active Workouts")
    st.caption("Select which workouts to include in your rotation")

    # Get all available templates
    all_labels = templates_df['label'].tolist()
    all_names = templates_df['name'].tolist()
    template_options = {label: name for label, name in zip(all_labels, all_names)}

    # Current active labels
    current_active = [l.strip() for l in active_labels.split(',') if l.strip()]

    # Multiselect for active workouts
    selected_labels = st.multiselect(
        "Active Workouts",
        options=list(template_options.keys()),
        default=current_active,
        format_func=lambda x: f"{x} - {template_options.get(x, 'Unknown')}",
        help="Select workouts to include in rotation. Order matters - first selected = first in cycle"
    )

    # Reorder interface
    if selected_labels:
        st.markdown("**Rotation Order** (drag to reorder):")

        # Simple reorder with up/down buttons
        for i, label in enumerate(selected_labels):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.write(f"{i+1}. {label} - {template_options.get(label, '')}")

            with col2:
                if i > 0 and st.button("⬆️", key=f"up_{label}"):
                    selected_labels[i], selected_labels[i-1] = selected_labels[i-1], selected_labels[i]
                    st.rerun()

            with col3:
                if i < len(selected_labels) - 1 and st.button("⬇️", key=f"down_{label}"):
                    selected_labels[i], selected_labels[i+1] = selected_labels[i+1], selected_labels[i]
                    st.rerun()

    # Save button
    if st.button("💾 Save Cycle Configuration", type="primary"):
        try:
            workflow.configure_cycle(selected_labels)
            st.success("Cycle configuration saved!")
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    # Show cycle summary
    st.divider()
    st.subheader("Cycle Summary")

    if selected_labels:
        st.markdown(f"**Total workouts in cycle:** {len(selected_labels)}")
        st.markdown(f"**Rotation:** {' → '.join(selected_labels)} → (repeat)")
    else:
        st.warning("No workouts selected for cycle")


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Cycle Config Test", layout="wide")
    render_cycle_config()

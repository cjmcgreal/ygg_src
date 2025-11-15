"""
Exercise Library Page
Create and manage exercises with progression schemes and warmup configurations
"""

import streamlit as st
import pandas as pd
import json
import workflow
import db

# Page configuration
st.set_page_config(
    page_title="Exercise Library - Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("📚 Exercise Library")
st.write("Create and manage your exercise library")

# Predefined muscle groups
MUSCLE_GROUPS = [
    "Chest", "Back", "Shoulders", "Biceps", "Triceps", "Forearms",
    "Quadriceps", "Hamstrings", "Glutes", "Calves",
    "Core", "Abs", "Obliques"
]

# Default warmup configuration
DEFAULT_WARMUP_CONFIG = {
    "enabled": True,
    "intensity_thresholds": [
        {"min_percent_1rm": 0, "max_percent_1rm": 50, "warmup_sets": 1},
        {"min_percent_1rm": 50, "max_percent_1rm": 70, "warmup_sets": 2},
        {"min_percent_1rm": 70, "max_percent_1rm": 100, "warmup_sets": 3}
    ],
    "warmup_percentages": [40, 60, 80],
    "warmup_reps": [8, 6, 4]
}

# Two-column layout
col_form, col_library = st.columns([1, 1])

# ============================================================================
# LEFT COLUMN: Exercise Creation Form
# ============================================================================

with col_form:
    st.subheader("Create New Exercise")

    with st.form("exercise_form", clear_on_submit=True):
        # Exercise name (required)
        exercise_name = st.text_input(
            "Exercise Name *",
            placeholder="e.g., Barbell Back Squat",
            help="Enter the name of the exercise"
        )

        # Description (optional)
        description = st.text_area(
            "Description",
            placeholder="Optional exercise description or notes",
            help="Add any notes about the exercise"
        )

        # Primary muscle groups (required)
        primary_muscles = st.multiselect(
            "Primary Muscle Groups *",
            options=MUSCLE_GROUPS,
            help="Select at least one primary muscle group"
        )

        # Secondary muscle groups (optional)
        secondary_muscles = st.multiselect(
            "Secondary Muscle Groups",
            options=MUSCLE_GROUPS,
            help="Select any secondary muscle groups"
        )

        # Progression scheme
        progression_scheme = st.radio(
            "Progression Scheme *",
            options=["Rep Range", "Linear Weight"],
            help="Rep Range: Add reps until max, then add weight. Linear Weight: Add weight each workout."
        )

        # Conditional inputs based on progression scheme
        if progression_scheme == "Rep Range":
            col_min, col_max = st.columns(2)
            with col_min:
                rep_range_min = st.number_input(
                    "Min Reps",
                    min_value=1,
                    max_value=50,
                    value=8,
                    help="Minimum reps in the range"
                )
            with col_max:
                rep_range_max = st.number_input(
                    "Max Reps",
                    min_value=1,
                    max_value=50,
                    value=12,
                    help="Maximum reps in the range"
                )
            target_reps = None
        else:  # Linear Weight
            target_reps = st.number_input(
                "Target Reps",
                min_value=1,
                max_value=50,
                value=5,
                help="Fixed number of reps for each set"
            )
            rep_range_min = None
            rep_range_max = None

        # Weight increment
        weight_increment = st.number_input(
            "Weight Increment (lbs) *",
            min_value=0.5,
            max_value=50.0,
            value=5.0,
            step=0.5,
            help="Amount to increase weight on successful workout"
        )

        # Warmup sets toggle
        enable_warmup = st.checkbox(
            "Enable Warmup Sets",
            value=True,
            help="Generate warmup sets before working sets"
        )

        warmup_config = None
        if enable_warmup:
            with st.expander("Warmup Configuration (Optional - Advanced)"):
                st.write("Default warmup configuration:")
                st.json(DEFAULT_WARMUP_CONFIG)
                st.info(
                    "Default config generates 1-3 warmup sets based on working set intensity:\n"
                    "- Low intensity (0-50% 1RM): 1 warmup set\n"
                    "- Medium intensity (50-70% 1RM): 2 warmup sets\n"
                    "- High intensity (70-100% 1RM): 3 warmup sets"
                )
                # For MVP, use default config only
                warmup_config = json.dumps(DEFAULT_WARMUP_CONFIG)

        # Submit button
        submit_button = st.form_submit_button("Create Exercise", use_container_width=True)

        # Form submission handling
        if submit_button:
            # Validate required fields
            if not exercise_name.strip():
                st.error("Exercise name is required")
            elif not primary_muscles:
                st.error("At least one primary muscle group is required")
            elif progression_scheme == "Rep Range" and rep_range_min >= rep_range_max:
                st.error("Min reps must be less than max reps")
            else:
                # Build exercise data dictionary
                exercise_data = {
                    "name": exercise_name.strip(),
                    "description": description.strip(),
                    "primary_muscle_groups": ",".join([m.lower() for m in primary_muscles]),
                    "secondary_muscle_groups": ",".join([m.lower() for m in secondary_muscles]) if secondary_muscles else "",
                    "progression_scheme": "rep_range" if progression_scheme == "Rep Range" else "linear_weight",
                    "rep_range_min": rep_range_min,
                    "rep_range_max": rep_range_max,
                    "target_reps": target_reps,
                    "weight_increment": weight_increment,
                    "warmup_config": warmup_config
                }

                try:
                    # Call workflow to create exercise
                    exercise_id = workflow.handle_create_exercise(exercise_data)
                    st.success(f"✅ Exercise '{exercise_name}' created successfully (ID: {exercise_id})")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Validation error: {str(e)}")
                except Exception as e:
                    st.error(f"Error creating exercise: {str(e)}")

# ============================================================================
# RIGHT COLUMN: Exercise Library View
# ============================================================================

with col_library:
    st.subheader("Exercise Library")

    # Load all exercises
    exercises_df = db.get_all_exercises()

    if exercises_df.empty:
        st.info("No exercises yet. Create your first exercise using the form on the left!")
    else:
        # Search and filter controls
        col_search, col_filter = st.columns([2, 1])

        with col_search:
            search_term = st.text_input(
                "Search by name",
                placeholder="Type to search...",
                label_visibility="collapsed"
            )

        with col_filter:
            muscle_filter = st.multiselect(
                "Filter by muscle",
                options=MUSCLE_GROUPS,
                label_visibility="collapsed",
                placeholder="Filter by muscle group"
            )

        # Apply filters
        filtered_df = exercises_df.copy()

        # Search filter
        if search_term:
            filtered_df = filtered_df[
                filtered_df['name'].str.contains(search_term, case=False, na=False)
            ]

        # Muscle group filter
        if muscle_filter:
            muscle_filter_lower = [m.lower() for m in muscle_filter]
            filtered_df = filtered_df[
                filtered_df['primary_muscle_groups'].apply(
                    lambda x: any(muscle in str(x).lower() for muscle in muscle_filter_lower)
                )
            ]

        # Display count
        st.write(f"Showing {len(filtered_df)} of {len(exercises_df)} exercises")

        # Display exercises table
        if filtered_df.empty:
            st.warning("No exercises match your search criteria")
        else:
            # Prepare display dataframe
            display_df = filtered_df[[
                'name',
                'primary_muscle_groups',
                'progression_scheme',
                'weight_increment'
            ]].copy()

            # Format columns for display
            display_df['primary_muscle_groups'] = display_df['primary_muscle_groups'].apply(
                lambda x: x.replace(',', ', ').title() if pd.notna(x) else ''
            )
            display_df['progression_scheme'] = display_df['progression_scheme'].apply(
                lambda x: "Rep Range" if x == "rep_range" else "Linear Weight"
            )
            display_df['weight_increment'] = display_df['weight_increment'].apply(
                lambda x: f"{x} lbs"
            )

            # Rename columns for display
            display_df.columns = ['Name', 'Primary Muscles', 'Progression', 'Weight Increment']

            # Display as interactive dataframe
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                hide_index=True
            )

            # Exercise details expandable section
            st.write("---")
            st.write("**Exercise Details**")

            # Select exercise to view details
            exercise_names = filtered_df['name'].tolist()
            selected_exercise_name = st.selectbox(
                "Select exercise to view details",
                options=exercise_names,
                label_visibility="collapsed"
            )

            if selected_exercise_name:
                # Get exercise details
                exercise = filtered_df[filtered_df['name'] == selected_exercise_name].iloc[0]

                with st.expander(f"📋 {selected_exercise_name}", expanded=True):
                    # Basic info
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**ID:** {exercise['id']}")
                        st.write(f"**Progression:** {exercise['progression_scheme'].replace('_', ' ').title()}")

                        if exercise['progression_scheme'] == 'rep_range':
                            st.write(f"**Rep Range:** {int(exercise['rep_range_min'])} - {int(exercise['rep_range_max'])}")
                        else:
                            st.write(f"**Target Reps:** {int(exercise['target_reps'])}")

                    with col2:
                        st.write(f"**Weight Increment:** {exercise['weight_increment']} lbs")
                        st.write(f"**Created:** {exercise['created_at'].strftime('%Y-%m-%d') if pd.notna(exercise['created_at']) else 'N/A'}")

                    # Description
                    if pd.notna(exercise['description']) and exercise['description'].strip():
                        st.write("**Description:**")
                        st.write(exercise['description'])

                    # Muscle groups
                    st.write("**Primary Muscles:**")
                    st.write(exercise['primary_muscle_groups'].replace(',', ', ').title())

                    if pd.notna(exercise['secondary_muscle_groups']) and exercise['secondary_muscle_groups'].strip():
                        st.write("**Secondary Muscles:**")
                        st.write(exercise['secondary_muscle_groups'].replace(',', ', ').title())

                    # Warmup config
                    if pd.notna(exercise['warmup_config']) and exercise['warmup_config']:
                        st.write("**Warmup Configuration:**")
                        try:
                            warmup_data = json.loads(exercise['warmup_config'])
                            st.json(warmup_data)
                        except json.JSONDecodeError:
                            st.write("Enabled")
                    else:
                        st.write("**Warmup Sets:** Disabled")

# Footer
st.write("---")
st.caption("💡 Tip: Create exercises first, then build workouts using them on the 'Create Workout' page")

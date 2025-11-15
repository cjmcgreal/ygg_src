"""
Exercise App - Main entry point with all render functions
This module can be imported into other applications
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import workflow
import db
import analysis


# ============================================================================
# RENDER: EXERCISE LIBRARY
# ============================================================================

def render_exercise_library():
    """Render the Exercise Library page"""

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

    # ========================================================================
    # LEFT COLUMN: Exercise Creation Form
    # ========================================================================

    with col_form:
        st.subheader("Create New Exercise")

        # Display success message if exercise was just created
        if 'exercise_created_success' in st.session_state:
            st.success(f"✅ Exercise '{st.session_state['exercise_created_success']}' created successfully!")
            del st.session_state['exercise_created_success']

        # Progression scheme OUTSIDE form for dynamic updates
        progression_scheme = st.radio(
            "Progression Scheme *",
            options=["Rep Range", "Linear Weight", "Linear Reps"],
            help="Rep Range: Add reps until max, then add weight. Linear Weight: Add weight each workout. Linear Reps: Add reps each workout.",
            key="exercise_progression_scheme"
        )

        with st.form("exercise_form", clear_on_submit=False):
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
                rep_increment = None
                weight_increment = st.number_input(
                    "Weight Increment (lbs) *",
                    min_value=-50.0,
                    max_value=50.0,
                    value=5.0,
                    step=0.5,
                    help="Amount to change weight on successful workout (use negative for assisted exercises)"
                )
            elif progression_scheme == "Linear Weight":
                target_reps = st.number_input(
                    "Target Reps",
                    min_value=1,
                    max_value=50,
                    value=5,
                    help="Fixed number of reps for each set"
                )
                rep_range_min = None
                rep_range_max = None
                rep_increment = None
                weight_increment = st.number_input(
                    "Weight Increment (lbs) *",
                    min_value=-50.0,
                    max_value=50.0,
                    value=5.0,
                    step=0.5,
                    help="Amount to change weight on successful workout (use negative for assisted exercises)"
                )
            else:  # Linear Reps
                target_reps = st.number_input(
                    "Starting Reps",
                    min_value=1,
                    max_value=50,
                    value=5,
                    help="Starting number of reps for each set"
                )
                rep_range_min = None
                rep_range_max = None
                rep_increment = st.number_input(
                    "Rep Increment *",
                    min_value=1,
                    max_value=10,
                    value=1,
                    help="Number of reps to add each successful workout"
                )
                weight_increment = None

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
                    # Map UI progression scheme to database value
                    if progression_scheme == "Rep Range":
                        prog_scheme_db = "rep_range"
                    elif progression_scheme == "Linear Weight":
                        prog_scheme_db = "linear_weight"
                    else:  # Linear Reps
                        prog_scheme_db = "linear_reps"

                    # Build exercise data dictionary
                    exercise_data = {
                        "name": exercise_name.strip(),
                        "description": description.strip(),
                        "primary_muscle_groups": ",".join([m.lower() for m in primary_muscles]),
                        "secondary_muscle_groups": ",".join([m.lower() for m in secondary_muscles]) if secondary_muscles else "",
                        "progression_scheme": prog_scheme_db,
                        "rep_range_min": rep_range_min,
                        "rep_range_max": rep_range_max,
                        "target_reps": target_reps,
                        "rep_increment": rep_increment,
                        "weight_increment": weight_increment,
                        "warmup_config": warmup_config
                    }

                    try:
                        # Call workflow to create exercise
                        exercise_id = workflow.handle_create_exercise(exercise_data)
                        # Store success message in session state so it persists after rerun
                        st.session_state['exercise_created_success'] = exercise_name
                        st.rerun()
                    except ValueError as e:
                        st.error(f"Validation error: {str(e)}")
                    except Exception as e:
                        st.error(f"Error creating exercise: {str(e)}")

    # ========================================================================
    # RIGHT COLUMN: Exercise Library View
    # ========================================================================

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

                        # Edit button
                        st.write("---")
                        if st.button("✏️ Edit Exercise", key=f"edit_btn_{exercise['id']}", use_container_width=True):
                            st.session_state['editing_exercise_id'] = exercise['id']
                            st.rerun()

    # Edit Exercise Form
    if 'editing_exercise_id' in st.session_state:
        st.write("---")
        st.subheader("Edit Exercise")

        # Load exercise to edit
        exercise_to_edit = db.get_exercise_by_id(st.session_state['editing_exercise_id'])

        if exercise_to_edit:
            # Map database progression scheme to UI value
            if exercise_to_edit['progression_scheme'] == 'rep_range':
                prog_scheme_ui = "Rep Range"
            elif exercise_to_edit['progression_scheme'] == 'linear_weight':
                prog_scheme_ui = "Linear Weight"
            else:
                prog_scheme_ui = "Linear Reps"

            # Initialize progression scheme in session state if not set
            if 'edit_prog_scheme' not in st.session_state:
                st.session_state['edit_prog_scheme'] = prog_scheme_ui

            # Progression scheme selector outside form for dynamic updates
            edit_progression_scheme = st.radio(
                "Progression Scheme *",
                options=["Rep Range", "Linear Weight", "Linear Reps"],
                index=["Rep Range", "Linear Weight", "Linear Reps"].index(st.session_state['edit_prog_scheme']),
                help="Rep Range: Add reps until max, then add weight. Linear Weight: Add weight each workout. Linear Reps: Add reps each workout.",
                key="edit_exercise_progression_scheme"
            )

            # Update session state
            st.session_state['edit_prog_scheme'] = edit_progression_scheme

            with st.form("edit_exercise_form", clear_on_submit=False):
                # Exercise name
                edit_name = st.text_input(
                    "Exercise Name *",
                    value=exercise_to_edit['name'],
                    help="Enter the name of the exercise"
                )

                # Description
                edit_description = st.text_area(
                    "Description",
                    value=exercise_to_edit.get('description', ''),
                    help="Add any notes about the exercise"
                )

                # Primary muscles
                current_primary = [m.strip().title() for m in exercise_to_edit['primary_muscle_groups'].split(',') if m.strip()]
                edit_primary_muscles = st.multiselect(
                    "Primary Muscle Groups *",
                    options=MUSCLE_GROUPS,
                    default=current_primary,
                    help="Select at least one primary muscle group"
                )

                # Secondary muscles
                current_secondary = []
                if pd.notna(exercise_to_edit.get('secondary_muscle_groups')) and exercise_to_edit['secondary_muscle_groups']:
                    current_secondary = [m.strip().title() for m in exercise_to_edit['secondary_muscle_groups'].split(',') if m.strip()]
                edit_secondary_muscles = st.multiselect(
                    "Secondary Muscle Groups",
                    options=MUSCLE_GROUPS,
                    default=current_secondary,
                    help="Select any secondary muscle groups"
                )

                # Conditional inputs based on progression scheme
                if edit_progression_scheme == "Rep Range":
                    col_min, col_max = st.columns(2)
                    with col_min:
                        # Safe conversion with NaN check
                        rep_min_val = exercise_to_edit.get('rep_range_min')
                        rep_min_val = int(rep_min_val) if pd.notna(rep_min_val) else 8
                        edit_rep_range_min = st.number_input(
                            "Min Reps",
                            min_value=1,
                            max_value=50,
                            value=rep_min_val,
                            help="Minimum reps in the range"
                        )
                    with col_max:
                        rep_max_val = exercise_to_edit.get('rep_range_max')
                        rep_max_val = int(rep_max_val) if pd.notna(rep_max_val) else 12
                        edit_rep_range_max = st.number_input(
                            "Max Reps",
                            min_value=1,
                            max_value=50,
                            value=rep_max_val,
                            help="Maximum reps in the range"
                        )
                    edit_target_reps = None
                    edit_rep_increment = None
                    weight_inc_val = exercise_to_edit.get('weight_increment')
                    weight_inc_val = float(weight_inc_val) if pd.notna(weight_inc_val) else 5.0
                    edit_weight_increment = st.number_input(
                        "Weight Increment (lbs) *",
                        min_value=-50.0,
                        max_value=50.0,
                        value=weight_inc_val,
                        step=0.5,
                        help="Amount to change weight on successful workout (use negative for assisted exercises)"
                    )
                elif edit_progression_scheme == "Linear Weight":
                    target_reps_val = exercise_to_edit.get('target_reps')
                    target_reps_val = int(target_reps_val) if pd.notna(target_reps_val) else 5
                    edit_target_reps = st.number_input(
                        "Target Reps",
                        min_value=1,
                        max_value=50,
                        value=target_reps_val,
                        help="Fixed number of reps for each set"
                    )
                    edit_rep_range_min = None
                    edit_rep_range_max = None
                    edit_rep_increment = None
                    weight_inc_val = exercise_to_edit.get('weight_increment')
                    weight_inc_val = float(weight_inc_val) if pd.notna(weight_inc_val) else 5.0
                    edit_weight_increment = st.number_input(
                        "Weight Increment (lbs) *",
                        min_value=-50.0,
                        max_value=50.0,
                        value=weight_inc_val,
                        step=0.5,
                        help="Amount to change weight on successful workout (use negative for assisted exercises)"
                    )
                else:  # Linear Reps
                    target_reps_val = exercise_to_edit.get('target_reps')
                    target_reps_val = int(target_reps_val) if pd.notna(target_reps_val) else 5
                    edit_target_reps = st.number_input(
                        "Starting Reps",
                        min_value=1,
                        max_value=50,
                        value=target_reps_val,
                        help="Starting number of reps for each set"
                    )
                    edit_rep_range_min = None
                    edit_rep_range_max = None
                    rep_inc_val = exercise_to_edit.get('rep_increment')
                    rep_inc_val = int(rep_inc_val) if pd.notna(rep_inc_val) else 1
                    edit_rep_increment = st.number_input(
                        "Rep Increment *",
                        min_value=1,
                        max_value=10,
                        value=rep_inc_val,
                        help="Number of reps to add each successful workout"
                    )
                    edit_weight_increment = None

                # Form buttons
                col1, col2 = st.columns([1, 1])
                with col1:
                    cancel_button = st.form_submit_button("Cancel", use_container_width=True)
                with col2:
                    save_button = st.form_submit_button("Save Changes", type="primary", use_container_width=True)

                if cancel_button:
                    del st.session_state['editing_exercise_id']
                    if 'edit_prog_scheme' in st.session_state:
                        del st.session_state['edit_prog_scheme']
                    st.rerun()

                if save_button:
                    # Validate
                    if not edit_name.strip():
                        st.error("Exercise name is required")
                    elif not edit_primary_muscles:
                        st.error("At least one primary muscle group is required")
                    elif edit_progression_scheme == "Rep Range" and edit_rep_range_min >= edit_rep_range_max:
                        st.error("Min reps must be less than max reps")
                    else:
                        # Map UI progression scheme to database value
                        if edit_progression_scheme == "Rep Range":
                            prog_scheme_db = "rep_range"
                        elif edit_progression_scheme == "Linear Weight":
                            prog_scheme_db = "linear_weight"
                        else:
                            prog_scheme_db = "linear_reps"

                        # Build exercise data
                        exercise_data = {
                            "name": edit_name.strip(),
                            "description": edit_description.strip(),
                            "primary_muscle_groups": ",".join([m.lower() for m in edit_primary_muscles]),
                            "secondary_muscle_groups": ",".join([m.lower() for m in edit_secondary_muscles]) if edit_secondary_muscles else "",
                            "progression_scheme": prog_scheme_db,
                            "rep_range_min": edit_rep_range_min,
                            "rep_range_max": edit_rep_range_max,
                            "target_reps": edit_target_reps,
                            "rep_increment": edit_rep_increment,
                            "weight_increment": edit_weight_increment,
                            "warmup_config": exercise_to_edit.get('warmup_config')
                        }

                        try:
                            workflow.handle_update_exercise(st.session_state['editing_exercise_id'], exercise_data)
                            st.success(f"✅ Exercise '{edit_name}' updated successfully!")
                            del st.session_state['editing_exercise_id']
                            if 'edit_prog_scheme' in st.session_state:
                                del st.session_state['edit_prog_scheme']
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Validation error: {str(e)}")
                        except Exception as e:
                            st.error(f"Error updating exercise: {str(e)}")

    # Footer
    st.write("---")
    st.caption("💡 Tip: Create exercises first, then build workouts using them on the 'Create Workout' page")


# ============================================================================
# RENDER: CREATE WORKOUT
# ============================================================================

def render_create_workout():
    """Render the Create Workout page"""

    st.title("🏋️ Create Workout")
    st.write("Build workout templates by selecting exercises from your library")

    # ========================================================================
    # WORKOUT CREATION FORM
    # ========================================================================

    st.subheader("Create New Workout")

    with st.form("workout_form", clear_on_submit=True):
        # Workout name (required)
        workout_name = st.text_input(
            "Workout Name *",
            placeholder="e.g., Push Day A, Leg Day, Full Body",
            help="Enter a descriptive name for your workout"
        )

        # Load all exercises for selection
        exercises_df = db.get_all_exercises()

        if exercises_df.empty:
            st.warning("⚠️ No exercises available. Please create exercises first in the Exercise Library.")
            exercise_selection = []
        else:
            # Create display options for multiselect (show name with ID)
            exercise_options = {}
            for _, exercise in exercises_df.iterrows():
                display_name = f"{exercise['name']} (ID: {exercise['id']})"
                exercise_options[display_name] = exercise['id']

            # Exercise multiselect
            selected_exercise_names = st.multiselect(
                "Select Exercises *",
                options=list(exercise_options.keys()),
                help="Select exercises in the order you want to perform them"
            )

            # Convert selected names to IDs
            exercise_selection = [exercise_options[name] for name in selected_exercise_names]

        # Display selected exercises in order
        if exercise_selection:
            st.write("**Selected Exercises (in order):**")

            for idx, exercise_id in enumerate(exercise_selection, start=1):
                exercise = exercises_df[exercises_df['id'] == exercise_id].iloc[0]

                col1, col2, col3 = st.columns([1, 4, 3])
                with col1:
                    st.write(f"**{idx}.**")
                with col2:
                    st.write(f"**{exercise['name']}**")
                with col3:
                    muscles = exercise['primary_muscle_groups'].replace(',', ', ').title()
                    scheme = "Rep Range" if exercise['progression_scheme'] == "rep_range" else "Linear Weight"
                    st.write(f"*{muscles} • {scheme}*")

        # Notes (optional)
        workout_notes = st.text_area(
            "Notes (Optional)",
            placeholder="Add any notes about this workout template...",
            help="Optional notes about the workout"
        )

        # Submit button
        submit_button = st.form_submit_button("Create Workout", use_container_width=True)

        # Form submission handling
        if submit_button:
            # Validate required fields
            if not workout_name.strip():
                st.error("❌ Workout name is required")
            elif not exercise_selection:
                st.error("❌ At least one exercise must be selected")
            else:
                try:
                    # Call workflow to create workout
                    workout_id = workflow.handle_create_workout(
                        name=workout_name.strip(),
                        exercise_ids=exercise_selection,
                        notes=workout_notes.strip()
                    )
                    st.success(f"✅ Workout '{workout_name}' created successfully (ID: {workout_id})")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Validation error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error creating workout: {str(e)}")

    # ========================================================================
    # WORKOUT LIST VIEW
    # ========================================================================

    st.write("---")
    st.subheader("Your Workouts")

    # Load all workouts
    workouts_df = db.get_all_workouts()

    if workouts_df.empty:
        st.info("📝 No workouts created yet. Create your first workout using the form above!")
    else:
        # Display workout count
        st.write(f"Total Workouts: **{len(workouts_df)}**")

        # Prepare display data
        display_data = []
        for _, workout in workouts_df.iterrows():
            # Count exercises
            exercise_ids = []
            if workout['exercise_ids']:
                exercise_ids = [int(x.strip()) for x in str(workout['exercise_ids']).split(',')]

            exercise_count = len(exercise_ids)
            created_date = workout['created_at'].strftime('%Y-%m-%d') if pd.notna(workout['created_at']) else 'N/A'

            display_data.append({
                'ID': workout['id'],
                'Name': workout['name'],
                'Exercises': exercise_count,
                'Created': created_date
            })

        # Display as table
        display_df = pd.DataFrame(display_data)
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=300
        )

        # Workout details expanders
        st.write("---")
        st.write("**Workout Details**")

        # Select workout to view details
        workout_names = workouts_df['name'].tolist()
        selected_workout_name = st.selectbox(
            "Select workout to view details",
            options=workout_names,
            label_visibility="collapsed"
        )

        if selected_workout_name:
            # Get workout details
            workout_row = workouts_df[workouts_df['name'] == selected_workout_name].iloc[0]
            workout_id = workout_row['id']

            # Load full workout details with exercises
            workout_details = workflow.get_workout_details(workout_id)

            with st.expander(f"📋 {selected_workout_name}", expanded=True):
                # Workout info
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**ID:** {workout_details['id']}")
                    st.write(f"**Exercises:** {len(workout_details['exercises'])}")

                with col2:
                    created = workout_details['created_at'].strftime('%Y-%m-%d') if pd.notna(workout_details['created_at']) else 'N/A'
                    st.write(f"**Created:** {created}")

                # Notes
                if workout_details['notes']:
                    st.write("**Notes:**")
                    st.write(workout_details['notes'])

                # Exercise list
                st.write("**Exercise List:**")

                for idx, exercise in enumerate(workout_details['exercises'], start=1):
                    col_num, col_name, col_muscles, col_scheme = st.columns([1, 4, 3, 2])

                    with col_num:
                        st.write(f"**{idx}.**")

                    with col_name:
                        st.write(exercise['name'])

                    with col_muscles:
                        muscles = exercise['primary_muscle_groups'].replace(',', ', ').title()
                        st.write(f"*{muscles}*")

                    with col_scheme:
                        scheme = "Rep Range" if exercise['progression_scheme'] == "rep_range" else "Linear Weight"
                        st.write(f"*{scheme}*")

                    # Show last performance if available
                    if exercise['last_performance']:
                        last_perf = exercise['last_performance']
                        last_date = last_perf['last_workout_date'].strftime('%Y-%m-%d') if pd.notna(last_perf['last_workout_date']) else 'N/A'
                        st.caption(
                            f"   Last: {last_perf['last_weight']} lbs × {last_perf['last_reps']} reps "
                            f"(1RM: {last_perf['last_1rm']:.1f} lbs) on {last_date}"
                        )

    # Footer
    st.write("---")
    st.caption("💡 Tip: Go to 'Workout Overview' to select and start a workout")


# ============================================================================
# RENDER: WORKOUT OVERVIEW
# ============================================================================

def render_workout_overview():
    """Render the Workout Overview page"""

    st.title("📊 Workout Overview")
    st.write("Select a workout to start your training session")

    # ========================================================================
    # WORKOUT SELECTION INTERFACE
    # ========================================================================

    # Load all workouts
    workouts_df = db.get_all_workouts()

    if workouts_df.empty:
        st.info("📝 No workouts available. Create your first workout in the 'Create Workout' page!")
        return

    # Display workouts as cards
    st.subheader("Available Workouts")
    st.write(f"You have **{len(workouts_df)}** workout(s) ready to go")

    # Create workout cards
    for _, workout_row in workouts_df.iterrows():
        workout_id = workout_row['id']

        # Load workout details
        workout_details = workflow.get_workout_details(workout_id)

        # Count exercises
        exercise_count = len(workout_details['exercises'])
        created_date = workout_details['created_at'].strftime('%Y-%m-%d') if pd.notna(workout_details['created_at']) else 'N/A'

        # Create a container for each workout card
        with st.container():
            col_info, col_button = st.columns([4, 1])

            with col_info:
                st.markdown(f"### {workout_details['name']}")

                # Workout summary
                col_exercises, col_created = st.columns(2)
                with col_exercises:
                    st.write(f"**Exercises:** {exercise_count}")
                with col_created:
                    st.write(f"**Created:** {created_date}")

                # Notes preview
                if workout_details['notes']:
                    notes = workout_details['notes']
                    if pd.isna(notes):
                        st.caption("")
                    elif len(notes) > 100:
                        st.caption(f"*{notes[:100]}...*")
                    else:
                        st.caption(f"*{notes}*")

            with col_button:
                # Start workout button
                if st.button(
                    "🚀 Start Workout",
                    key=f"start_{workout_id}",
                    use_container_width=True,
                    type="primary"
                ):
                    # Store workout_id in session state
                    st.session_state['selected_workout_id'] = workout_id
                    st.session_state['navigate_to_execution'] = True

                    # Clear any existing workout session state
                    keys_to_clear = [
                        'workout_log_id',
                        'workout_plan',
                        'set_completion',
                        'start_time',
                        'workout_initialized'
                    ]
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]

                    st.success(f"✅ Starting '{workout_details['name']}'...")
                    st.rerun()

            # View details expander
            with st.expander(f"📋 View Details: {workout_details['name']}", expanded=False):
                st.write("**Exercise List:**")

                # Display exercises in a clean format
                for idx, exercise in enumerate(workout_details['exercises'], start=1):
                    st.write(f"**{idx}. {exercise['name']}**")

                    # Exercise info
                    col_muscles, col_scheme = st.columns(2)

                    with col_muscles:
                        muscles = exercise['primary_muscle_groups'].replace(',', ', ').title()
                        st.caption(f"Primary Muscles: {muscles}")

                    with col_scheme:
                        scheme = "Rep Range" if exercise['progression_scheme'] == "rep_range" else "Linear Weight"
                        st.caption(f"Progression: {scheme}")

                    # Last performance data
                    if exercise['last_performance']:
                        last_perf = exercise['last_performance']
                        last_date = last_perf['last_workout_date']

                        if pd.notna(last_date):
                            last_date_str = last_date.strftime('%Y-%m-%d %H:%M')
                        else:
                            last_date_str = 'N/A'

                        st.caption(
                            f"📈 Last Performance: {last_perf['last_weight']} lbs × {last_perf['last_reps']} reps "
                            f"(1RM: {last_perf['last_1rm']:.1f} lbs) on {last_date_str}"
                        )
                    else:
                        st.caption("📈 Last Performance: No history yet (first time!)")

                    # Add spacing between exercises
                    if idx < len(workout_details['exercises']):
                        st.write("")

            # Divider between workout cards
            st.write("---")

    # ========================================================================
    # INSTRUCTIONS
    # ========================================================================

    st.subheader("💡 How to Use")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Starting a Workout:**")
        st.write("1. Review the workout details")
        st.write("2. Click 'Start Workout' button")
        st.write("3. Follow the generated sets")
        st.write("4. Track your progress")

    with col2:
        st.write("**What Happens Next:**")
        st.write("• Sets are generated based on your history")
        st.write("• Warmup sets are included if configured")
        st.write("• Progression logic determines weight/reps")
        st.write("• Complete sets and save your workout")

    # Footer
    st.write("---")
    st.caption("💪 Ready to train? Pick a workout and let's go!")


# ============================================================================
# RENDER: WORKOUT EXECUTION
# ============================================================================

def render_workout_execution():
    """Render the Workout Execution page"""

    # Import the entire page module since it's complex
    # We'll read and adapt it inline here

    # Check for workout selection
    if 'selected_workout_id' not in st.session_state:
        st.warning("⚠️ No workout selected. Please select a workout from the Workout Overview tab.")
        return

    # Initialize workout on first load
    if 'workout_initialized' not in st.session_state or not st.session_state.get('workout_initialized', False):
        try:
            # Call workflow to start workout and generate sets
            workout_id = st.session_state['selected_workout_id']
            workout_plan = workflow.handle_start_workout(workout_id)

            # Store workout plan in session state
            st.session_state['workout_log_id'] = workout_plan['workout_log_id']
            st.session_state['workout_name'] = workout_plan['workout_name']
            st.session_state['workout_exercises'] = workout_plan['exercises']
            st.session_state['start_time'] = datetime.now()
            st.session_state['workout_initialized'] = True

            # Initialize set completion tracking
            if 'set_completion' not in st.session_state:
                st.session_state['set_completion'] = {}

        except Exception as e:
            st.error(f"❌ Error initializing workout: {str(e)}")
            st.warning("Please go back and try starting the workout again.")
            return

    # Get workout data from session state
    workout_name = st.session_state.get('workout_name', 'Unknown Workout')
    workout_exercises = st.session_state.get('workout_exercises', [])
    start_time = st.session_state.get('start_time', datetime.now())

    # Page header
    st.title(f"💪 {workout_name}")

    # Workout timer
    elapsed_time = datetime.now() - start_time
    hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    st.write(f"⏱️ Workout Duration: **{hours:02d}:{minutes:02d}:{seconds:02d}**")
    st.write("---")

    # Display exercises and sets
    for exercise_idx, exercise in enumerate(workout_exercises):
        exercise_id = exercise['exercise_id']
        exercise_name = exercise['exercise_name']
        sets = exercise['sets']

        st.subheader(f"Exercise {exercise_idx + 1}: {exercise_name}")

        # Display each set
        for set_idx, set_data in enumerate(sets):
            set_number = set_data['set_number']
            set_type = set_data['set_type']
            target_weight = set_data['target_weight']
            target_reps = set_data['target_reps']

            # Create unique key for this set
            set_key = (exercise_id, set_number)

            # Set display
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

            with col1:
                set_label = "Warmup" if set_type == "warmup" else "Working"
                st.write(f"**Set {set_number}** ({set_label})")

            with col2:
                st.write(f"Target: **{target_weight} lbs × {target_reps} reps**")

            with col3:
                # Input for actual performance
                if set_key not in st.session_state['set_completion']:
                    actual_weight = st.number_input(
                        "Actual Weight",
                        min_value=0.0,
                        value=float(target_weight),
                        step=2.5,
                        key=f"weight_{exercise_id}_{set_number}",
                        label_visibility="collapsed"
                    )
                    actual_reps = st.number_input(
                        "Actual Reps",
                        min_value=0,
                        value=int(target_reps),
                        step=1,
                        key=f"reps_{exercise_id}_{set_number}",
                        label_visibility="collapsed"
                    )
                else:
                    completed_data = st.session_state['set_completion'][set_key]
                    st.write(f"✅ {completed_data['weight']} lbs × {completed_data['reps']} reps")

            with col4:
                if set_key not in st.session_state['set_completion']:
                    if st.button("✓", key=f"complete_{exercise_id}_{set_number}"):
                        # Mark set as complete
                        st.session_state['set_completion'][set_key] = {
                            'weight': actual_weight,
                            'reps': actual_reps,
                            'set_type': set_type
                        }
                        st.rerun()

        st.write("---")

    # Check if all sets are completed
    total_sets = sum(len(ex['sets']) for ex in workout_exercises)
    completed_sets = len(st.session_state['set_completion'])

    st.progress(completed_sets / total_sets if total_sets > 0 else 0)
    st.write(f"**Progress:** {completed_sets} / {total_sets} sets completed")

    # Finish workout button
    if completed_sets == total_sets:
        st.success("🎉 All sets completed! You can now finish your workout.")

        if st.button("🏁 Finish Workout", type="primary", use_container_width=True):
            try:
                # Prepare set data for saving
                completed_sets_data = []
                for exercise in workout_exercises:
                    exercise_id = exercise['exercise_id']
                    for set_data in exercise['sets']:
                        set_number = set_data['set_number']
                        set_key = (exercise_id, set_number)

                        if set_key in st.session_state['set_completion']:
                            completed = st.session_state['set_completion'][set_key]
                            completed_sets_data.append({
                                'exercise_id': exercise_id,
                                'set_number': set_number,
                                'set_type': completed['set_type'],
                                'target_weight': set_data['target_weight'],
                                'target_reps': set_data['target_reps'],
                                'actual_weight': completed['weight'],
                                'actual_reps': completed['reps']
                            })

                # Save workout
                workout_log_id = st.session_state['workout_log_id']
                workflow.handle_complete_workout(workout_log_id, completed_sets_data)

                # Clear session state
                for key in ['selected_workout_id', 'workout_log_id', 'workout_name',
                           'workout_exercises', 'start_time', 'workout_initialized',
                           'set_completion']:
                    if key in st.session_state:
                        del st.session_state[key]

                st.success("✅ Workout saved successfully!")
                st.balloons()

                # Navigate back after short delay
                st.info("Returning to workout overview...")
                st.session_state['navigate_to_overview'] = True
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error saving workout: {str(e)}")


# ============================================================================
# RENDER: HISTORY
# ============================================================================

def render_history():
    """Render the Workout History page"""

    st.title("📊 Workout History")
    st.write("Review your workout history and track your progress")

    # Load workout history
    history_df = db.get_all_workout_logs()

    if history_df.empty:
        st.info("No workout history yet. Complete your first workout to see it here!")
        return

    # Display summary stats
    st.subheader("Summary Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_workouts = len(history_df)
        st.metric("Total Workouts", total_workouts)

    with col2:
        # Get unique workout dates
        if 'start_time' in history_df.columns:
            unique_dates = history_df['start_time'].dt.date.nunique()
            st.metric("Training Days", unique_dates)

    with col3:
        # Calculate total sets from set logs
        set_logs_df = db.get_all_set_logs()
        total_sets = len(set_logs_df) if not set_logs_df.empty else 0
        st.metric("Total Sets", total_sets)

    st.write("---")

    # Recent workouts
    st.subheader("Recent Workouts")

    # Prepare display data
    display_data = []
    for _, log in history_df.head(20).iterrows():
        # Get workout name (handle NULL workout_id for ad-hoc workouts)
        if pd.notna(log.get('workout_id')):
            workout = db.get_workout_by_id(log['workout_id'])
            workout_name = workout['name'] if workout is not None else 'Unknown Template'
        else:
            # Format: "Manual Entry - YYYY-MM-DD"
            workout_date_str = pd.to_datetime(log['start_time']).strftime('%Y-%m-%d') if pd.notna(log['start_time']) else 'N/A'
            workout_name = f'Manual Entry - {workout_date_str}'

        # Format date
        workout_date = log['start_time'].strftime('%Y-%m-%d %H:%M') if pd.notna(log['start_time']) else 'N/A'

        # Get metadata if available
        duration = log.get('duration_seconds', 'N/A')
        if duration != 'N/A' and pd.notna(duration):
            duration = int(duration / 60)  # Convert seconds to minutes
        total_volume = log.get('total_volume', 'N/A')

        display_data.append({
            'Date': workout_date,
            'Workout': workout_name,
            'Duration (min)': duration,
            'Volume (lbs)': total_volume
        })

    if display_data:
        display_df = pd.DataFrame(display_data)
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )

    st.write("---")
    st.caption("💡 View individual workout details and progress charts coming soon!")


# ============================================================================
# RENDER: LOG OLD WORKOUT
# ============================================================================

def render_log_old_workout():
    """Render the Log Old Workout page"""

    st.title("📝 Log Old Workout")
    st.write("Manually log a workout from the past to add it to your history.")
    st.write("---")

    # Initialize session state for logged sets
    if 'logged_sets' not in st.session_state:
        st.session_state['logged_sets'] = []

    # Workout Details Section
    st.subheader("1. Workout Details")

    col_workout, col_date = st.columns(2)

    with col_workout:
        # Load all workouts
        workouts_df = db.get_all_workouts()

        # Create workout options with "No template" as default
        workout_options = {"(No template - just log sets)": None}
        if not workouts_df.empty:
            for _, row in workouts_df.iterrows():
                workout_options[row['name']] = row['id']

        # Workout selection (optional)
        selected_workout_name = st.selectbox(
            "Select Workout (Optional)",
            options=list(workout_options.keys()),
            help="Choose a workout template if you want to associate these sets with one, or leave as 'No template' to just log individual sets"
        )
        selected_workout_id = workout_options[selected_workout_name]

    with col_date:
        # Date/time selection
        workout_date = st.date_input(
            "Workout Date",
            value=datetime.now().date(),
            max_value=datetime.now().date(),
            help="When did you perform this workout?"
        )

        workout_time = st.time_input(
            "Workout Time",
            value=datetime.now().time(),
            help="What time did you start?"
        )

    # Combine date and time
    workout_datetime = datetime.combine(workout_date, workout_time)

    # Notes section
    workout_notes = st.text_area(
        "Workout Notes (Optional)",
        placeholder="Add any notes about this workout (e.g., how you felt, PRs, modifications, etc.)",
        help="Optional notes about the workout session"
    )

    st.write("---")

    # Enter Set Data Section
    st.subheader("2. Enter Set Data")

    # Load all exercises for dropdown
    exercises_df = db.get_all_exercises()

    if exercises_df.empty:
        st.warning("No exercises available. Please create exercises first in the Exercise Library.")
        return

    # Create exercise options for dropdown
    exercise_options = {}
    for _, exercise in exercises_df.iterrows():
        display_name = f"{exercise['name']}"
        exercise_options[display_name] = {
            'id': exercise['id'],
            'name': exercise['name']
        }

    # Form to add a single set
    with st.form("add_set_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            selected_exercise_name = st.selectbox(
                "Exercise",
                options=list(exercise_options.keys()),
                help="Select the exercise for this set"
            )

        with col2:
            weight = st.number_input(
                "Weight (lbs)",
                min_value=0.0,
                value=135.0,
                step=2.5,
                help="Weight used for this set"
            )

        with col3:
            reps = st.number_input(
                "Reps",
                min_value=0,
                value=10,
                step=1,
                help="Reps completed"
            )

        # Notes field (optional)
        set_notes = st.text_input(
            "Set Notes (Optional)",
            placeholder="e.g., 'felt easy', 'struggled on last rep', 'form breakdown'",
            help="Optional notes about this specific set"
        )

        # Add set button
        add_set_button = st.form_submit_button("➕ Add Set", use_container_width=True)

        if add_set_button:
            # Get exercise details
            exercise_info = exercise_options[selected_exercise_name]

            # Add set to session state
            st.session_state['logged_sets'].append({
                'exercise_id': exercise_info['id'],
                'exercise_name': exercise_info['name'],
                'weight': weight,
                'reps': reps,
                'set_type': 'working',
                'notes': set_notes.strip() if set_notes else ''
            })
            st.rerun()

    # Display logged sets
    if st.session_state['logged_sets']:
        st.write("---")
        st.subheader("Logged Sets")

        # Group sets by exercise
        exercise_groups = {}
        for idx, set_data in enumerate(st.session_state['logged_sets']):
            exercise_name = set_data['exercise_name']
            if exercise_name not in exercise_groups:
                exercise_groups[exercise_name] = []
            exercise_groups[exercise_name].append((idx, set_data))

        # Display sets grouped by exercise
        for exercise_name, sets in exercise_groups.items():
            st.write(f"**{exercise_name}** ({len(sets)} sets)")

            for set_idx, (global_idx, set_data) in enumerate(sets, start=1):
                col1, col2, col3 = st.columns([1, 3, 1])

                with col1:
                    st.write(f"Set {set_idx}")

                with col2:
                    st.write(f"{set_data['weight']} lbs × {set_data['reps']} reps")
                    # Show notes if they exist
                    if set_data.get('notes'):
                        st.caption(f"💬 {set_data['notes']}")

                with col3:
                    if st.button("🗑️", key=f"delete_{global_idx}", help="Remove this set"):
                        st.session_state['logged_sets'].pop(global_idx)
                        st.rerun()

            st.write("")

        # Clear all button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Clear All Sets", use_container_width=True):
                st.session_state['logged_sets'] = []
                st.rerun()

        # Save workout button
        with col2:
            if st.button("💾 Save Workout", type="primary", use_container_width=True):
                try:
                    # Prepare set data with set numbers per exercise
                    set_data_by_exercise = {}
                    for set_info in st.session_state['logged_sets']:
                        exercise_id = set_info['exercise_id']
                        if exercise_id not in set_data_by_exercise:
                            set_data_by_exercise[exercise_id] = []
                        set_data_by_exercise[exercise_id].append(set_info)

                    # Add set numbers
                    formatted_sets = []
                    for exercise_id, sets in set_data_by_exercise.items():
                        for set_num, set_info in enumerate(sets, start=1):
                            formatted_sets.append({
                                'exercise_id': exercise_id,
                                'set_number': set_num,
                                'weight': set_info['weight'],
                                'reps': set_info['reps'],
                                'set_type': set_info['set_type'],
                                'notes': set_info.get('notes', '')
                            })

                    # Create workout log
                    workout_log_id = workflow.handle_log_old_workout(
                        workout_id=selected_workout_id,
                        workout_datetime=workout_datetime,
                        set_data=formatted_sets,
                        notes=workout_notes
                    )

                    st.success(f"✅ Workout logged successfully! (Log ID: {workout_log_id})")
                    st.balloons()

                    # Clear session state
                    st.session_state['logged_sets'] = []
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error logging workout: {str(e)}")
    else:
        st.info("👆 Add sets using the form above. Sets will appear here as you add them.")


# ============================================================================
# RENDER: ANALYTICS
# ============================================================================

def render_analytics():
    """Render the Analytics page with filterable historic data"""

    st.title("📊 Analytics")
    st.write("View and analyze your workout history")

    # Load all set logs
    all_sets_df = db.get_all_set_logs()

    if all_sets_df.empty:
        st.info("No workout data yet. Complete some workouts to see analytics!")
        return

    # Load all workouts and exercises for reference
    all_workouts_df = db.get_all_workouts()
    all_exercises_df = db.get_all_exercises()

    # Create lookup dictionaries
    exercise_name_map = {row['id']: row['name'] for _, row in all_exercises_df.iterrows()}

    # Add exercise names to sets
    all_sets_df['exercise_name'] = all_sets_df['exercise_id'].map(exercise_name_map)

    # Get workout dates from workout_log_id
    workout_logs_df = db.load_table("workout_logs")
    workout_date_map = {row['id']: row['start_time'] for _, row in workout_logs_df.iterrows()}
    all_sets_df['workout_date'] = all_sets_df['workout_log_id'].map(workout_date_map)

    # Convert workout_date to datetime if it's not already
    all_sets_df['workout_date'] = pd.to_datetime(all_sets_df['workout_date'])

    # Extract just the date for filtering
    all_sets_df['date_only'] = all_sets_df['workout_date'].dt.date

    st.subheader("Filter Options")

    # Create filter columns
    col1, col2 = st.columns(2)

    with col1:
        # Date filter
        unique_dates = sorted(all_sets_df['date_only'].dropna().unique(), reverse=True)
        date_options = ["All Dates"] + [str(d) for d in unique_dates]

        selected_date = st.selectbox(
            "Filter by Date",
            options=date_options,
            help="Select a specific workout date to view all sets from that day"
        )

    with col2:
        # Exercise filter
        unique_exercises = sorted(all_sets_df['exercise_name'].dropna().unique())
        exercise_options = ["All Exercises"] + unique_exercises

        selected_exercise = st.selectbox(
            "Filter by Exercise",
            options=exercise_options,
            help="Select a specific exercise to view all historic sets"
        )

    # Apply filters
    filtered_df = all_sets_df.copy()

    if selected_date != "All Dates":
        filtered_df = filtered_df[filtered_df['date_only'].astype(str) == selected_date]

    if selected_exercise != "All Exercises":
        filtered_df = filtered_df[filtered_df['exercise_name'] == selected_exercise]

    # Display results
    st.subheader("Results")

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
    else:
        # Show summary stats
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric("Total Sets", len(filtered_df))

        with col_stat2:
            total_volume = (filtered_df['target_weight'] * filtered_df['target_reps']).sum()
            st.metric("Total Volume (lbs)", f"{total_volume:,.0f}")

        with col_stat3:
            unique_exercises_count = filtered_df['exercise_name'].nunique()
            st.metric("Exercises", unique_exercises_count)

        with col_stat4:
            unique_dates_count = filtered_df['date_only'].nunique()
            st.metric("Workout Days", unique_dates_count)

        st.markdown("---")

        # Prepare display dataframe
        display_columns = [
            'workout_date',
            'exercise_name',
            'set_type',
            'set_number',
            'target_weight',
            'actual_weight',
            'target_reps',
            'actual_reps',
            'completed',
            'volume',
            'one_rep_max_estimate',
            'notes'
        ]

        # Filter to only existing columns
        display_columns = [col for col in display_columns if col in filtered_df.columns]

        display_df = filtered_df[display_columns].copy()

        # Format the workout_date column
        display_df['workout_date'] = display_df['workout_date'].dt.strftime('%Y-%m-%d %H:%M')

        # Rename columns for better display
        display_df = display_df.rename(columns={
            'workout_date': 'Workout Date',
            'exercise_name': 'Exercise',
            'set_type': 'Set Type',
            'set_number': 'Set #',
            'target_weight': 'Target Weight (lbs)',
            'actual_weight': 'Actual Weight (lbs)',
            'target_reps': 'Target Reps',
            'actual_reps': 'Actual Reps',
            'completed': 'Completed',
            'volume': 'Volume (lbs)',
            'one_rep_max_estimate': '1RM Estimate',
            'notes': 'Notes'
        })

        # Sort by date descending (most recent first)
        display_df = display_df.sort_values('Workout Date', ascending=False)

        # Display the table
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"workout_analytics_{selected_date}_{selected_exercise}.csv",
            mime="text/csv"
        )


# ============================================================================
# RENDER: ABOUT
# ============================================================================

def render_about():
    """Render the About/Documentation page"""

    st.title("💪 Exercise Tracker")
    st.write("Welcome to your personal workout tracking and progression system!")

    st.markdown("""
    ## Features

    - **Intelligent Progression**: Automatically calculates next workout parameters based on performance history
    - **Flexible Schemes**: Supports two distinct progression methodologies (rep range and linear weight)
    - **1RM-Based Planning**: Uses one-rep max estimation to determine appropriate training loads
    - **Warmup Set Generation**: Automatically generates warmup sets based on working set intensity
    - **Comprehensive Tracking**: Records all workout data with detailed metadata
    - **Historical Logging**: Backfill past workouts to build your training history

    ## Getting Started

    ### 1. Create Exercises (Exercise Library Tab)
    - Define exercises with progression schemes (rep range or linear weight)
    - Configure warmup sets for compound movements
    - Set weight increments for progressive overload

    ### 2. Build Workout Templates (Create Workout Tab)
    - Combine exercises into workout routines
    - Exercises will be performed in the order selected
    - Add notes for workout-specific guidance

    ### 3. Execute Workouts (Workout Overview Tab)
    - Select a workout template to begin
    - App generates appropriate sets based on your history
    - Track performance in real-time during execution

    ### 4. Review Progress (History Tab)
    - View completed workouts and statistics
    - Track volume, 1RM estimates, and training frequency
    - Analyze your progression over time

    ## Progression Logic

    ### Rep Range Progression
    - Start at minimum reps (e.g., 8 reps with 135 lbs)
    - Add 1 rep each successful workout (9, 10, 11, 12...)
    - When you hit max reps, increase weight and reset to min reps
    - Example: 135×12 → 140×8

    ### Linear Weight Progression
    - Fixed number of reps per set (e.g., always 5 reps)
    - Add weight each successful workout (e.g., +5 lbs)
    - If you fail, repeat the same weight next time
    - Example: 225×5 → 230×5 → 235×5

    ### Warmup Sets
    Automatically generated based on working set intensity:
    - **Low intensity (0-50% 1RM)**: 1 warmup set
    - **Medium intensity (50-70% 1RM)**: 2 warmup sets
    - **High intensity (70-100% 1RM)**: 3 warmup sets

    Default warmup percentages: 40%, 60%, 80% of working weight

    ## Tips for Success

    - **Create exercises first** before building workouts
    - **Enable warmup sets** for heavy compound movements
    - **Be consistent** with tracking to ensure accurate progression
    - **Use rep range** for hypertrophy (8-12 reps)
    - **Use linear weight** for strength (3-5 reps)
    - **Log old workouts** to build your training history

    ## Data Storage

    All data is stored locally in CSV files in the `data/` directory. Your data includes:
    - Exercise library definitions
    - Workout templates
    - Workout logs (completed sessions)
    - Set logs (individual set performance)

    To backup your data, simply copy the `data/` folder.
    """)


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_exercise_app():
    """
    Main render function for the Exercise Tracker app.
    This function can be imported and called from other Streamlit apps.
    """

    # Check for navigation flags
    if st.session_state.get('navigate_to_execution', False):
        st.session_state['navigate_to_execution'] = False
        st.session_state['active_tab'] = 3  # Workout Execution tab

    if st.session_state.get('navigate_to_overview', False):
        st.session_state['navigate_to_overview'] = False
        st.session_state['active_tab'] = 2  # Workout Overview tab

    # Create tabs for navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📚 Exercise Library",
        "🏋️ Create Workout",
        "📊 Workout Overview",
        "💪 Workout Execution",
        "📈 History",
        "📝 Log Old Workout",
        "📊 Analytics",
        "ℹ️ About"
    ])

    with tab1:
        render_exercise_library()

    with tab2:
        render_create_workout()

    with tab3:
        render_workout_overview()

    with tab4:
        render_workout_execution()

    with tab5:
        render_history()

    with tab6:
        render_log_old_workout()

    with tab7:
        render_analytics()

    with tab8:
        render_about()

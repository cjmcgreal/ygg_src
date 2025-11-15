"""
Create Workout Page
Create workout templates by selecting exercises from the library
"""

import streamlit as st
import pandas as pd
import workflow
import db

# Page configuration
st.set_page_config(
    page_title="Create Workout - Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("🏋️ Create Workout")
st.write("Build workout templates by selecting exercises from your library")

# ============================================================================
# WORKOUT CREATION FORM
# ============================================================================

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

# ============================================================================
# WORKOUT LIST VIEW
# ============================================================================

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

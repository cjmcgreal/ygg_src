"""
Log Old Workout Page
Manually log workouts from the past to backfill workout history
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import db
import workflow
import analysis

# Page configuration
st.set_page_config(
    page_title="Log Old Workout - Exercise Tracker",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Log Old Workout")
st.write("Manually log a workout from the past to add it to your history.")

st.write("---")

# ============================================================================
# SELECT WORKOUT AND DATE
# ============================================================================

st.subheader("1. Workout Details")

col_workout, col_date = st.columns(2)

with col_workout:
    # Load all workouts
    workouts_df = db.get_all_workouts()

    if workouts_df.empty:
        st.warning("No workouts found. Please create a workout first.")
        if st.button("Go to Create Workout"):
            st.switch_page("pages/2_create_workout.py")
        st.stop()

    # Workout selection
    workout_options = {f"{row['name']}": row['id'] for _, row in workouts_df.iterrows()}
    selected_workout_name = st.selectbox(
        "Select Workout",
        options=list(workout_options.keys()),
        help="Choose the workout template you performed"
    )
    selected_workout_id = workout_options[selected_workout_name]

with col_date:
    # Date selection
    workout_date = st.date_input(
        "Workout Date",
        value=datetime.now().date() - timedelta(days=1),
        max_value=datetime.now().date(),
        help="When did you perform this workout?"
    )

    # Time selection
    workout_time = st.time_input(
        "Workout Time",
        value=datetime.now().time().replace(hour=9, minute=0, second=0),
        help="What time did you start?"
    )

# Combine date and time
workout_datetime = datetime.combine(workout_date, workout_time)

st.write("---")

# ============================================================================
# LOAD WORKOUT DETAILS
# ============================================================================

# Get workout details
workout = db.get_workout_by_id(selected_workout_id)

# Handle exercise_ids (could be string or list)
exercise_ids_raw = workout['exercise_ids']
if isinstance(exercise_ids_raw, str):
    exercise_ids = [int(x.strip()) for x in exercise_ids_raw.split(',')]
elif isinstance(exercise_ids_raw, list):
    exercise_ids = [int(x) for x in exercise_ids_raw]
else:
    exercise_ids = [int(exercise_ids_raw)]

st.subheader("2. Enter Exercise Data")

# Initialize session state for set data
if 'old_workout_sets' not in st.session_state:
    st.session_state['old_workout_sets'] = {}

# Load all exercises for dropdown
all_exercises_df = db.get_all_exercises()
if all_exercises_df.empty:
    st.warning("No exercises found. Please create exercises first.")
    st.stop()

# Create exercise options for dropdown
exercise_options = {}
for _, row in all_exercises_df.iterrows():
    exercise_options[f"{row['name']} ({row['primary_muscle_groups']})"] = row['id']

# Exercise selection dropdown
selected_exercise_display = st.selectbox(
    "Select Exercise to Log",
    options=list(exercise_options.keys()),
    help="Choose which exercise you want to log data for"
)
selected_exercise_id = exercise_options[selected_exercise_display]

# Get exercise details
exercise = db.get_exercise_by_id(selected_exercise_id)

if exercise:
    st.write("")
    st.write(f"### {exercise['name']}")
    st.caption(f"💪 {exercise['primary_muscle_groups']}")

    # Number of sets input
    set_count_key = f"set_count_{selected_exercise_id}"

    # Get existing value if already entered
    if set_count_key in st.session_state:
        default_sets = st.session_state[set_count_key]
    else:
        default_sets = 3

    num_sets = st.number_input(
        f"Number of sets completed",
        min_value=0,
        max_value=10,
        value=default_sets,
        step=1,
        key=set_count_key,
        help="How many sets did you complete for this exercise?"
    )

    if num_sets > 0:
        # Create columns for set data entry
        st.write("**Set Details:**")

        # Header row
        col_set, col_weight, col_reps = st.columns([1, 2, 2])
        with col_set:
            st.write("**Set #**")
        with col_weight:
            st.write("**Weight (lbs)**")
        with col_reps:
            st.write("**Reps**")

        # Data entry rows for each set
        for set_num in range(1, num_sets + 1):
            col_set, col_weight, col_reps = st.columns([1, 2, 2])

            with col_set:
                st.write(f"{set_num}")

            with col_weight:
                # Get existing value if already entered
                set_key = (selected_exercise_id, set_num)
                existing_weight = st.session_state['old_workout_sets'].get(set_key, {}).get('weight', 45.0)

                weight = st.number_input(
                    f"Weight for set {set_num}",
                    min_value=0.0,
                    max_value=1000.0,
                    value=float(existing_weight),
                    step=2.5,
                    key=f"weight_{selected_exercise_id}_{set_num}",
                    label_visibility="collapsed"
                )

            with col_reps:
                # Get existing value if already entered
                existing_reps = st.session_state['old_workout_sets'].get(set_key, {}).get('reps', 10)

                reps = st.number_input(
                    f"Reps for set {set_num}",
                    min_value=0,
                    max_value=100,
                    value=int(existing_reps),
                    step=1,
                    key=f"reps_{selected_exercise_id}_{set_num}",
                    label_visibility="collapsed"
                )

            # Store in session state
            set_key = (selected_exercise_id, set_num)
            st.session_state['old_workout_sets'][set_key] = {
                'weight': weight,
                'reps': reps,
                'exercise_name': exercise['name']
            }

# Show summary of exercises entered so far
st.write("")
st.write("---")
st.subheader("Exercises Logged So Far")

# Group sets by exercise
exercises_logged = {}
for set_key, set_data in st.session_state['old_workout_sets'].items():
    exercise_id, set_num = set_key
    if exercise_id not in exercises_logged:
        exercises_logged[exercise_id] = {
            'name': set_data.get('exercise_name', f'Exercise {exercise_id}'),
            'sets': []
        }
    exercises_logged[exercise_id]['sets'].append({
        'set_num': set_num,
        'weight': set_data['weight'],
        'reps': set_data['reps']
    })

if exercises_logged:
    for exercise_id, data in exercises_logged.items():
        # Get set count for this exercise
        set_count = st.session_state.get(f"set_count_{exercise_id}", 0)
        if set_count > 0:
            st.write(f"**{data['name']}**: {set_count} sets")
else:
    st.info("No exercises logged yet. Select an exercise above and enter set data.")

st.write("---")

# ============================================================================
# WORKOUT DURATION
# ============================================================================

st.subheader("3. Workout Duration")

col_duration = st.columns([2, 2, 2])[1]
with col_duration:
    duration_minutes = st.number_input(
        "Workout Duration (minutes)",
        min_value=1,
        max_value=300,
        value=60,
        step=5,
        help="How long did the workout take?"
    )

st.write("---")

# ============================================================================
# SAVE WORKOUT
# ============================================================================

st.subheader("4. Save Workout")

col_save, col_cancel = st.columns([1, 1])

with col_save:
    if st.button("💾 Save Old Workout", type="primary", use_container_width=True):
        try:
            # Calculate end time
            end_datetime = workout_datetime + timedelta(minutes=duration_minutes)

            # Create workout log entry
            workout_log_id = db.create_workout_log(
                workout_id=selected_workout_id,
                start_time=workout_datetime,
                status='completed'
            )

            # Build set data from logged exercises
            set_data = []

            # Get unique exercise IDs from logged sets
            logged_exercise_ids = set()
            for set_key in st.session_state['old_workout_sets'].keys():
                exercise_id, _ = set_key
                logged_exercise_ids.add(exercise_id)

            # Calculate total sets across all logged exercises
            total_sets_in_workout = sum([
                st.session_state.get(f"set_count_{eid}", 0)
                for eid in logged_exercise_ids
            ])
            avg_set_duration = (duration_minutes * 60) // total_sets_in_workout if total_sets_in_workout > 0 else 60

            for exercise_id in logged_exercise_ids:
                exercise = db.get_exercise_by_id(exercise_id)
                if not exercise:
                    continue

                # Get number of sets for this exercise
                set_count_key = f"set_count_{exercise_id}"
                num_sets = st.session_state.get(set_count_key, 0)

                for set_num in range(1, num_sets + 1):
                    set_key = (exercise_id, set_num)
                    set_info = st.session_state['old_workout_sets'].get(set_key, {})

                    weight = set_info.get('weight', 0)
                    reps = set_info.get('reps', 0)

                    # Calculate set timestamp (spread throughout workout)
                    set_offset_seconds = (set_num - 1) * avg_set_duration
                    set_timestamp = workout_datetime + timedelta(seconds=set_offset_seconds)

                    set_data.append({
                        'exercise_id': exercise_id,
                        'set_type': 'working',  # All sets are working sets for manual entry
                        'set_number': set_num,
                        'target_weight': weight,
                        'actual_weight': weight,
                        'target_reps': reps,
                        'actual_reps': reps,
                        'rest_seconds': 120,
                        'completed': True,
                        'completed_at': set_timestamp,
                        'duration_seconds': avg_set_duration,
                        'notes': 'Manually logged workout'
                    })

            # Calculate metadata and save
            if set_data:
                # Calculate metadata for all sets
                for set_item in set_data:
                    set_metadata = analysis.calculate_set_metadata(
                        actual_weight=set_item['actual_weight'],
                        actual_reps=set_item['actual_reps'],
                        duration_seconds=set_item['duration_seconds'],
                        set_type=set_item['set_type']
                    )
                    set_item.update(set_metadata)

                # Save all sets
                for set_item in set_data:
                    set_item['workout_log_id'] = workout_log_id
                    db.create_set_log(**set_item)

                # Get all saved sets for metadata calculation
                all_set_logs = db.get_set_logs_for_workout(workout_log_id)

                # Calculate workout metadata
                workout_metadata = analysis.calculate_workout_metadata(
                    start_time=workout_datetime,
                    end_time=end_datetime,
                    all_set_logs=all_set_logs,
                    exercise_ids=list(logged_exercise_ids)
                )

                # Update workout log with metadata
                db.update_workout_log(
                    workout_log_id=workout_log_id,
                    end_time=end_datetime,
                    duration_seconds=workout_metadata['duration_seconds'],
                    total_volume=workout_metadata['total_volume'],
                    total_calories=workout_metadata['total_calories'],
                    total_sets=workout_metadata['total_sets'],
                    muscle_groups_trained=workout_metadata['muscle_groups_trained'],
                    status='completed'
                )

                # Success message
                st.success("✅ Old workout logged successfully!")

                st.write("### Summary")
                col_sum1, col_sum2, col_sum3 = st.columns(3)

                with col_sum1:
                    st.metric("Date", workout_date.strftime('%Y-%m-%d'))

                with col_sum2:
                    st.metric("Total Volume", f"{workout_metadata['total_volume']:.0f} lbs")

                with col_sum3:
                    st.metric("Total Sets", workout_metadata['total_sets'])

                # Clear session state
                if 'old_workout_sets' in st.session_state:
                    del st.session_state['old_workout_sets']

                # Navigation
                st.write("")
                if st.button("📊 View History", use_container_width=True):
                    st.switch_page("pages/5_history.py")

                st.stop()
            else:
                st.error("No sets entered. Please enter at least one set for one exercise.")

        except Exception as e:
            st.error(f"Error saving workout: {str(e)}")

with col_cancel:
    if st.button("❌ Cancel", use_container_width=True):
        if 'old_workout_sets' in st.session_state:
            del st.session_state['old_workout_sets']
        st.switch_page("pages/3_workout_overview.py")

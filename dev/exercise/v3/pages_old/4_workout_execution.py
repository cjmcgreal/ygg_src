"""
Workout Execution Page
Execute a workout with dynamically generated sets and track progress
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import workflow

# Page configuration
st.set_page_config(
    page_title="Workout Execution - Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

# ============================================================================
# CHECK FOR WORKOUT SELECTION
# ============================================================================

if 'selected_workout_id' not in st.session_state:
    st.warning("⚠️ No workout selected. Please select a workout from the Workout Overview page.")
    if st.button("Go to Workout Overview"):
        st.switch_page("pages/3_workout_overview.py")
    st.stop()

# ============================================================================
# WORKOUT INITIALIZATION
# ============================================================================

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
        # Key format: (exercise_id, set_number)
        if 'set_completion' not in st.session_state:
            st.session_state['set_completion'] = {}

        st.success(f"✅ Workout '{workout_plan['workout_name']}' initialized successfully!")
        st.rerun()

    except Exception as e:
        st.error(f"Error initializing workout: {str(e)}")
        st.stop()

# ============================================================================
# WORKOUT HEADER
# ============================================================================

st.title(f"💪 {st.session_state['workout_name']}")

# Calculate elapsed time
start_time = st.session_state['start_time']
elapsed_time = datetime.now() - start_time
elapsed_minutes = int(elapsed_time.total_seconds() / 60)
elapsed_seconds = int(elapsed_time.total_seconds() % 60)

# Progress tracking
total_sets = 0
completed_sets = 0
total_working_sets = 0
completed_working_sets = 0

for exercise in st.session_state['workout_exercises']:
    for set_info in exercise['sets']:
        total_sets += 1
        if set_info['set_type'] == 'working':
            total_working_sets += 1

        set_key = (exercise['exercise_id'], set_info['set_type'], set_info['set_number'])
        if st.session_state['set_completion'].get(set_key, {}).get('completed', False):
            completed_sets += 1
            if set_info['set_type'] == 'working':
                completed_working_sets += 1

# Display header metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Elapsed Time", f"{elapsed_minutes}:{elapsed_seconds:02d}")

with col2:
    st.metric("Total Sets", f"{completed_sets} / {total_sets}")

with col3:
    st.metric("Working Sets", f"{completed_working_sets} / {total_working_sets}")

with col4:
    progress_pct = int((completed_sets / total_sets) * 100) if total_sets > 0 else 0
    st.metric("Progress", f"{progress_pct}%")

# Progress bar
st.progress(completed_sets / total_sets if total_sets > 0 else 0)

st.write("---")

# ============================================================================
# EXERCISE SECTIONS
# ============================================================================

for exercise_idx, exercise in enumerate(st.session_state['workout_exercises']):
    exercise_id = exercise['exercise_id']
    exercise_name = exercise['exercise_name']
    muscle_groups = exercise['muscle_groups'].replace(',', ', ').title()

    # Exercise header
    st.subheader(f"{exercise_idx + 1}. {exercise_name}")
    st.caption(f"Targets: {muscle_groups}")

    # Last performance data
    if exercise['last_performance']:
        last_perf = exercise['last_performance']

        col_last1, col_last2, col_last3 = st.columns(3)

        with col_last1:
            st.caption(f"📊 Last Weight/Reps: {last_perf['last_weight']} lbs × {last_perf['last_reps']} reps")

        with col_last2:
            if last_perf['last_1rm']:
                st.caption(f"💪 Last 1RM: {last_perf['last_1rm']:.1f} lbs")

        with col_last3:
            if last_perf['last_workout_date'] and pd.notna(last_perf['last_workout_date']):
                date_str = last_perf['last_workout_date'].strftime('%Y-%m-%d')
                st.caption(f"📅 Last Performed: {date_str}")
    else:
        st.caption("📊 First time performing this exercise!")

    st.write("")

    # Display sets
    for set_info in exercise['sets']:
        set_number = set_info['set_number']
        set_type = set_info['set_type']
        target_weight = set_info['target_weight']
        target_reps = set_info['target_reps']
        rest_seconds = set_info['rest_seconds']

        set_key = (exercise_id, set_type, set_number)

        # Initialize set completion data if not exists
        if set_key not in st.session_state['set_completion']:
            st.session_state['set_completion'][set_key] = {
                'completed': False,
                'completed_at': None,
                'actual_weight': target_weight,
                'actual_reps': target_reps,
                'notes': ''
            }

        # Get current set completion state
        set_state = st.session_state['set_completion'][set_key]

        # Container for each set
        with st.container():
            # Visual distinction for warmup vs working sets
            if set_type == 'warmup':
                set_label = f"🔥 Warmup Set {set_number}"
                set_color = "orange"
            else:
                set_label = f"💥 Working Set {set_number}"
                set_color = "blue"

            # Set header with checkbox
            col_check, col_details = st.columns([1, 5])

            with col_check:
                completed = st.checkbox(
                    "Done",
                    value=set_state['completed'],
                    key=f"check_{exercise_id}_{set_type}_{set_number}",
                    label_visibility="collapsed"
                )

                # Update completion state and timestamp
                if completed != set_state['completed']:
                    st.session_state['set_completion'][set_key]['completed'] = completed
                    if completed:
                        st.session_state['set_completion'][set_key]['completed_at'] = datetime.now()
                    else:
                        st.session_state['set_completion'][set_key]['completed_at'] = None
                    st.rerun()

            with col_details:
                st.markdown(f"**{set_label}**")

                # Display target weight/reps and rest time
                col_weight, col_reps, col_rest = st.columns(3)

                with col_weight:
                    st.write(f"Weight: **{target_weight} lbs**")

                with col_reps:
                    st.write(f"Reps: **{target_reps}**")

                with col_rest:
                    rest_min = rest_seconds // 60
                    rest_sec = rest_seconds % 60
                    st.write(f"Rest: **{rest_min}:{rest_sec:02d}**")

            # Expandable section for adjustments
            with st.expander("⚙️ Adjust Weight/Reps (Optional)", expanded=False):
                col_adj_weight, col_adj_reps = st.columns(2)

                with col_adj_weight:
                    actual_weight = st.number_input(
                        "Actual Weight (lbs)",
                        min_value=0.0,
                        max_value=1000.0,
                        value=float(set_state['actual_weight']),
                        step=2.5,
                        key=f"weight_{exercise_id}_{set_type}_{set_number}",
                        help="Enter actual weight if different from target"
                    )
                    st.session_state['set_completion'][set_key]['actual_weight'] = actual_weight

                with col_adj_reps:
                    actual_reps = st.number_input(
                        "Actual Reps",
                        min_value=0,
                        max_value=100,
                        value=int(set_state['actual_reps']),
                        step=1,
                        key=f"reps_{exercise_id}_{set_type}_{set_number}",
                        help="Enter actual reps if different from target"
                    )
                    st.session_state['set_completion'][set_key]['actual_reps'] = actual_reps

                # Notes input
                notes = st.text_input(
                    "Set Notes (Optional)",
                    value=set_state['notes'],
                    key=f"notes_{exercise_id}_{set_type}_{set_number}",
                    placeholder="Add any notes about this set..."
                )
                st.session_state['set_completion'][set_key]['notes'] = notes

            # Visual indicator for completed sets
            if set_state['completed']:
                st.success("✅ Completed")

        st.write("")

    # Divider between exercises
    if exercise_idx < len(st.session_state['workout_exercises']) - 1:
        st.write("---")

# ============================================================================
# COMPLETE WORKOUT BUTTON
# ============================================================================

st.write("---")
st.write("")

# Check if all working sets are completed
all_working_complete = completed_working_sets == total_working_sets

col_complete, col_cancel = st.columns([1, 1])

with col_complete:
    # Determine button text and type based on completion status
    if all_working_complete:
        button_text = "✅ Complete Workout"
        button_type = "primary"
    else:
        button_text = f"⚠️ Complete Workout Early ({completed_working_sets}/{total_working_sets} sets done)"
        button_type = "secondary"

    if st.button(button_text, type=button_type, use_container_width=True,
                 help="Log this workout as complete. Only completed sets will be saved."):
        try:
            # Show warning if not all sets complete
            if not all_working_complete:
                st.warning(f"⚠️ Logging workout with only {completed_working_sets}/{total_working_sets} working sets completed. Only completed sets will count toward progression.")

            # Gather all set data
            set_data = []
            last_timestamp = st.session_state['start_time']

            for exercise in st.session_state['workout_exercises']:
                for set_info in exercise['sets']:
                    set_key = (exercise['exercise_id'], set_info['set_type'], set_info['set_number'])
                    set_state = st.session_state['set_completion'].get(set_key, {})

                    if set_state.get('completed', False):
                        completed_at = set_state.get('completed_at', datetime.now())

                        # Calculate duration (time since last set or start)
                        duration_seconds = int((completed_at - last_timestamp).total_seconds())
                        last_timestamp = completed_at

                        # Build set data dict
                        # Use actual weight/reps if provided, otherwise use target
                        actual_weight = set_state.get('actual_weight')
                        if actual_weight is None:
                            actual_weight = set_info['target_weight']

                        actual_reps = set_state.get('actual_reps')
                        if actual_reps is None:
                            actual_reps = set_info['target_reps']

                        set_data.append({
                            'exercise_id': exercise['exercise_id'],
                            'set_type': set_info['set_type'],
                            'set_number': set_info['set_number'],
                            'target_weight': set_info['target_weight'],
                            'actual_weight': actual_weight,
                            'target_reps': set_info['target_reps'],
                            'actual_reps': actual_reps,
                            'rest_seconds': set_info['rest_seconds'],
                            'completed': True,
                            'completed_at': completed_at,
                            'duration_seconds': duration_seconds,
                            'notes': set_state.get('notes', '')
                        })

                # Call workflow to save workout
                workout_log_id = st.session_state['workout_log_id']
                workout_metadata = workflow.handle_complete_workout(workout_log_id, set_data)

                # Show success message with summary
                st.success("🎉 Workout Completed Successfully!")

                st.write("### Workout Summary")
                col_sum1, col_sum2, col_sum3 = st.columns(3)

                with col_sum1:
                    duration_min = workout_metadata['duration_seconds'] // 60
                    st.metric("Duration", f"{duration_min} minutes")

                with col_sum2:
                    st.metric("Total Volume", f"{workout_metadata['total_volume']:.0f} lbs")

                with col_sum3:
                    st.metric("Calories Burned", f"{workout_metadata['total_calories']:.1f}")

                st.write(f"**Total Sets:** {workout_metadata['total_sets']}")
                st.write(f"**Muscles Trained:** {workout_metadata['muscle_groups_trained'].replace(',', ', ').title()}")

                # Clear workout session state
                keys_to_clear = [
                    'selected_workout_id',
                    'workout_log_id',
                    'workout_name',
                    'workout_exercises',
                    'start_time',
                    'workout_initialized',
                    'set_completion'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

                # Navigation options
                st.write("")
                col_nav1, col_nav2 = st.columns(2)

                with col_nav1:
                    if st.button("📊 View History", use_container_width=True):
                        st.switch_page("pages/5_history.py")

                with col_nav2:
                    if st.button("🏠 Back to Overview", use_container_width=True):
                        st.switch_page("pages/3_workout_overview.py")

                # Stop page execution after completing workout
                st.stop()

        except Exception as e:
            st.error(f"Error completing workout: {str(e)}")

with col_cancel:
    if st.button("❌ Cancel Workout", use_container_width=True):
        # Clear workout session state
        keys_to_clear = [
            'selected_workout_id',
            'workout_log_id',
            'workout_name',
            'workout_exercises',
            'start_time',
            'workout_initialized',
            'set_completion'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        st.warning("Workout cancelled. Returning to overview...")
        st.switch_page("pages/3_workout_overview.py")

# ============================================================================
# INSTRUCTIONS
# ============================================================================

st.write("---")

with st.expander("💡 How to Use This Page", expanded=False):
    st.write("**Executing Your Workout:**")
    st.write("1. **Perform each set** according to the target weight and reps")
    st.write("2. **Check the box** when you complete a set")
    st.write("3. **Adjust weight/reps** if you used different values than the target")
    st.write("4. **Add notes** for any set if needed (optional)")
    st.write("5. **Rest** for the specified time between sets")
    st.write("6. **Complete all working sets** to enable the 'Complete Workout' button")
    st.write("")
    st.write("**Set Types:**")
    st.write("- 🔥 **Warmup Sets**: Prepare your muscles (optional to complete)")
    st.write("- 💥 **Working Sets**: Your main training sets (must complete all)")
    st.write("")
    st.write("**Tips:**")
    st.write("- You can uncheck a set if you made a mistake")
    st.write("- Your progress is automatically saved in your browser")
    st.write("- If you couldn't complete the target reps, adjust the 'Actual Reps' value")

# Footer
st.write("---")
st.caption("💪 Keep pushing! Every rep counts!")

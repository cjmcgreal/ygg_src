"""
Workout History Page
View historical workout data and track progress over time
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import workflow
import db

# Page configuration
st.set_page_config(
    page_title="Workout History - Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("📊 Workout History")
st.write("Review your workout history and track your progress")

# ============================================================================
# FILTER CONTROLS
# ============================================================================

st.subheader("Filters")

with st.form("history_filters"):
    col_date1, col_date2, col_workout, col_exercise = st.columns(4)

    with col_date1:
        start_date = st.date_input(
            "Start Date",
            value=None,
            help="Filter workouts from this date onwards"
        )

    with col_date2:
        end_date = st.date_input(
            "End Date",
            value=None,
            help="Filter workouts up to this date"
        )

    with col_workout:
        # Load all workouts for filter
        workouts_df = db.get_all_workouts()
        workout_options = ["All Workouts"] + workouts_df['name'].tolist() if not workouts_df.empty else ["All Workouts"]
        selected_workout = st.selectbox(
            "Workout",
            options=workout_options,
            help="Filter by specific workout"
        )

    with col_exercise:
        # Load all exercises for filter
        exercises_df = db.get_all_exercises()
        exercise_options = ["All Exercises"] + exercises_df['name'].tolist() if not exercises_df.empty else ["All Exercises"]
        selected_exercise = st.selectbox(
            "Exercise",
            options=exercise_options,
            help="Filter workouts containing this exercise"
        )

    # Status filter
    status_filter = st.multiselect(
        "Status",
        options=["completed", "partial", "abandoned"],
        default=["completed"],
        help="Filter by workout status"
    )

    apply_filters = st.form_submit_button("Apply Filters", use_container_width=True)

st.write("---")

# ============================================================================
# QUERY WORKOUT HISTORY
# ============================================================================

# Convert filters to appropriate format
start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None

# Get workout ID if specific workout selected
workout_id = None
if selected_workout != "All Workouts":
    workout_row = workouts_df[workouts_df['name'] == selected_workout]
    if not workout_row.empty:
        workout_id = int(workout_row.iloc[0]['id'])

# Get exercise ID if specific exercise selected
exercise_id = None
if selected_exercise != "All Exercises":
    exercise_row = exercises_df[exercises_df['name'] == selected_exercise]
    if not exercise_row.empty:
        exercise_id = int(exercise_row.iloc[0]['id'])

# Call workflow to get filtered workout history
try:
    workout_logs = workflow.get_workout_history(
        start_date=start_datetime,
        end_date=end_datetime,
        workout_id=workout_id,
        exercise_id=exercise_id
    )

    # Filter by status
    if status_filter:
        workout_logs = [log for log in workout_logs if log.get('status') in status_filter]

except Exception as e:
    st.error(f"Error loading workout history: {str(e)}")
    workout_logs = []

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

if workout_logs:
    st.subheader("Summary Statistics")

    # Calculate summary metrics
    total_workouts = len(workout_logs)
    total_volume = sum(log.get('total_volume', 0) or 0 for log in workout_logs)
    total_calories = sum(log.get('total_calories', 0) or 0 for log in workout_logs)

    # Current week summary
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    this_week_logs = [
        log for log in workout_logs
        if pd.notna(log.get('start_time')) and log['start_time'] >= week_start
    ]
    week_workouts = len(this_week_logs)

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Workouts", total_workouts)

    with col2:
        st.metric("Total Volume", f"{total_volume:,.0f} lbs")

    with col3:
        st.metric("Total Calories", f"{total_calories:,.1f}")

    with col4:
        st.metric("This Week", f"{week_workouts} workouts")

    st.write("---")

# ============================================================================
# WORKOUT LOG TABLE
# ============================================================================

st.subheader("Workout Logs")

if not workout_logs:
    st.info("No workout logs found. Complete your first workout to see it here!")
else:
    # Prepare data for display
    display_data = []

    for log in workout_logs:
        # Format duration
        duration_seconds = log.get('duration_seconds', 0) or 0
        if pd.isna(duration_seconds):
            duration_seconds = 0
        duration_minutes = int(duration_seconds / 60)

        # Format date
        start_time = log.get('start_time')
        if pd.notna(start_time):
            date_str = start_time.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = 'N/A'

        display_data.append({
            'Date': date_str,
            'Workout': log.get('workout_name', 'Unknown'),
            'Duration': f"{duration_minutes} min",
            'Volume': f"{log.get('total_volume', 0):,.0f} lbs",
            'Calories': f"{log.get('total_calories', 0):.1f}",
            'Sets': log.get('total_sets', 0),
            'Status': log.get('status', 'unknown').title(),
            'ID': log['id']  # Keep for expandable details
        })

    # Create DataFrame for display
    display_df = pd.DataFrame(display_data)

    # Sort by date descending (most recent first)
    display_df = display_df.sort_values('Date', ascending=False)

    # Display count
    st.write(f"Showing {len(display_df)} workout(s)")

    # Display table (without ID column)
    st.dataframe(
        display_df[['Date', 'Workout', 'Duration', 'Volume', 'Calories', 'Sets', 'Status']],
        use_container_width=True,
        height=400,
        hide_index=True
    )

    # ========================================================================
    # WORKOUT DETAILS EXPANSION
    # ========================================================================

    st.write("---")
    st.subheader("Workout Details")

    # Select workout to view details
    workout_dates = display_df['Date'].tolist()
    workout_names = display_df['Workout'].tolist()
    workout_ids = display_df['ID'].tolist()

    # Create display options
    detail_options = [f"{date} - {name}" for date, name in zip(workout_dates, workout_names)]

    if detail_options:
        selected_detail = st.selectbox(
            "Select workout to view details",
            options=detail_options,
            label_visibility="collapsed"
        )

        # Get selected workout ID
        selected_idx = detail_options.index(selected_detail)
        selected_workout_log_id = workout_ids[selected_idx]

        # Load set logs for this workout
        try:
            set_logs = db.get_set_logs_for_workout(selected_workout_log_id)

            if set_logs:
                with st.expander(f"📋 {selected_detail}", expanded=True):
                    # Get workout log details
                    selected_log = [log for log in workout_logs if log['id'] == selected_workout_log_id][0]

                    # Display workout summary
                    col_sum1, col_sum2, col_sum3 = st.columns(3)

                    with col_sum1:
                        duration_min = (selected_log.get('duration_seconds', 0) or 0) // 60
                        st.write(f"**Duration:** {duration_min} minutes")

                    with col_sum2:
                        st.write(f"**Volume:** {selected_log.get('total_volume', 0):,.0f} lbs")

                    with col_sum3:
                        st.write(f"**Calories:** {selected_log.get('total_calories', 0):.1f}")

                    # Display muscles trained
                    muscles = selected_log.get('muscle_groups_trained', '')
                    if muscles:
                        st.write(f"**Muscles Trained:** {muscles.replace(',', ', ').title()}")

                    # Display notes if present
                    notes = selected_log.get('notes')
                    if notes and pd.notna(notes) and notes.strip():
                        st.write(f"**Notes:** {notes}")

                    st.write("")
                    st.write("**Sets:**")

                    # Group sets by exercise
                    exercise_groups = {}
                    for set_log in set_logs:
                        ex_id = set_log['exercise_id']
                        if ex_id not in exercise_groups:
                            exercise_groups[ex_id] = []
                        exercise_groups[ex_id].append(set_log)

                    # Display sets grouped by exercise
                    for ex_id, sets in exercise_groups.items():
                        # Get exercise name
                        exercise = db.get_exercise_by_id(ex_id)
                        exercise_name = exercise['name'] if exercise else f"Exercise {ex_id}"

                        st.write(f"**{exercise_name}**")

                        # Prepare set data for display
                        set_display_data = []

                        for set_log in sets:
                            # Determine actual values, handling NaN and None
                            actual_weight = set_log.get('actual_weight')
                            target_weight = set_log.get('target_weight', 0)

                            if pd.notna(actual_weight) and actual_weight is not None:
                                weight = actual_weight
                            elif pd.notna(target_weight):
                                weight = target_weight
                            else:
                                weight = 0

                            actual_reps = set_log.get('actual_reps')
                            target_reps = set_log.get('target_reps', 0)

                            if pd.notna(actual_reps) and actual_reps is not None:
                                reps = actual_reps
                            elif pd.notna(target_reps):
                                reps = target_reps
                            else:
                                reps = 0

                            # Format 1RM (working sets only)
                            one_rm = set_log.get('one_rep_max_estimate')
                            one_rm_str = f"{one_rm:.1f}" if one_rm and pd.notna(one_rm) else "-"

                            # Volume
                            volume = set_log.get('volume', 0) or 0

                            # Completed status
                            completed = "✅" if set_log.get('completed') else "❌"

                            set_display_data.append({
                                'Set': set_log['set_number'],
                                'Type': set_log['set_type'].title(),
                                'Weight': f"{weight} lbs",
                                'Reps': int(reps),
                                '1RM Est': one_rm_str,
                                'Volume': f"{volume:.0f} lbs",
                                'Done': completed
                            })

                        # Display set table
                        set_df = pd.DataFrame(set_display_data)
                        st.dataframe(
                            set_df,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.write("")
            else:
                st.warning("No set data found for this workout.")

        except Exception as e:
            st.error(f"Error loading workout details: {str(e)}")

# ============================================================================
# EXERCISE-SPECIFIC HISTORY VIEW (OPTIONAL)
# ============================================================================

st.write("---")
st.subheader("Exercise Progression View")

# Toggle between views
view_mode = st.radio(
    "View Mode",
    options=["Workout View", "Exercise View"],
    horizontal=True,
    help="Switch between viewing by workout or by exercise"
)

if view_mode == "Exercise View":
    st.write("**Exercise Progression**")

    # Select exercise to view progression
    if not exercises_df.empty:
        exercise_names = exercises_df['name'].tolist()
        selected_prog_exercise = st.selectbox(
            "Select exercise to view progression",
            options=exercise_names,
            key="exercise_progression_select"
        )

        if selected_prog_exercise:
            # Get exercise ID
            exercise_row = exercises_df[exercises_df['name'] == selected_prog_exercise]
            prog_exercise_id = int(exercise_row.iloc[0]['id'])

            # Get exercise history
            try:
                exercise_history = db.get_exercise_history(prog_exercise_id)

                # Filter for completed working sets
                working_sets = exercise_history[
                    (exercise_history['set_type'] == 'working') &
                    (exercise_history['completed'] == True)
                ]

                if not working_sets.empty:
                    # Prepare progression data
                    progression_data = []

                    # Group by workout_log_id
                    for workout_log_id in working_sets['workout_log_id'].unique():
                        workout_sets = working_sets[working_sets['workout_log_id'] == workout_log_id]

                        # Get first set for date and weight/reps
                        first_set = workout_sets.iloc[0]

                        # Determine actual values, handling NaN and None
                        actual_weight = first_set.get('actual_weight')
                        target_weight = first_set.get('target_weight', 0)

                        if pd.notna(actual_weight) and actual_weight is not None:
                            weight = actual_weight
                        elif pd.notna(target_weight):
                            weight = target_weight
                        else:
                            weight = 0

                        actual_reps = first_set.get('actual_reps')
                        target_reps = first_set.get('target_reps', 0)

                        if pd.notna(actual_reps) and actual_reps is not None:
                            reps = actual_reps
                        elif pd.notna(target_reps):
                            reps = target_reps
                        else:
                            reps = 0

                        one_rm = first_set.get('one_rep_max_estimate')

                        date = first_set['completed_at']
                        if pd.notna(date):
                            date_str = date.strftime('%Y-%m-%d')
                        else:
                            date_str = 'N/A'

                        progression_data.append({
                            'Date': date_str,
                            'Weight': f"{weight} lbs",
                            'Reps': int(reps),
                            '1RM Est': f"{one_rm:.1f}" if one_rm and pd.notna(one_rm) else "-",
                            'Sets Completed': len(workout_sets)
                        })

                    # Create DataFrame
                    prog_df = pd.DataFrame(progression_data)

                    # Sort by date
                    prog_df = prog_df.sort_values('Date', ascending=False)

                    st.write(f"**{selected_prog_exercise} - Progression History**")
                    st.write(f"Showing {len(prog_df)} workout(s)")

                    st.dataframe(
                        prog_df,
                        use_container_width=True,
                        hide_index=True,
                        height=300
                    )

                    # Display 1RM progression summary
                    st.write("**1RM Progression Summary:**")

                    # Filter out rows with valid 1RM
                    one_rm_data = [row for row in progression_data if row['1RM Est'] != "-"]

                    if one_rm_data:
                        latest_1rm = one_rm_data[0]['1RM Est']
                        earliest_1rm = one_rm_data[-1]['1RM Est']

                        col_1rm1, col_1rm2 = st.columns(2)

                        with col_1rm1:
                            st.metric("Latest 1RM", latest_1rm)

                        with col_1rm2:
                            st.metric("Earliest 1RM", earliest_1rm)
                    else:
                        st.info("No 1RM estimates available yet.")
                else:
                    st.info(f"No completed working sets found for {selected_prog_exercise}")

            except Exception as e:
                st.error(f"Error loading exercise progression: {str(e)}")
    else:
        st.info("No exercises created yet. Create exercises to view progression.")

# ============================================================================
# INSTRUCTIONS
# ============================================================================

st.write("---")

with st.expander("💡 How to Use This Page", expanded=False):
    st.write("**Viewing Your History:**")
    st.write("1. **Apply filters** to narrow down workout logs by date, workout, exercise, or status")
    st.write("2. **View summary statistics** to track your overall progress")
    st.write("3. **Browse the workout table** to see all logged workouts")
    st.write("4. **Select a workout** to expand and view detailed set-by-set information")
    st.write("")
    st.write("**Exercise Progression View:**")
    st.write("1. **Switch to Exercise View** using the radio buttons")
    st.write("2. **Select an exercise** to see its progression over time")
    st.write("3. **Review weight, reps, and 1RM estimates** across multiple workouts")
    st.write("")
    st.write("**Tips:**")
    st.write("- Use date filters to view specific time periods (e.g., last month)")
    st.write("- Filter by exercise to see all workouts containing that movement")
    st.write("- Check 1RM progression to verify strength gains over time")

# Footer
st.write("---")
st.caption("📈 Track your progress and stay motivated!")

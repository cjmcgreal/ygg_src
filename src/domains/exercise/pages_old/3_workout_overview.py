"""
Workout Overview Page
Select a workout to execute and view workout details
"""

import streamlit as st
import pandas as pd
import workflow
import db

# Page configuration
st.set_page_config(
    page_title="Workout Overview - Exercise Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("📊 Workout Overview")
st.write("Select a workout to start your training session")

# ============================================================================
# WORKOUT SELECTION INTERFACE
# ============================================================================

# Load all workouts
workouts_df = db.get_all_workouts()

if workouts_df.empty:
    st.info("📝 No workouts available. Create your first workout in the 'Create Workout' page!")
    st.stop()

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
                # print(type(workout_details['notes']))
                if pd.isna(notes):
                    st.caption("")  # or st.caption("*No notes*") if you prefer
                elif len(notes) > 100:
                    st.caption(f"*{notes[:100]}...*")
                else:
                    st.caption(f"*{notes}*")
               # st.caption(f"*{workout_details['notes'][:100]}...*" if len(workout_details['notes']) > 100 else f"*{workout_details['notes']}*")

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

                # Navigate to workout execution page
                st.success(f"✅ Starting '{workout_details['name']}'...")
                st.switch_page("pages/4_workout_execution.py")

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

# ============================================================================
# INSTRUCTIONS
# ============================================================================

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

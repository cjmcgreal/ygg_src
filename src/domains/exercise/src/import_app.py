"""
Markdown Import UI Component
Streamlit UI for importing completed workouts from markdown files
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import db
import workflow

# Import markdown utils
from markdown_utils import parse_workout_markdown, extract_checked_sets


def render_import_workout():
    """
    Render the markdown import tab

    Allows users to:
    - Upload or paste markdown content
    - Preview parsed sets
    - Match exercises to database
    - Set workout date
    - Import completed sets to database
    """
    st.header("Import Completed Workout")
    st.caption("Import workout data from markdown files with checkboxes")

    # Input method selection
    input_method = st.radio(
        "Input Method",
        options=["Paste Text", "Upload File"],
        horizontal=True
    )

    markdown_content = ""

    if input_method == "Paste Text":
        markdown_content = st.text_area(
            "Paste markdown content",
            height=300,
            placeholder="""**Chest - Barbell Bench Press**
- Strategic Goal: 3 x 10 x 135 lb
- Goal today: 3 x 10 x 80 lb
- [x] Warmup set 1: 10 x 45 lb
- [x] Main Set 1: 10 x 80 lb
- [x] Main Set 2: 10 x 80 lb
- [ ] Main Set 3: 8 x 80 lb (not completed)"""
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload markdown file",
            type=['md', 'txt'],
            help="Upload a .md or .txt file containing your workout"
        )

        if uploaded_file:
            markdown_content = uploaded_file.read().decode('utf-8')
            st.text_area("File contents", value=markdown_content, height=200, disabled=True)

    if not markdown_content:
        st.info("Enter or upload markdown content to preview and import")
        return

    st.divider()

    # Parse and preview
    st.subheader("Preview")

    try:
        all_sets = parse_workout_markdown(markdown_content)
        checked_sets = extract_checked_sets(markdown_content)
    except Exception as e:
        st.error(f"Error parsing markdown: {str(e)}")
        return

    if not all_sets:
        st.warning("No sets found in the markdown content")
        return

    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sets Found", len(all_sets))
    with col2:
        st.metric("Completed Sets", len(checked_sets))
    with col3:
        st.metric("Skipped Sets", len(all_sets) - len(checked_sets))

    st.divider()

    # Show parsed sets
    st.subheader("Parsed Sets")

    # Group by exercise
    exercises = {}
    for s in all_sets:
        ex_name = s['exercise_name']
        if ex_name not in exercises:
            exercises[ex_name] = []
        exercises[ex_name].append(s)

    # Display each exercise
    for ex_name, sets in exercises.items():
        with st.expander(f"**{ex_name}** ({len([s for s in sets if s['completed']])} / {len(sets)} completed)"):
            for s in sets:
                status = "✅" if s['completed'] else "⬜"
                st.write(f"{status} {s['set_type'].title()} {s['set_number']}: {s['reps']} x {s['weight']} lb")

    st.divider()

    # Exercise matching
    st.subheader("Exercise Matching")
    st.caption("Match exercises in the markdown to exercises in your library")

    exercises_df = db.get_all_exercises()
    exercise_options = {row['id']: row['name'] for _, row in exercises_df.iterrows()}

    # Create mapping for each unique exercise name
    exercise_mapping = {}

    for ex_name in exercises.keys():
        # Try automatic match
        auto_match = None
        ex_lower = ex_name.lower()

        for ex_id, db_name in exercise_options.items():
            if db_name.lower() == ex_lower or ex_lower in db_name.lower() or db_name.lower() in ex_lower:
                auto_match = ex_id
                break

        col1, col2 = st.columns([1, 2])

        with col1:
            st.write(f"**{ex_name}**")

        with col2:
            options = [None] + list(exercise_options.keys())
            default_idx = 0
            if auto_match and auto_match in options:
                default_idx = options.index(auto_match)

            selected = st.selectbox(
                "Match to",
                options=options,
                index=default_idx,
                format_func=lambda x: "-- Skip --" if x is None else exercise_options.get(x, "Unknown"),
                key=f"match_{ex_name}",
                label_visibility="collapsed"
            )

            exercise_mapping[ex_name] = selected

    st.divider()

    # Workout date
    st.subheader("Workout Details")

    workout_date = st.date_input(
        "When was this workout performed?",
        value=date.today(),
        max_value=date.today()
    )

    workout_time = st.time_input(
        "Time (optional)",
        value=None
    )

    if workout_time:
        workout_datetime = datetime.combine(workout_date, workout_time)
    else:
        workout_datetime = datetime.combine(workout_date, datetime.now().time())

    st.divider()

    # Import button
    if st.button("📥 Import Completed Sets", type="primary"):
        # Build set data with matched exercise IDs
        set_data = []
        unmatched = []

        for s in checked_sets:
            ex_name = s['exercise_name']
            exercise_id = exercise_mapping.get(ex_name)

            if not exercise_id:
                unmatched.append(ex_name)
                continue

            set_data.append({
                'exercise_id': exercise_id,
                'set_number': s['set_number'],
                'set_type': s['set_type'],
                'weight': s['weight'],
                'reps': s['reps']
            })

        if not set_data:
            st.error("No sets to import. Please match at least one exercise.")
            if unmatched:
                st.warning(f"Unmatched exercises: {', '.join(set(unmatched))}")
            return

        try:
            workout_log_id = workflow.handle_log_old_workout(
                workout_id=None,
                workout_datetime=workout_datetime,
                set_data=set_data,
                notes=f"Imported from markdown ({len(set_data)} sets)"
            )

            st.success(f"Successfully imported {len(set_data)} sets! (Workout Log ID: {workout_log_id})")

            if unmatched:
                st.warning(f"Skipped unmatched exercises: {', '.join(set(unmatched))}")

        except Exception as e:
            st.error(f"Error importing workout: {str(e)}")


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    st.set_page_config(page_title="Import Workout Test", layout="wide")
    render_import_workout()

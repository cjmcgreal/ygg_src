"""
UI workflows and page rendering for Streamlit
Handles all user interactions and displays
"""

import streamlit as st
from typing import List, Optional
from datetime import datetime

from . import logic
from . import database
from . import analysis
from . import utils


def render_browser():
    """Render the procedure browser page"""
    st.title("📋 Procedures")

    # Get all procedures
    procedures = logic.get_all_procedures_with_metadata()

    if not procedures:
        st.info("No procedures yet. Create your first one!")
        if st.button("➕ Create Procedure"):
            st.session_state.page = "editor"
            st.session_state.edit_procedure_id = None
            st.rerun()
        return

    # Search and filters
    col1, col2 = st.columns([3, 1])

    with col1:
        search = st.text_input("🔍 Search procedures", key="search_input")

    with col2:
        # Get all labels
        all_labels = database.get_all_labels()
        if all_labels:
            label_names = [label['name'] for label in all_labels]
            selected_labels = st.multiselect("🏷️ Filter by labels", label_names)
            selected_label_ids = [
                label['id'] for label in all_labels
                if label['name'] in selected_labels
            ]
        else:
            selected_label_ids = []

    # Filter procedures
    filtered = logic.filter_procedures(procedures, search, selected_label_ids)

    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        ["Name", "Last Run", "Most Frequent", "Completion Rate"],
        key="sort_select"
    )

    # Apply sorting
    if sort_by == "Name":
        filtered.sort(key=lambda x: x['name'].lower())
    elif sort_by == "Last Run":
        filtered.sort(key=lambda x: x['last_run'] or datetime.min, reverse=True)
    elif sort_by == "Most Frequent":
        filtered.sort(key=lambda x: x['total_runs'], reverse=True)
    elif sort_by == "Completion Rate":
        filtered.sort(key=lambda x: x['completion_rate'], reverse=True)

    # Create button
    if st.button("➕ Create New Procedure", type="primary"):
        st.session_state.page = "editor"
        st.session_state.edit_procedure_id = None
        st.rerun()

    st.divider()

    # Display procedures
    st.write(f"**{len(filtered)}** procedure(s)")

    for proc in filtered:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])

            with col1:
                st.markdown(f"### {proc['name']}")
                if proc.get('description'):
                    st.caption(utils.truncate_text(proc['description'], 80))

                # Labels
                if proc.get('labels'):
                    label_html = " ".join([
                        f'<span style="background-color: {label["color"]}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 0.8em; margin-right: 4px;">{label["name"]}</span>'
                        for label in proc['labels']
                    ])
                    st.markdown(label_html, unsafe_allow_html=True)

            with col2:
                st.metric("Steps", proc['step_count'])
                st.metric("Runs", proc['total_runs'])

            with col3:
                st.caption("Avg Duration")
                st.write(proc['avg_duration_formatted'])
                st.caption("Completion Rate")
                st.write(f"{proc['completion_rate']:.0f}%")

            with col4:
                if st.button("▶️ Start", key=f"start_{proc['id']}"):
                    success, run_id, error = logic.start_procedure_run(proc['id'])
                    if success:
                        st.session_state.active_run_id = run_id
                        st.session_state.page = "execute"
                        st.rerun()
                    else:
                        st.error(f"Error: {error}")

                if st.button("✏️ Edit", key=f"edit_{proc['id']}"):
                    st.session_state.page = "editor"
                    st.session_state.edit_procedure_id = proc['id']
                    st.rerun()

            st.divider()


def render_execution():
    """Render the procedure execution page"""
    # Check if there's an active run
    run_id = st.session_state.get('active_run_id')

    if not run_id:
        # Check for any active run in database
        active_run = logic.get_active_run()
        if active_run:
            st.session_state.active_run_id = active_run['id']
            run_id = active_run['id']
        else:
            st.warning("No active procedure. Please start one from the browser.")
            if st.button("Go to Browser"):
                st.session_state.page = "browser"
                st.rerun()
            return

    # Get run details
    run = logic.get_run_with_details(run_id)

    if not run:
        st.error("Run not found")
        return

    # Header
    st.title(f"▶️ {run['procedure']['name']}")

    if run['procedure'].get('description'):
        st.caption(run['procedure']['description'])

    # Progress
    progress = logic.get_run_progress(run_id)
    st.progress(progress['progress_percent'] / 100)
    st.write(f"**Progress:** {progress['completed_steps']} / {progress['total_steps']} steps")

    # Elapsed time
    elapsed = utils.calculate_duration_seconds(run['start_time'])
    st.write(f"**Elapsed Time:** {utils.format_duration(elapsed)}")

    st.divider()

    # Steps
    for i, step in enumerate(run['steps']):
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                # Step description
                if step['completed']:
                    st.markdown(f"~~{i+1}. {step['description']}~~")
                else:
                    st.markdown(f"**{i+1}. {step['description']}**")

                # Step notes
                if step.get('run_step_notes'):
                    st.caption(f"📝 {step['run_step_notes']}")

            with col2:
                if not step['completed']:
                    if st.button("✓ Done", key=f"complete_{step['id']}"):
                        logic.complete_step_in_run(run_id, step['id'])
                        st.rerun()
                else:
                    st.success("✓")

        st.divider()

    # Actions
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("✅ Complete Run", type="primary"):
            logic.finish_run(run_id, status="completed")
            st.session_state.active_run_id = None
            st.success("Procedure completed!")
            st.balloons()
            if st.button("Back to Browser"):
                st.session_state.page = "browser"
                st.rerun()

    with col2:
        if st.button("❌ Cancel Run"):
            logic.finish_run(run_id, status="cancelled")
            st.session_state.active_run_id = None
            st.warning("Run cancelled")
            if st.button("Back to Browser"):
                st.session_state.page = "browser"
                st.rerun()


def render_history():
    """Render the run history page"""
    st.title("📜 Run History")

    # Get all runs
    runs = logic.get_all_runs_with_details()

    if not runs:
        st.info("No runs yet. Start executing procedures to see history!")
        return

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        # Get unique procedure names
        all_procedures = database.get_all_procedures()
        proc_names = ["All"] + [proc['name'] for _, proc in all_procedures.iterrows()]
        selected_proc = st.selectbox("Filter by Procedure", proc_names)

    with col2:
        status_options = ["All", "completed", "cancelled", "in_progress"]
        selected_status = st.selectbox("Filter by Status", status_options)

    with col3:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Today", "This Week", "This Month"]
        )

    # Apply filters
    filtered_runs = runs

    if selected_proc != "All":
        filtered_runs = [r for r in filtered_runs if r['procedure']['name'] == selected_proc]

    if selected_status != "All":
        filtered_runs = [r for r in filtered_runs if r['status'] == selected_status]

    # Date filtering
    if date_range == "Today":
        today = datetime.now().date()
        filtered_runs = [r for r in filtered_runs if r['start_time'].date() == today]
    elif date_range == "This Week":
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        filtered_runs = [r for r in filtered_runs if r['start_time'] >= week_ago]
    elif date_range == "This Month":
        from datetime import timedelta
        month_ago = datetime.now() - timedelta(days=30)
        filtered_runs = [r for r in filtered_runs if r['start_time'] >= month_ago]

    st.write(f"**{len(filtered_runs)}** run(s)")

    st.divider()

    # Display runs
    for run in filtered_runs:
        with st.expander(
            f"{run['procedure']['name']} - {utils.format_datetime(run['start_time'], '%Y-%m-%d %H:%M')} - {run['status']}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Start:** {utils.format_datetime(run['start_time'])}")
                st.write(f"**Status:** {run['status']}")

            with col2:
                st.write(f"**Duration:** {run['duration_formatted']}")
                if run.get('notes'):
                    st.write(f"**Notes:** {run['notes']}")

            # Show steps
            if st.checkbox("Show Steps", key=f"show_steps_{run['id']}"):
                for step in run['steps']:
                    status_icon = "✓" if step['completed'] else "○"
                    st.write(f"{status_icon} {step['description']}")


def render_analytics():
    """Render the analytics dashboard"""
    st.title("📊 Analytics")

    # Overall stats
    stats = analysis.get_overall_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Procedures", stats['total_procedures'])

    with col2:
        st.metric("Total Runs", stats['total_runs'])

    with col3:
        st.metric("Runs This Week", stats['runs_this_week'])

    with col4:
        st.metric("Completion Rate", f"{stats['overall_completion_rate']:.1f}%")

    st.divider()

    # Most frequent procedures
    st.subheader("Most Frequently Run Procedures")
    frequent = analysis.get_most_frequent_procedures(limit=5)

    if frequent:
        for proc in frequent:
            st.write(f"**{proc['name']}** - {proc['run_count']} runs")
    else:
        st.info("No data yet")

    st.divider()

    # Completion rates by procedure
    st.subheader("Completion Rates by Procedure")
    completion_rates = analysis.get_completion_rate_by_procedure()

    if completion_rates:
        # Use plotly for better visualization
        import plotly.express as px

        df_rates = {
            'Procedure': [p['name'] for p in completion_rates],
            'Completion Rate (%)': [p['completion_rate'] for p in completion_rates]
        }

        fig = px.bar(df_rates, x='Completion Rate (%)', y='Procedure', orientation='h')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet")


def render_editor():
    """Render the procedure editor (create/update)"""
    edit_id = st.session_state.get('edit_procedure_id')

    if edit_id:
        st.title("✏️ Edit Procedure")
        procedure = database.get_procedure_by_id(edit_id)
        existing_steps = database.get_steps_for_procedure(edit_id)

        default_name = procedure['name']
        default_desc = procedure.get('description', '')
        default_steps = [step['description'] for step in existing_steps]
    else:
        st.title("➕ Create Procedure")
        default_name = ""
        default_desc = ""
        default_steps = [""]

    # Form
    name = st.text_input("Procedure Name*", value=default_name)
    description = st.text_area("Description (optional)", value=default_desc)

    st.subheader("Steps")

    # Initialize steps in session state if not present
    if 'editor_steps' not in st.session_state:
        st.session_state.editor_steps = default_steps.copy()

    # Display steps
    for i, step_text in enumerate(st.session_state.editor_steps):
        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            new_text = st.text_input(
                f"Step {i+1}",
                value=step_text,
                key=f"step_{i}",
                label_visibility="collapsed"
            )
            st.session_state.editor_steps[i] = new_text

        with col2:
            if len(st.session_state.editor_steps) > 1:
                if st.button("🗑️", key=f"delete_{i}"):
                    st.session_state.editor_steps.pop(i)
                    st.rerun()

        with col3:
            if i > 0:
                if st.button("⬆️", key=f"up_{i}"):
                    st.session_state.editor_steps[i], st.session_state.editor_steps[i-1] = \
                        st.session_state.editor_steps[i-1], st.session_state.editor_steps[i]
                    st.rerun()

    # Add step button
    if st.button("➕ Add Step"):
        st.session_state.editor_steps.append("")
        st.rerun()

    st.divider()

    # Actions
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("💾 Save", type="primary"):
            # Filter out empty steps
            steps = [s.strip() for s in st.session_state.editor_steps if s.strip()]

            if edit_id:
                # Update
                success, error = logic.update_procedure_with_steps(
                    edit_id, name, description, steps
                )
                if success:
                    st.success("Procedure updated!")
                    del st.session_state.editor_steps
                    st.session_state.page = "browser"
                    st.rerun()
                else:
                    st.error(f"Error: {error}")
            else:
                # Create
                success, proc_id, error = logic.create_procedure_with_steps(
                    name, description, steps
                )
                if success:
                    st.success("Procedure created!")
                    del st.session_state.editor_steps
                    st.session_state.page = "browser"
                    st.rerun()
                else:
                    st.error(f"Error: {error}")

    with col2:
        if st.button("Cancel"):
            del st.session_state.editor_steps
            st.session_state.page = "browser"
            st.rerun()

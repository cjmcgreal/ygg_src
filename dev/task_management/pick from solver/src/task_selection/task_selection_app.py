"""
Streamlit UI Layer for Task Selection System

This module implements the complete 4-tab Streamlit interface for the task
selection algorithm prototype. It provides the user-facing interface for:
- Tab 1: Task Management - CRUD operations for tasks
- Tab 2: Bandwidth Allocation - Time allocation and domain preferences with metadata calculator
- Tab 3: Solver Run - Algorithm execution and results display
- Tab 4: Solver Output Details - Detailed explanations and metrics

Key responsibilities:
- Render all UI components using Streamlit widgets
- Manage session state for persistence across tab switches
- Call workflow layer functions for backend operations
- Display validation errors and success messages
- Provide visual feedback with domain color coding
- Format data for user-friendly display
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path to import sibling modules
sys.path.insert(0, os.path.dirname(__file__))

from task_selection_workflow import (
    create_task,
    update_task,
    delete_task,
    get_all_tasks,
    get_all_domains,
    get_domain_names,
    run_solver,
    save_solver_run,
    get_solver_run_history,
    get_solver_run_details
)

from task_selection_logic import (
    calculate_time_breakdown,
    validate_bandwidth_allocation
)


# ==============================================================================
# SESSION STATE MANAGEMENT
# ==============================================================================

def initialize_session_state():
    """
    Initialize Streamlit session state variables.

    Session state maintains data across tab switches and interactions.
    This function ensures all required variables exist before use.

    Session state variables:
    - current_solver_results: Selected tasks DataFrame from most recent solver run
    - current_explanation: Explanation list from most recent solver run
    - current_metrics: Metrics dictionary from most recent solver run
    - last_run_timestamp: Timestamp of most recent solver run
    - available_time: Total available time in story points
    - domain_preferences: Dictionary of domain percentages
    - selected_algorithm: Currently selected algorithm name
    - points_to_hours_ratio: Conversion ratio for metadata calculator
    """
    # Solver results
    if 'current_solver_results' not in st.session_state:
        st.session_state.current_solver_results = None

    if 'current_explanation' not in st.session_state:
        st.session_state.current_explanation = []

    if 'current_metrics' not in st.session_state:
        st.session_state.current_metrics = {}

    if 'last_run_timestamp' not in st.session_state:
        st.session_state.last_run_timestamp = None

    # Bandwidth allocation settings
    if 'available_time' not in st.session_state:
        st.session_state.available_time = 40.0

    if 'domain_preferences' not in st.session_state:
        st.session_state.domain_preferences = {}

    # Algorithm selection
    if 'selected_algorithm' not in st.session_state:
        st.session_state.selected_algorithm = 'Greedy'

    # Metadata calculator settings
    if 'points_to_hours_ratio' not in st.session_state:
        st.session_state.points_to_hours_ratio = 2.0


# ==============================================================================
# TAB 1: TASK MANAGEMENT
# ==============================================================================

def render_tab_task_management():
    """
    Render Tab 1: Task Management interface with CRUD operations.

    Layout:
    - Section 1: "Add New Task" form with all task fields
    - Section 2: "Existing Tasks" table with edit/delete actions
    - Section 3: Domain filter for table

    Features:
    - Create tasks with validation
    - View all tasks in sortable table
    - Filter tasks by domain
    - Edit existing tasks
    - Delete tasks with confirmation
    - Color-coded domain display
    """
    st.header("📋 Task Management")
    st.write("Create, view, update, and delete tasks in your backlog.")

    # Load domain names for dropdown
    domain_names = get_domain_names()

    if len(domain_names) == 0:
        st.error("No domains available. Please ensure domains.csv is properly configured.")
        return

    # -------------------------------------------------------------------------
    # Section 1: Add New Task Form
    # -------------------------------------------------------------------------
    st.subheader("➕ Add New Task")

    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            new_title = st.text_input(
                "Task Title*",
                placeholder="e.g., Implement user authentication",
                help="Brief, descriptive name for the task"
            )

            new_domain = st.selectbox(
                "Domain*",
                options=domain_names,
                help="Categorization for this task"
            )

            new_effort = st.number_input(
                "Effort (Story Points)*",
                min_value=0.1,
                value=5.0,
                step=0.5,
                help="Relative effort estimate (1=small, 5=medium, 13=large)"
            )

            new_priority = st.number_input(
                "Priority*",
                min_value=1,
                value=1,
                step=1,
                help="Priority ranking (1=highest priority)"
            )

        with col2:
            new_description = st.text_area(
                "Description",
                placeholder="Optional detailed description of the task",
                height=100,
                help="Additional context and details"
            )

            new_project = st.text_input(
                "Project Parent",
                placeholder="e.g., authentication_project (optional)",
                help="Optional grouping label for related tasks"
            )

            new_value = st.number_input(
                "Value*",
                min_value=0.1,
                value=8.0,
                step=0.5,
                help="Numeric score representing task importance/value"
            )

        # Form submit buttons
        col_submit, col_reset = st.columns([1, 4])
        with col_submit:
            submit_button = st.form_submit_button("Add Task", type="primary")

        if submit_button:
            # Call workflow to create task
            success, message, task_id = create_task(
                title=new_title,
                description=new_description,
                domain=new_domain,
                project_parent=new_project,
                effort=new_effort,
                value=new_value,
                priority=new_priority
            )

            if success:
                st.success(f"✅ {message}")
                st.rerun()  # Refresh to show new task in table
            else:
                st.error(f"❌ {message}")

    st.divider()

    # -------------------------------------------------------------------------
    # Section 2: Existing Tasks Table
    # -------------------------------------------------------------------------
    st.subheader("📊 Existing Tasks")

    # Load all tasks
    tasks_df = get_all_tasks()

    if len(tasks_df) == 0:
        st.info("No tasks yet. Add your first task using the form above.")
        return

    # Domain filter
    st.write("**Filter by Domain:**")
    filter_domains = st.multiselect(
        "Select domains to display (leave empty to show all)",
        options=domain_names,
        default=[],
        label_visibility="collapsed"
    )

    # Apply filter if selected
    if len(filter_domains) > 0:
        display_tasks_df = tasks_df[tasks_df['domain'].isin(filter_domains)].copy()
    else:
        display_tasks_df = tasks_df.copy()

    if len(display_tasks_df) == 0:
        st.info("No tasks match the selected domain filter.")
        return

    st.write(f"Showing {len(display_tasks_df)} of {len(tasks_df)} tasks")

    # Display tasks in a data editor for easier viewing
    # Note: Using st.dataframe for read-only display with better formatting
    display_columns = ['id', 'title', 'domain', 'project_parent', 'effort', 'value', 'priority']
    st.dataframe(
        display_tasks_df[display_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "title": st.column_config.TextColumn("Title", width="large"),
            "domain": st.column_config.TextColumn("Domain", width="medium"),
            "project_parent": st.column_config.TextColumn("Project", width="medium"),
            "effort": st.column_config.NumberColumn("Effort (sp)", width="small", format="%.1f"),
            "value": st.column_config.NumberColumn("Value", width="small", format="%.1f"),
            "priority": st.column_config.NumberColumn("Priority", width="small")
        }
    )

    # -------------------------------------------------------------------------
    # Section 3: Edit/Delete Actions
    # -------------------------------------------------------------------------
    st.subheader("✏️ Edit or Delete Task")

    col_action, col_task = st.columns([1, 2])

    with col_action:
        action = st.radio("Action:", ["Edit Task", "Delete Task"])

    with col_task:
        task_ids = display_tasks_df['id'].tolist()
        task_options = [f"ID {task_id}: {display_tasks_df[display_tasks_df['id']==task_id]['title'].values[0]}"
                       for task_id in task_ids]
        selected_task_option = st.selectbox("Select Task:", task_options)

        # Extract task ID from selection
        selected_task_id = int(selected_task_option.split(":")[0].replace("ID ", ""))

    if action == "Edit Task":
        # Get the selected task data
        task_row = tasks_df[tasks_df['id'] == selected_task_id].iloc[0]

        st.write("**Update Task Fields:**")
        with st.form("edit_task_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_title = st.text_input("Title", value=task_row['title'])
                edit_domain = st.selectbox("Domain", options=domain_names,
                                          index=domain_names.index(task_row['domain']) if task_row['domain'] in domain_names else 0)
                edit_effort = st.number_input("Effort (Story Points)", min_value=0.1, value=float(task_row['effort']), step=0.5)
                edit_priority = st.number_input("Priority", min_value=1, value=int(task_row['priority']), step=1)

            with col2:
                edit_description = st.text_area("Description", value=task_row['description'], height=100)
                edit_project = st.text_input("Project Parent", value=task_row['project_parent'])
                edit_value = st.number_input("Value", min_value=0.1, value=float(task_row['value']), step=0.5)

            update_button = st.form_submit_button("Update Task", type="primary")

            if update_button:
                success, message = update_task(
                    task_id=selected_task_id,
                    title=edit_title,
                    description=edit_description,
                    domain=edit_domain,
                    project_parent=edit_project,
                    effort=edit_effort,
                    value=edit_value,
                    priority=edit_priority
                )

                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

    else:  # Delete Task
        task_row = tasks_df[tasks_df['id'] == selected_task_id].iloc[0]
        st.warning(f"⚠️ You are about to delete: **{task_row['title']}**")
        st.write("This action cannot be undone.")

        if st.button("🗑️ Confirm Delete", type="secondary"):
            success, message = delete_task(selected_task_id)

            if success:
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")


# ==============================================================================
# TAB 2: BANDWIDTH ALLOCATION
# ==============================================================================

def render_tab_bandwidth_allocation():
    """
    Render Tab 2: Bandwidth Allocation interface with two-column layout.

    Layout:
    - Left column: Available time input and domain preference sliders
    - Right column: Metadata calculator showing time breakdown

    Features:
    - Set total available time in story points
    - Allocate percentage preferences across domains
    - Real-time validation of 100% sum requirement
    - Metadata calculator converts story points to hours
    - Configurable conversion ratio
    - Domain color coding for visual distinction
    """
    st.header("⏱️ Bandwidth Allocation")
    st.write("Define your available time and domain preferences for the solver algorithm.")

    # Load domains
    domains_df = get_all_domains()

    if len(domains_df) == 0:
        st.error("No domains available. Please ensure domains.csv is properly configured.")
        return

    # Create two-column layout
    col_left, col_right = st.columns([1, 1])

    # -------------------------------------------------------------------------
    # Left Column: Input Your Allocation
    # -------------------------------------------------------------------------
    with col_left:
        st.subheader("📊 Input Your Allocation")

        # Available time input
        available_time = st.number_input(
            "Available Time (story points)",
            min_value=0.1,
            value=st.session_state.available_time,
            step=1.0,
            help="Total time capacity you have available for task selection. Story points are relative effort estimates."
        )

        # Update session state
        st.session_state.available_time = available_time

        st.write("**Domain Preferences (%)**")
        st.caption("Allocate your available time across domains. Must sum to exactly 100%.")

        # Initialize domain preferences if empty
        if len(st.session_state.domain_preferences) == 0:
            # Default: distribute evenly across domains
            num_domains = len(domains_df)
            default_pct = 100.0 / num_domains
            for _, domain_row in domains_df.iterrows():
                st.session_state.domain_preferences[domain_row['name']] = default_pct

        # Create sliders for each domain
        domain_prefs = {}
        for _, domain_row in domains_df.iterrows():
            domain_name = domain_row['name']
            domain_color = domain_row['color']

            # Get current value from session state
            current_value = st.session_state.domain_preferences.get(domain_name, 0.0)

            # Create slider with domain color as label
            pref_value = st.slider(
                f"{domain_name}",
                min_value=0.0,
                max_value=100.0,
                value=float(current_value),
                step=1.0,
                help=f"Percentage of time to allocate to {domain_name} domain"
            )

            domain_prefs[domain_name] = pref_value

        # Update session state
        st.session_state.domain_preferences = domain_prefs

        # Calculate total and validate
        total_pct = sum(domain_prefs.values())

        st.divider()

        # Display total allocation with validation
        if abs(total_pct - 100.0) <= 0.01:
            st.success(f"✅ Total allocation: **{total_pct:.1f}%** (Valid)")
        else:
            st.error(f"⚠️ Total allocation: **{total_pct:.1f}%** (Must equal 100%)")
            st.caption("Adjust the sliders above so the total equals exactly 100%")

    # -------------------------------------------------------------------------
    # Right Column: Metadata Calculator
    # -------------------------------------------------------------------------
    with col_right:
        st.subheader("🧮 Metadata Calculator")
        st.write("View your time allocation broken down by domain.")

        # Conversion ratio input
        points_to_hours = st.number_input(
            "Story points to hours ratio",
            min_value=0.1,
            value=st.session_state.points_to_hours_ratio,
            step=0.1,
            help="How many hours does 1 story point represent? Default: 1sp = 2hrs"
        )

        st.session_state.points_to_hours_ratio = points_to_hours

        st.write("**Time Breakdown by Domain:**")

        # Calculate breakdown
        breakdown = calculate_time_breakdown(
            available_time,
            st.session_state.domain_preferences,
            points_to_hours
        )

        # Display breakdown for each domain with color coding
        breakdown_data = []
        for _, domain_row in domains_df.iterrows():
            domain_name = domain_row['name']
            domain_color = domain_row['color']

            if domain_name in breakdown:
                info = breakdown[domain_name]
                breakdown_data.append({
                    'Domain': domain_name,
                    'Percentage': f"{info['percentage']:.1f}%",
                    'Story Points': f"{info['story_points']:.2f}sp",
                    'Hours': f"{info['hours']:.2f}hrs"
                })

        # Display as table
        if len(breakdown_data) > 0:
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(
                breakdown_df,
                use_container_width=True,
                hide_index=True
            )

            # Total summary
            total_sp = sum([breakdown[d]['story_points'] for d in breakdown.keys()])
            total_hrs = sum([breakdown[d]['hours'] for d in breakdown.keys()])

            st.info(f"**Total: {total_sp:.2f}sp = {total_hrs:.2f}hrs**")

        st.divider()

        st.caption("💡 **Tip:** Adjust your domain preferences to reflect where you want to focus your effort. "
                  "The solver will respect these preferences when selecting tasks.")


# ==============================================================================
# TAB 3: SOLVER RUN
# ==============================================================================

def render_tab_solver_run():
    """
    Render Tab 3: Solver Run interface for algorithm execution.

    Layout:
    - Section 1: Algorithm selection with explanatory expanders
    - Section 2: Run parameters summary (read-only)
    - Section 3: Run solver button
    - Section 4: Results summary (appears after run)

    Features:
    - Select from three algorithms (greedy, weighted, knapsack)
    - View algorithm explanations
    - Display current parameters
    - Execute solver with loading indicator
    - Display selected tasks in table
    - Show metrics (effort, value, utilization)
    - Visualize domain breakdown
    - Save successful runs
    """
    st.header("🚀 Solver Run")
    st.write("Select an algorithm and run the solver to find optimal task selection.")

    # -------------------------------------------------------------------------
    # Section 1: Algorithm Selection
    # -------------------------------------------------------------------------
    st.subheader("🔧 Algorithm Selection")

    algorithm = st.radio(
        "Choose optimization algorithm:",
        ["Greedy", "Weighted", "Knapsack"],
        index=["Greedy", "Weighted", "Knapsack"].index(st.session_state.selected_algorithm),
        horizontal=True
    )

    st.session_state.selected_algorithm = algorithm

    # Algorithm explanations
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("ℹ️ Greedy Algorithm"):
            st.write("""
            **How it works:**
            - Calculates value-to-effort ratio for each task
            - Selects tasks with highest ratio first
            - Continues until no more tasks fit

            **Best for:**
            - Maximizing immediate return on time
            - Simple, fast optimization
            - When all tasks are equally prioritized
            """)

    with col2:
        with st.expander("ℹ️ Weighted Algorithm"):
            st.write("""
            **How it works:**
            - Scores tasks based on multiple factors:
              - Domain preference (higher preference = higher score)
              - Task value (higher value = higher score)
              - Priority (lower number = higher score)
              - Effort (lower effort = higher score)
            - Selects highest-scoring tasks first

            **Best for:**
            - Balancing multiple objectives
            - Respecting task priorities
            - Aligning with domain preferences
            """)

    with col3:
        with st.expander("ℹ️ Knapsack Algorithm"):
            st.write("""
            **How it works:**
            - Uses dynamic programming for optimal solution
            - Adjusts task values by domain preference and priority
            - Finds mathematically optimal task combination
            - May be slower for large task sets

            **Best for:**
            - Finding provably optimal selection
            - Complex constraint scenarios
            - When performance allows
            """)

    st.divider()

    # -------------------------------------------------------------------------
    # Section 2: Run Parameters Summary
    # -------------------------------------------------------------------------
    st.subheader("📋 Run Parameters")

    # Validate bandwidth allocation
    is_valid, error_msg, total_pct = validate_bandwidth_allocation(st.session_state.domain_preferences)

    if not is_valid:
        st.error(f"⚠️ Invalid bandwidth allocation: {error_msg}")
        st.info("👈 Please go to **Tab 2: Bandwidth Allocation** to fix domain preferences")
        return

    # Display current parameters
    col_param1, col_param2, col_param3 = st.columns(3)

    with col_param1:
        st.metric("Available Time", f"{st.session_state.available_time:.1f}sp")

    with col_param2:
        st.metric("Algorithm", algorithm)

    with col_param3:
        st.metric("Domain Preferences", f"{len(st.session_state.domain_preferences)} domains")

    with st.expander("View Domain Preferences Details"):
        for domain, pct in st.session_state.domain_preferences.items():
            st.write(f"- **{domain}**: {pct:.1f}%")

    st.divider()

    # -------------------------------------------------------------------------
    # Section 3: Run Solver
    # -------------------------------------------------------------------------
    st.subheader("▶️ Execute Solver")

    run_button = st.button("🚀 Run Solver", type="primary", use_container_width=True)

    if run_button:
        with st.spinner(f"Running {algorithm} solver..."):
            # Call workflow to run solver
            selected_tasks, explanation, metrics, error = run_solver(
                available_time=st.session_state.available_time,
                domain_preferences=st.session_state.domain_preferences,
                algorithm=algorithm.lower()
            )

            if error is not None:
                st.error(f"❌ Solver error: {error}")
                return

            # Store results in session state
            st.session_state.current_solver_results = selected_tasks
            st.session_state.current_explanation = explanation
            st.session_state.current_metrics = metrics
            st.session_state.last_run_timestamp = pd.Timestamp.now()

            st.success("✅ Solver completed successfully!")
            st.rerun()

    # -------------------------------------------------------------------------
    # Section 4: Results Summary (if available)
    # -------------------------------------------------------------------------
    if st.session_state.current_solver_results is not None:
        st.divider()
        st.subheader("📊 Results Summary")

        selected_df = st.session_state.current_solver_results
        metrics = st.session_state.current_metrics

        # Metrics display
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            st.metric(
                "Tasks Selected",
                metrics.get('num_tasks', 0)
            )

        with col_m2:
            st.metric(
                "Total Effort",
                f"{metrics.get('total_effort', 0):.1f}sp",
                delta=f"of {st.session_state.available_time:.1f}sp"
            )

        with col_m3:
            st.metric(
                "Total Value",
                f"{metrics.get('total_value', 0):.1f}"
            )

        with col_m4:
            st.metric(
                "Utilization",
                f"{metrics.get('utilization_pct', 0):.1f}%"
            )

        # Selected tasks table
        st.write("**Selected Tasks:**")

        if len(selected_df) > 0:
            display_cols = ['id', 'title', 'domain', 'effort', 'value', 'priority']
            st.dataframe(
                selected_df[display_cols],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "title": "Title",
                    "domain": "Domain",
                    "effort": st.column_config.NumberColumn("Effort (sp)", format="%.1f"),
                    "value": st.column_config.NumberColumn("Value", format="%.1f"),
                    "priority": "Priority"
                }
            )

            # Domain breakdown
            st.write("**Domain Breakdown:**")
            domain_breakdown = selected_df.groupby('domain')['effort'].sum().reset_index()
            domain_breakdown.columns = ['Domain', 'Effort Used (sp)']

            # Add allocated effort for comparison
            domain_breakdown['Allocated (sp)'] = domain_breakdown['Domain'].apply(
                lambda d: (st.session_state.domain_preferences.get(d, 0) / 100.0) * st.session_state.available_time
            )

            st.dataframe(
                domain_breakdown,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Domain": "Domain",
                    "Effort Used (sp)": st.column_config.NumberColumn("Used (sp)", format="%.2f"),
                    "Allocated (sp)": st.column_config.NumberColumn("Allocated (sp)", format="%.2f")
                }
            )
        else:
            st.info("No tasks were selected by the solver within the given constraints.")

        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            if st.button("💾 Save This Run"):
                # Extract task IDs
                task_ids = selected_df['id'].tolist() if len(selected_df) > 0 else []

                # Save run
                success, run_id = save_solver_run(
                    available_time=st.session_state.available_time,
                    domain_preferences=st.session_state.domain_preferences,
                    algorithm=st.session_state.selected_algorithm.lower(),
                    selected_task_ids=task_ids,
                    metrics=metrics,
                    explanation=st.session_state.current_explanation
                )

                if success:
                    st.success(f"✅ Run saved with ID: {run_id}")
                else:
                    st.error("❌ Failed to save run")

        with col_btn2:
            if st.button("📄 View Detailed Explanation"):
                st.info("👉 Switch to **Tab 4: Solver Output Details** to view the full explanation")

        with col_btn3:
            st.caption(f"Last run: {st.session_state.last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


# ==============================================================================
# TAB 4: SOLVER OUTPUT DETAILS
# ==============================================================================

def render_tab_solver_output_details():
    """
    Render Tab 4: Solver Output Details with comprehensive explanations.

    Layout:
    - Section 1: Run overview (timestamp, algorithm, parameters)
    - Section 2: Algorithm decision process (step-by-step explanation)
    - Section 3: Task selection rationale (per-task justification)
    - Section 4: Constraint satisfaction (domain and time constraints)
    - Section 5: Performance metrics (execution time, efficiency)

    Features:
    - Display current solver run details
    - Show step-by-step decision process
    - Explain task selections and rejections
    - Visualize constraint satisfaction
    - Display performance metrics
    - Compare with historical runs (future enhancement)
    """
    st.header("📄 Solver Output Details")

    # Check if solver results exist
    if st.session_state.current_solver_results is None:
        st.info("ℹ️ No solver run available. Please run the solver in **Tab 3: Solver Run** first.")
        return

    selected_df = st.session_state.current_solver_results
    explanation = st.session_state.current_explanation
    metrics = st.session_state.current_metrics

    # -------------------------------------------------------------------------
    # Section 1: Run Overview
    # -------------------------------------------------------------------------
    st.subheader("📋 Run Overview")

    col_overview1, col_overview2, col_overview3 = st.columns(3)

    with col_overview1:
        st.write("**Algorithm Used:**")
        st.write(f"{st.session_state.selected_algorithm}")

    with col_overview2:
        st.write("**Available Time:**")
        st.write(f"{st.session_state.available_time:.1f} story points")

    with col_overview3:
        st.write("**Run Timestamp:**")
        if st.session_state.last_run_timestamp:
            st.write(st.session_state.last_run_timestamp.strftime('%Y-%m-%d %H:%M:%S'))

    with st.expander("View Domain Preferences"):
        for domain, pct in st.session_state.domain_preferences.items():
            st.write(f"- **{domain}**: {pct:.1f}%")

    st.divider()

    # -------------------------------------------------------------------------
    # Section 2: Algorithm Decision Process
    # -------------------------------------------------------------------------
    st.subheader("🧠 Algorithm Decision Process")
    st.write("Step-by-step explanation of how the algorithm made its decisions:")

    with st.expander("View Full Decision Log", expanded=True):
        for i, line in enumerate(explanation):
            # Format summary lines differently
            if line.startswith("===") or line.startswith("Total") or line.startswith("Tasks"):
                st.markdown(f"**{line}**")
            elif line.startswith("Selected"):
                st.success(f"✅ {line}")
            elif line.startswith("Rejected"):
                st.warning(f"❌ {line}")
            else:
                st.write(line)

    st.divider()

    # -------------------------------------------------------------------------
    # Section 3: Task Selection Rationale
    # -------------------------------------------------------------------------
    st.subheader("💡 Task Selection Rationale")

    if len(selected_df) > 0:
        st.write(f"**{len(selected_df)} tasks were selected:**")

        for _, task in selected_df.iterrows():
            with st.expander(f"✅ {task['title']} (ID: {task['id']})"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Domain:** {task['domain']}")
                    st.write(f"**Effort:** {task['effort']:.1f} story points")

                with col2:
                    st.write(f"**Value:** {task['value']:.1f}")
                    st.write(f"**Priority:** {task['priority']}")

                with col3:
                    # Calculate value-to-effort ratio
                    ratio = task['value'] / task['effort'] if task['effort'] > 0 else 0
                    st.write(f"**Value/Effort:** {ratio:.2f}")

                st.caption(f"**Description:** {task['description'] if task['description'] else 'No description provided'}")
    else:
        st.info("No tasks were selected by the solver.")

    st.divider()

    # -------------------------------------------------------------------------
    # Section 4: Constraint Satisfaction
    # -------------------------------------------------------------------------
    st.subheader("✓ Constraint Satisfaction")
    st.write("Verification that all constraints were satisfied:")

    # Time constraint
    st.write("**Time Constraint:**")
    col_time1, col_time2, col_time3 = st.columns(3)

    with col_time1:
        st.metric("Available Time", f"{st.session_state.available_time:.1f}sp")

    with col_time2:
        st.metric("Time Used", f"{metrics.get('total_effort', 0):.1f}sp")

    with col_time3:
        st.metric("Remaining", f"{st.session_state.available_time - metrics.get('total_effort', 0):.1f}sp")

    # Progress bar for time utilization
    utilization = metrics.get('utilization_pct', 0)
    st.progress(min(utilization / 100.0, 1.0))
    st.caption(f"Time utilization: {utilization:.1f}%")

    st.write("**Domain Constraints:**")

    # Calculate domain usage
    if len(selected_df) > 0:
        domain_usage = selected_df.groupby('domain')['effort'].sum().to_dict()
    else:
        domain_usage = {}

    # Create constraint satisfaction table
    constraint_data = []
    for domain, pref_pct in st.session_state.domain_preferences.items():
        allocated_sp = (pref_pct / 100.0) * st.session_state.available_time
        used_sp = domain_usage.get(domain, 0.0)
        domain_util_pct = (used_sp / allocated_sp * 100.0) if allocated_sp > 0 else 0.0

        constraint_data.append({
            'Domain': domain,
            'Preference': f"{pref_pct:.1f}%",
            'Allocated': f"{allocated_sp:.2f}sp",
            'Used': f"{used_sp:.2f}sp",
            'Utilization': f"{domain_util_pct:.1f}%"
        })

    constraint_df = pd.DataFrame(constraint_data)
    st.dataframe(constraint_df, use_container_width=True, hide_index=True)

    st.divider()

    # -------------------------------------------------------------------------
    # Section 5: Performance Metrics
    # -------------------------------------------------------------------------
    st.subheader("📈 Performance Metrics")

    col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)

    with col_perf1:
        st.metric("Execution Time", f"{metrics.get('execution_time_ms', 0):.2f}ms")

    with col_perf2:
        st.metric("Total Value", f"{metrics.get('total_value', 0):.1f}")

    with col_perf3:
        st.metric("Value per SP", f"{metrics.get('value_per_sp', 0):.2f}")

    with col_perf4:
        st.metric("Tasks Evaluated", f"{metrics.get('num_tasks_evaluated', 0)}")

    # Efficiency analysis
    with st.expander("📊 Efficiency Analysis"):
        st.write(f"""
        - **Total effort used:** {metrics.get('total_effort', 0):.1f} story points
        - **Total value achieved:** {metrics.get('total_value', 0):.1f} points
        - **Efficiency ratio:** {metrics.get('value_per_sp', 0):.2f} value per story point
        - **Time utilization:** {metrics.get('utilization_pct', 0):.1f}% of available time
        - **Tasks selected:** {metrics.get('num_tasks', 0)} out of {metrics.get('num_tasks_evaluated', 0)} evaluated
        """)


# ==============================================================================
# MAIN RENDER FUNCTION
# ==============================================================================

def render_task_selection():
    """
    Main entry point for the task selection Streamlit application.

    This function is called by the root app.py file to render the complete
    4-tab interface for task selection algorithm prototype.

    Features:
    - Initializes session state
    - Creates 4-tab navigation
    - Renders each tab's content
    - Maintains state across tab switches

    Tabs:
    1. Task Management - CRUD operations
    2. Bandwidth Allocation - Time and domain preferences
    3. Solver Run - Algorithm execution and results
    4. Solver Output Details - Comprehensive explanations

    This function can be called independently for standalone testing.
    """
    # Initialize session state
    initialize_session_state()

    # App title
    st.title("📋 Task Selection Algorithm Prototype")
    st.caption("Optimize your task selection using configurable algorithms")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Task Management",
        "⏱️ Bandwidth Allocation",
        "🚀 Solver Run",
        "📄 Solver Output Details"
    ])

    # Render each tab
    with tab1:
        render_tab_task_management()

    with tab2:
        render_tab_bandwidth_allocation()

    with tab3:
        render_tab_solver_run()

    with tab4:
        render_tab_solver_output_details()


# ==============================================================================
# STANDALONE TEST SECTION
# ==============================================================================

if __name__ == "__main__":
    """
    Standalone test section for the Streamlit UI.

    This allows running the app directly for testing:
    $ streamlit run src/task_selection/task_selection_app.py

    The render_task_selection() function serves as the main entry point.
    """
    render_task_selection()

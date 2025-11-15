"""
Streamlit UI layer for runestones monitoring system.
Provides interactive dashboard with visualizations for monitoring jobs, projects, and metrics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import runestones_workflow as workflow
import runestones_logic as logic


def render_runestones():
    """
    Main render function for the runestones monitoring dashboard.
    Called by the root app.py to display the runestones page.
    """
    st.title("🪨 Runestones Framework Monitor")
    st.markdown("Monitor LLM job execution, token usage, and project metrics")

    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard",
        "📁 Projects",
        "📝 Jobs",
        "🤖 Models",
        "➕ Add Data"
    ])

    with tab1:
        render_dashboard_tab()

    with tab2:
        render_projects_tab()

    with tab3:
        render_jobs_tab()

    with tab4:
        render_models_tab()

    with tab5:
        render_add_data_tab()


def render_dashboard_tab():
    """
    Render the main dashboard overview with key metrics and visualizations.
    """
    st.header("Dashboard Overview")

    # Get dashboard data from workflow
    dashboard_data = workflow.get_dashboard_data()
    overall_stats = dashboard_data['overall_stats']

    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Jobs",
            value=f"{overall_stats['total_jobs']:,}"
        )

    with col2:
        st.metric(
            label="Total Tokens",
            value=f"{overall_stats['total_tokens']:,}"
        )

    with col3:
        st.metric(
            label="Total Tasks",
            value=f"{overall_stats['total_tasks']:,}"
        )

    with col4:
        st.metric(
            label="Total Cost",
            value=f"${overall_stats['total_cost']:.2f}"
        )

    st.divider()

    # Second row of metrics
    col5, col6, col7 = st.columns(3)

    with col5:
        st.metric(
            label="Avg Tokens/Job",
            value=f"{overall_stats['avg_tokens_per_job']:,.0f}"
        )

    with col6:
        st.metric(
            label="Avg Tasks/Job",
            value=f"{overall_stats['avg_tasks_per_job']:.1f}"
        )

    with col7:
        st.metric(
            label="Avg Cost/Job",
            value=f"${overall_stats['avg_cost_per_job']:.3f}"
        )

    st.divider()

    # Visualizations row
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Job Status Distribution")
        status_dist = dashboard_data['status_dist']

        # Create pie chart for status distribution
        fig_status = px.pie(
            status_dist,
            values='count',
            names='status',
            title='Job Status Breakdown',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_status, use_container_width=True)

    with col_right:
        st.subheader("Top Projects by Token Usage")
        top_tokens = dashboard_data['top_projects_tokens']

        # Create bar chart for top projects
        fig_tokens = px.bar(
            top_tokens,
            x='project_name',
            y='total_tokens',
            title='Token Usage by Project',
            labels={'total_tokens': 'Total Tokens', 'project_name': 'Project'},
            color='total_tokens',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_tokens, use_container_width=True)

    # Third row - cost and model visualizations
    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader("Top Projects by Cost")
        top_cost = dashboard_data['top_projects_cost']

        fig_cost = px.bar(
            top_cost,
            x='project_name',
            y='total_cost',
            title='Cost by Project',
            labels={'total_cost': 'Total Cost ($)', 'project_name': 'Project'},
            color='total_cost',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    with col_right2:
        st.subheader("Model Usage Statistics")
        model_stats = dashboard_data['model_stats']

        fig_model = px.bar(
            model_stats,
            x='llm_model',
            y='job_count',
            title='Jobs by LLM Model',
            labels={'job_count': 'Number of Jobs', 'llm_model': 'Model'},
            color='total_cost',
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig_model, use_container_width=True)


def render_projects_tab():
    """
    Render the projects view with detailed project information.
    """
    st.header("Projects Overview")

    # Get dashboard data
    dashboard_data = workflow.get_dashboard_data()
    projects = dashboard_data['projects']

    # Display projects summary table
    st.subheader("All Projects")
    st.dataframe(
        projects,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Project selector for detailed view
    st.subheader("Project Details")

    if len(projects) > 0:
        project_names = projects['project_name'].tolist()
        project_ids = projects['project_id'].tolist()

        # Create mapping for display
        project_map = dict(zip(project_names, project_ids))

        selected_project_name = st.selectbox(
            "Select a project to view details:",
            options=project_names
        )

        if selected_project_name:
            selected_project_id = project_map[selected_project_name]

            # Get project details
            project_details = workflow.get_project_details(selected_project_id)

            if project_details:
                # Display project info
                st.markdown(f"**Project:** {project_details['project_info']['project_name']}")
                st.markdown(f"**Description:** {project_details['project_info']['description']}")
                st.markdown(f"**Created:** {project_details['project_info']['created_date']}")

                st.divider()

                # Display metrics in columns
                if project_details['cost_summary'] is not None:
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Total Cost",
                            f"${project_details['cost_summary']['total_cost']:.3f}"
                        )

                    with col2:
                        st.metric(
                            "Avg Cost/Job",
                            f"${project_details['cost_summary']['avg_cost_per_job']:.3f}"
                        )

                    with col3:
                        st.metric(
                            "Job Count",
                            f"{int(project_details['cost_summary']['job_count'])}"
                        )

                # Budget check
                budget_limit = st.number_input(
                    "Set Budget Limit ($)",
                    min_value=0.0,
                    value=100.0,
                    step=10.0
                )

                budget_status = workflow.check_project_budget_status(
                    selected_project_id,
                    budget_limit=budget_limit
                )

                # Display budget status
                col_budget1, col_budget2 = st.columns(2)

                with col_budget1:
                    st.metric(
                        "Budget Used",
                        f"{budget_status['budget_percentage']:.1f}%",
                        delta=f"${budget_status['remaining_budget']:.2f} remaining"
                    )

                with col_budget2:
                    if budget_status['over_budget']:
                        st.error("⚠️ OVER BUDGET!")
                    else:
                        st.success("✓ Within Budget")

                st.divider()

                # Display jobs for this project
                st.subheader("Jobs in this Project")
                jobs_display = project_details['jobs'][[
                    'job_id', 'prompt_text', 'llm_model', 'status',
                    'token_count', 'task_count', 'total_cost', 'created_date'
                ]]
                st.dataframe(
                    jobs_display,
                    use_container_width=True,
                    hide_index=True
                )
    else:
        st.info("No projects found. Add a project in the 'Add Data' tab.")


def render_jobs_tab():
    """
    Render the jobs view with filtering and detailed job information.
    """
    st.header("Jobs Overview")

    # Filters
    col_filter1, col_filter2 = st.columns(2)

    with col_filter1:
        # Status filter
        status_options = ['All', 'completed', 'in_progress', 'pending', 'failed']
        selected_status = st.selectbox("Filter by Status:", options=status_options)

    with col_filter2:
        # Project filter
        dashboard_data = workflow.get_dashboard_data()
        projects = dashboard_data['projects']
        project_options = ['All'] + projects['project_name'].tolist()
        selected_project = st.selectbox("Filter by Project:", options=project_options)

    # Get filtered jobs
    project_id = None
    if selected_project != 'All':
        project_id = projects[projects['project_name'] == selected_project]['project_id'].values[0]

    status = None if selected_status == 'All' else selected_status

    jobs = workflow.get_jobs_list(project_id=project_id, status=status)

    # Display job count
    st.metric("Total Jobs", len(jobs))

    # Display jobs table
    if len(jobs) > 0:
        jobs_display = jobs[[
            'job_id', 'project_id', 'prompt_text', 'llm_model', 'status',
            'token_count', 'task_count', 'total_cost', 'created_date', 'completed_date'
        ]]

        st.dataframe(
            jobs_display,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # Efficiency analysis
        st.subheader("Job Efficiency Analysis")
        efficiency_data = workflow.get_job_efficiency_analysis()

        # Filter by current selection
        if project_id:
            efficiency_data = efficiency_data[efficiency_data['project_id'] == project_id]
        if status:
            # Need to join with original jobs to get status
            pass  # Already filtered above

        st.dataframe(
            efficiency_data,
            use_container_width=True,
            hide_index=True
        )

        # Visualize efficiency
        fig_efficiency = px.scatter(
            efficiency_data.head(20),
            x='token_count',
            y='task_count',
            size='efficiency_score',
            color='llm_model',
            hover_data=['job_id'],
            title='Job Efficiency: Tasks vs Tokens',
            labels={
                'token_count': 'Token Count',
                'task_count': 'Task Count',
                'efficiency_score': 'Efficiency Score'
            }
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)

    else:
        st.info("No jobs found matching the selected filters.")


def render_models_tab():
    """
    Render the models comparison view.
    """
    st.header("LLM Model Comparison")

    # Get model comparison data
    model_stats = workflow.get_model_comparison()

    # Display model statistics table
    st.subheader("Model Statistics")
    st.dataframe(
        model_stats,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Token usage by model
        fig_tokens = px.bar(
            model_stats,
            x='llm_model',
            y='total_tokens',
            title='Total Tokens by Model',
            labels={'total_tokens': 'Total Tokens', 'llm_model': 'Model'},
            color='total_tokens',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_tokens, use_container_width=True)

    with col2:
        # Cost by model
        fig_cost = px.bar(
            model_stats,
            x='llm_model',
            y='total_cost',
            title='Total Cost by Model',
            labels={'total_cost': 'Total Cost ($)', 'llm_model': 'Model'},
            color='total_cost',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    # Average comparison
    st.subheader("Average Metrics Comparison")

    fig_avg = go.Figure()

    fig_avg.add_trace(go.Bar(
        name='Avg Tokens per Job',
        x=model_stats['llm_model'],
        y=model_stats['avg_tokens_per_job'],
        yaxis='y',
        offsetgroup=1
    ))

    fig_avg.update_layout(
        title='Average Tokens per Job by Model',
        xaxis=dict(title='Model'),
        yaxis=dict(title='Average Tokens'),
        barmode='group'
    )

    st.plotly_chart(fig_avg, use_container_width=True)


def render_add_data_tab():
    """
    Render the add data form for creating new projects and jobs.
    """
    st.header("Add New Data")

    # Two columns for project and job forms
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Add New Project")

        with st.form("new_project_form"):
            project_name = st.text_input("Project Name*")
            project_description = st.text_area("Description")

            submitted = st.form_submit_button("Create Project")

            if submitted:
                if project_name:
                    success, message, project_id = workflow.create_new_project(
                        project_name,
                        project_description
                    )

                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please provide a project name")

    with col2:
        st.subheader("Add New Job")

        # Get projects for dropdown
        dashboard_data = workflow.get_dashboard_data()
        projects = dashboard_data['projects']

        if len(projects) > 0:
            with st.form("new_job_form"):
                project_names = projects['project_name'].tolist()
                project_ids = projects['project_id'].tolist()
                project_map = dict(zip(project_names, project_ids))

                selected_project = st.selectbox("Project*", options=project_names)
                prompt_text = st.text_area("Prompt Text*")
                llm_model = st.selectbox(
                    "LLM Model*",
                    options=['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
                )

                col_a, col_b = st.columns(2)
                with col_a:
                    token_count = st.number_input("Total Tokens*", min_value=0, value=1000)
                    task_count = st.number_input("Task Count*", min_value=0, value=1)

                with col_b:
                    input_tokens = st.number_input("Input Tokens*", min_value=0, value=200)
                    output_tokens = st.number_input("Output Tokens*", min_value=0, value=800)

                # Calculate and display estimated cost
                estimated_cost = logic.calculate_token_cost(token_count, llm_model)
                st.info(f"Estimated Cost: ${estimated_cost:.3f}")

                submitted_job = st.form_submit_button("Create Job")

                if submitted_job:
                    if prompt_text and selected_project:
                        project_id = project_map[selected_project]

                        success, message, job_id = workflow.create_new_job(
                            project_id,
                            prompt_text,
                            llm_model,
                            token_count,
                            task_count,
                            input_tokens,
                            output_tokens
                        )

                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all required fields")
        else:
            st.info("Please create a project first before adding jobs.")


if __name__ == "__main__":
    # Standalone test section - run the Streamlit app directly
    st.set_page_config(
        page_title="Runestones Monitor",
        page_icon="🪨",
        layout="wide"
    )

    render_runestones()

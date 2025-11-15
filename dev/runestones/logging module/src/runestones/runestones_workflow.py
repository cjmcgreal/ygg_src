"""
Workflow layer for runestones monitoring system.
Acts as the API interface layer between frontend and backend.
Orchestrates calls to logic, analysis, and database modules.
"""

import runestones_db as db
import runestones_analysis as analysis
import runestones_logic as logic


def get_dashboard_data():
    """
    Get all data needed for the main dashboard view.

    Returns:
        dict: Dictionary containing all dashboard data including:
            - projects: All projects with job counts
            - overall_stats: Overall statistics
            - model_stats: Statistics by LLM model
            - status_dist: Job status distribution
            - top_projects_tokens: Top projects by token usage
            - top_projects_cost: Top projects by cost
    """
    # Load base data
    projects_df = db.get_all_projects()
    jobs_df = db.get_all_jobs()
    jobs_with_metrics_df = db.get_jobs_with_metrics()

    # Calculate various metrics
    overall_stats = analysis.calculate_overall_stats(jobs_with_metrics_df)
    model_stats = analysis.calculate_model_usage_stats(jobs_with_metrics_df)
    status_dist = analysis.calculate_status_distribution(jobs_df)
    top_projects_tokens = analysis.get_top_projects_by_tokens(jobs_with_metrics_df, projects_df, top_n=5)
    top_projects_cost = analysis.get_top_projects_by_cost(jobs_with_metrics_df, projects_df, top_n=5)
    projects_with_counts = db.get_projects_with_job_counts()

    return {
        'projects': projects_with_counts,
        'overall_stats': overall_stats,
        'model_stats': model_stats,
        'status_dist': status_dist,
        'top_projects_tokens': top_projects_tokens,
        'top_projects_cost': top_projects_cost
    }


def get_project_details(project_id):
    """
    Get detailed information about a specific project.

    Args:
        project_id (int): The project ID

    Returns:
        dict: Dictionary containing project details including:
            - project_info: Project metadata
            - jobs: All jobs for the project with metrics
            - token_summary: Token usage summary
            - cost_summary: Cost summary
            - task_summary: Task summary
    """
    # Get project info
    projects_df = db.get_all_projects()
    project_info = projects_df[projects_df['project_id'] == project_id]

    if len(project_info) == 0:
        return None

    project_info = project_info.iloc[0]

    # Get jobs for this project
    jobs_df = db.get_jobs_by_project(project_id)

    # Get jobs with metrics for this project
    all_jobs_with_metrics = db.get_jobs_with_metrics()
    project_jobs_with_metrics = all_jobs_with_metrics[all_jobs_with_metrics['project_id'] == project_id]

    # Calculate summaries
    token_summary = analysis.calculate_project_token_summary(project_jobs_with_metrics)
    cost_summary = analysis.calculate_project_cost_summary(project_jobs_with_metrics)
    task_summary = analysis.calculate_task_summary(project_jobs_with_metrics)

    return {
        'project_info': project_info,
        'jobs': project_jobs_with_metrics,
        'token_summary': token_summary.iloc[0] if len(token_summary) > 0 else None,
        'cost_summary': cost_summary.iloc[0] if len(cost_summary) > 0 else None,
        'task_summary': task_summary.iloc[0] if len(task_summary) > 0 else None
    }


def get_jobs_list(project_id=None, status=None, start_date=None, end_date=None):
    """
    Get filtered list of jobs with metrics.

    Args:
        project_id (int, optional): Filter by project ID
        status (str, optional): Filter by job status
        start_date (str, optional): Filter by start date
        end_date (str, optional): Filter by end date

    Returns:
        pd.DataFrame: Filtered jobs with metrics
    """
    # Get all jobs with metrics
    jobs_with_metrics_df = db.get_jobs_with_metrics()

    # Apply project filter
    if project_id is not None:
        jobs_with_metrics_df = jobs_with_metrics_df[jobs_with_metrics_df['project_id'] == project_id]

    # Apply status filter
    if status is not None:
        jobs_with_metrics_df = jobs_with_metrics_df[jobs_with_metrics_df['status'] == status]

    # Apply date range filter
    if start_date or end_date:
        jobs_with_metrics_df = logic.filter_jobs_by_date_range(jobs_with_metrics_df, start_date, end_date)

    return jobs_with_metrics_df


def create_new_project(project_name, description):
    """
    Create a new project with validation.

    Args:
        project_name (str): Name of the project
        description (str): Project description

    Returns:
        tuple: (success: bool, message: str, project_id: int or None)
    """
    # Validate project name
    is_valid, error = logic.validate_project_name(project_name)

    if not is_valid:
        return False, error, None

    # Create project in database
    try:
        project_id = db.add_project(project_name, description)
        return True, f"Project created successfully with ID {project_id}", project_id
    except Exception as e:
        return False, f"Error creating project: {str(e)}", None


def create_new_job(project_id, prompt_text, llm_model, token_count, task_count, input_tokens, output_tokens):
    """
    Create a new job with validation and metrics.

    Args:
        project_id (int): ID of the project
        prompt_text (str): The prompt text
        llm_model (str): The LLM model used
        token_count (int): Total token count
        task_count (int): Number of tasks
        input_tokens (int): Input token count
        output_tokens (int): Output token count

    Returns:
        tuple: (success: bool, message: str, job_id: int or None)
    """
    # Validate job data
    is_valid, error = logic.validate_job_data(prompt_text, llm_model)
    if not is_valid:
        return False, error, None

    # Validate metrics data
    is_valid, error = logic.validate_metrics_data(token_count, task_count, input_tokens, output_tokens)
    if not is_valid:
        return False, error, None

    # Calculate cost
    total_cost = logic.calculate_token_cost(token_count, llm_model)

    try:
        # Create job
        job_id = db.add_job(project_id, prompt_text, llm_model, status='completed')

        # Add metrics
        db.add_job_metrics(job_id, token_count, task_count, input_tokens, output_tokens, total_cost)

        return True, f"Job created successfully with ID {job_id}", job_id
    except Exception as e:
        return False, f"Error creating job: {str(e)}", None


def update_job_status_workflow(job_id, new_status):
    """
    Update job status with validation.

    Args:
        job_id (int): ID of the job to update
        new_status (str): New status value

    Returns:
        tuple: (success: bool, message: str)
    """
    valid_statuses = ['pending', 'in_progress', 'completed', 'failed', 'cancelled']

    if new_status not in valid_statuses:
        return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

    try:
        db.update_job_status(job_id, new_status)
        return True, f"Job {job_id} status updated to {new_status}"
    except Exception as e:
        return False, f"Error updating job status: {str(e)}"


def get_model_comparison():
    """
    Get comparison data across different LLM models.

    Returns:
        pd.DataFrame: Model usage statistics
    """
    jobs_with_metrics_df = db.get_jobs_with_metrics()
    return analysis.calculate_model_usage_stats(jobs_with_metrics_df)


def get_time_series_data(frequency='D'):
    """
    Get time series data for jobs created over time.

    Args:
        frequency (str): Frequency for grouping ('D', 'W', 'M')

    Returns:
        pd.DataFrame: Time series data
    """
    jobs_df = db.get_all_jobs()
    return analysis.calculate_jobs_over_time(jobs_df, freq=frequency)


def check_project_budget_status(project_id, budget_limit=100.0):
    """
    Check if a project is within budget.

    Args:
        project_id (int): The project ID
        budget_limit (float): Budget limit in dollars

    Returns:
        dict: Dictionary containing budget status information
    """
    # Get project jobs with metrics
    all_jobs_with_metrics = db.get_jobs_with_metrics()
    project_jobs = all_jobs_with_metrics[all_jobs_with_metrics['project_id'] == project_id]

    # Calculate total cost
    total_cost = project_jobs['total_cost'].sum()

    # Check if over budget
    over_budget = logic.is_project_over_budget(total_cost, budget_limit)

    # Calculate remaining budget
    remaining_budget = budget_limit - total_cost

    return {
        'project_id': project_id,
        'total_cost': round(total_cost, 3),
        'budget_limit': budget_limit,
        'remaining_budget': round(remaining_budget, 3),
        'over_budget': over_budget,
        'budget_percentage': round((total_cost / budget_limit) * 100, 1)
    }


def get_job_efficiency_analysis():
    """
    Get efficiency analysis for all jobs.

    Returns:
        pd.DataFrame: Jobs with efficiency scores
    """
    jobs_with_metrics_df = db.get_jobs_with_metrics()

    # Add efficiency score to each job
    jobs_with_metrics_df['efficiency_score'] = jobs_with_metrics_df.apply(
        lambda row: logic.calculate_efficiency_score(row['token_count'], row['task_count']),
        axis=1
    )

    return jobs_with_metrics_df[['job_id', 'project_id', 'llm_model', 'task_count', 'token_count', 'efficiency_score']].sort_values('efficiency_score', ascending=False)


if __name__ == "__main__":
    # Standalone test section - demonstrates workflow orchestration
    print("=" * 60)
    print("RUNESTONES WORKFLOW LAYER TEST")
    print("=" * 60)

    # Test 1: Get dashboard data
    print("\n1. Dashboard Data:")
    dashboard = get_dashboard_data()
    print(f"   Total Projects: {len(dashboard['projects'])}")
    print(f"   Overall Stats Keys: {list(dashboard['overall_stats'].keys())}")
    print(f"   Total Jobs: {dashboard['overall_stats']['total_jobs']}")
    print(f"   Total Cost: ${dashboard['overall_stats']['total_cost']}")

    # Test 2: Get project details
    print("\n2. Project Details (Project 1):")
    project_details = get_project_details(1)
    if project_details:
        print(f"   Project Name: {project_details['project_info']['project_name']}")
        print(f"   Number of Jobs: {len(project_details['jobs'])}")
        if project_details['cost_summary'] is not None:
            print(f"   Total Cost: ${project_details['cost_summary']['total_cost']}")
            print(f"   Avg Cost per Job: ${project_details['cost_summary']['avg_cost_per_job']}")

    # Test 3: Get filtered jobs list
    print("\n3. Filtered Jobs (Completed Status):")
    completed_jobs = get_jobs_list(status='completed')
    print(f"   Number of Completed Jobs: {len(completed_jobs)}")

    # Test 4: Model comparison
    print("\n4. Model Comparison:")
    model_comparison = get_model_comparison()
    print(model_comparison[['llm_model', 'job_count', 'total_tokens', 'total_cost']].to_string(index=False))

    # Test 5: Check project budget
    print("\n5. Budget Status Check (Project 1, Budget=$100):")
    budget_status = check_project_budget_status(1, budget_limit=100.0)
    print(f"   Total Cost: ${budget_status['total_cost']}")
    print(f"   Remaining Budget: ${budget_status['remaining_budget']}")
    print(f"   Budget Used: {budget_status['budget_percentage']}%")
    print(f"   Over Budget: {budget_status['over_budget']}")

    # Test 6: Job efficiency analysis
    print("\n6. Job Efficiency Analysis (Top 3):")
    efficiency = get_job_efficiency_analysis()
    print(efficiency.head(3).to_string(index=False))

    # Test 7: Validate new project creation
    print("\n7. Validate New Project:")
    success, message, project_id = create_new_project("Test Project", "This is a test")
    print(f"   Validation Result: {message}")

    # Test 8: Validate new job creation
    print("\n8. Validate New Job:")
    success, message, job_id = create_new_job(
        project_id=1,
        prompt_text="This is a test prompt for validation",
        llm_model="gpt-4",
        token_count=1000,
        task_count=2,
        input_tokens=200,
        output_tokens=800
    )
    print(f"   Validation Result: {message}")

    print("\n" + "=" * 60)
    print("All workflow operations completed successfully!")
    print("=" * 60)

"""
Analysis layer for runestones monitoring system.
Handles data analysis, aggregations, and statistical calculations.
"""

import pandas as pd
from datetime import datetime


def calculate_project_token_summary(jobs_with_metrics_df):
    """
    Calculate total tokens used per project.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data

    Returns:
        pd.DataFrame: Summary with columns [project_id, total_tokens, total_input_tokens, total_output_tokens]
    """
    # Group by project_id and sum token counts
    summary_df = jobs_with_metrics_df.groupby('project_id').agg({
        'token_count': 'sum',
        'input_tokens': 'sum',
        'output_tokens': 'sum'
    }).reset_index()

    # Rename columns for clarity
    summary_df.columns = ['project_id', 'total_tokens', 'total_input_tokens', 'total_output_tokens']

    return summary_df


def calculate_project_cost_summary(jobs_with_metrics_df):
    """
    Calculate total costs per project.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data

    Returns:
        pd.DataFrame: Summary with columns [project_id, total_cost, avg_cost_per_job, job_count]
    """
    # Group by project and calculate cost metrics
    summary_df = jobs_with_metrics_df.groupby('project_id').agg({
        'total_cost': ['sum', 'mean', 'count']
    }).reset_index()

    # Flatten column names
    summary_df.columns = ['project_id', 'total_cost', 'avg_cost_per_job', 'job_count']

    # Round costs to 3 decimal places
    summary_df['total_cost'] = summary_df['total_cost'].round(3)
    summary_df['avg_cost_per_job'] = summary_df['avg_cost_per_job'].round(3)

    return summary_df


def calculate_task_summary(jobs_with_metrics_df):
    """
    Calculate task-related metrics per project.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data

    Returns:
        pd.DataFrame: Summary with columns [project_id, total_tasks, avg_tasks_per_job, max_tasks_in_job]
    """
    # Group by project and calculate task metrics
    summary_df = jobs_with_metrics_df.groupby('project_id').agg({
        'task_count': ['sum', 'mean', 'max']
    }).reset_index()

    # Flatten column names
    summary_df.columns = ['project_id', 'total_tasks', 'avg_tasks_per_job', 'max_tasks_in_job']

    # Round averages to 1 decimal place
    summary_df['avg_tasks_per_job'] = summary_df['avg_tasks_per_job'].round(1)

    return summary_df


def calculate_model_usage_stats(jobs_with_metrics_df):
    """
    Calculate usage statistics grouped by LLM model.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data

    Returns:
        pd.DataFrame: Summary with columns [llm_model, job_count, total_tokens, total_cost, avg_tokens_per_job]
    """
    # Group by LLM model
    summary_df = jobs_with_metrics_df.groupby('llm_model').agg({
        'job_id': 'count',
        'token_count': ['sum', 'mean'],
        'total_cost': 'sum'
    }).reset_index()

    # Flatten column names
    summary_df.columns = ['llm_model', 'job_count', 'total_tokens', 'avg_tokens_per_job', 'total_cost']

    # Round values
    summary_df['avg_tokens_per_job'] = summary_df['avg_tokens_per_job'].round(0)
    summary_df['total_cost'] = summary_df['total_cost'].round(3)

    return summary_df


def calculate_status_distribution(jobs_df):
    """
    Calculate the distribution of job statuses.

    Args:
        jobs_df (pd.DataFrame): Jobs data

    Returns:
        pd.DataFrame: Summary with columns [status, count, percentage]
    """
    # Count jobs by status
    status_counts = jobs_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    # Calculate percentage
    total_jobs = status_counts['count'].sum()
    status_counts['percentage'] = (status_counts['count'] / total_jobs * 100).round(1)

    return status_counts


def get_date_range_stats(jobs_df):
    """
    Calculate statistics about job dates.

    Args:
        jobs_df (pd.DataFrame): Jobs data with created_date column

    Returns:
        dict: Dictionary containing date range information
    """
    # Convert created_date to datetime
    jobs_df = jobs_df.copy()
    jobs_df['created_date'] = pd.to_datetime(jobs_df['created_date'])

    # Calculate date range
    date_stats = {
        'earliest_date': jobs_df['created_date'].min(),
        'latest_date': jobs_df['created_date'].max(),
        'total_days': (jobs_df['created_date'].max() - jobs_df['created_date'].min()).days
    }

    return date_stats


def calculate_jobs_over_time(jobs_df, freq='D'):
    """
    Calculate number of jobs created over time.

    Args:
        jobs_df (pd.DataFrame): Jobs data with created_date column
        freq (str): Frequency for grouping ('D' for daily, 'W' for weekly, 'M' for monthly)

    Returns:
        pd.DataFrame: Time series data with columns [date, job_count]
    """
    # Convert created_date to datetime
    jobs_df = jobs_df.copy()
    jobs_df['created_date'] = pd.to_datetime(jobs_df['created_date'])

    # Group by date period
    time_series = jobs_df.groupby(pd.Grouper(key='created_date', freq=freq)).size().reset_index()
    time_series.columns = ['date', 'job_count']

    return time_series


def get_top_projects_by_tokens(jobs_with_metrics_df, projects_df, top_n=5):
    """
    Get top N projects by total token usage.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data
        projects_df (pd.DataFrame): Projects data
        top_n (int): Number of top projects to return

    Returns:
        pd.DataFrame: Top projects with columns [project_name, total_tokens, job_count]
    """
    # Calculate token summary by project
    token_summary = calculate_project_token_summary(jobs_with_metrics_df)

    # Merge with project names
    result_df = token_summary.merge(projects_df[['project_id', 'project_name']], on='project_id')

    # Count jobs per project
    job_counts = jobs_with_metrics_df.groupby('project_id').size().reset_index(name='job_count')
    result_df = result_df.merge(job_counts, on='project_id')

    # Sort by total tokens descending and get top N
    result_df = result_df.sort_values('total_tokens', ascending=False).head(top_n)

    # Reorder columns
    result_df = result_df[['project_name', 'total_tokens', 'job_count']]

    return result_df


def get_top_projects_by_cost(jobs_with_metrics_df, projects_df, top_n=5):
    """
    Get top N projects by total cost.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data
        projects_df (pd.DataFrame): Projects data
        top_n (int): Number of top projects to return

    Returns:
        pd.DataFrame: Top projects with columns [project_name, total_cost, job_count]
    """
    # Calculate cost summary by project
    cost_summary = calculate_project_cost_summary(jobs_with_metrics_df)

    # Merge with project names
    result_df = cost_summary.merge(projects_df[['project_id', 'project_name']], on='project_id')

    # Sort by total cost descending and get top N
    result_df = result_df.sort_values('total_cost', ascending=False).head(top_n)

    # Reorder columns
    result_df = result_df[['project_name', 'total_cost', 'job_count']]

    return result_df


def calculate_overall_stats(jobs_with_metrics_df):
    """
    Calculate overall statistics across all jobs.

    Args:
        jobs_with_metrics_df (pd.DataFrame): Jobs joined with metrics data

    Returns:
        dict: Dictionary containing overall statistics
    """
    stats = {
        'total_jobs': len(jobs_with_metrics_df),
        'total_tokens': jobs_with_metrics_df['token_count'].sum(),
        'total_tasks': jobs_with_metrics_df['task_count'].sum(),
        'total_cost': round(jobs_with_metrics_df['total_cost'].sum(), 3),
        'avg_tokens_per_job': round(jobs_with_metrics_df['token_count'].mean(), 0),
        'avg_tasks_per_job': round(jobs_with_metrics_df['task_count'].mean(), 1),
        'avg_cost_per_job': round(jobs_with_metrics_df['total_cost'].mean(), 3)
    }

    return stats


if __name__ == "__main__":
    # Standalone test section - demonstrates analysis functions
    import sys
    import os
    # Add parent directory to path to import db module
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from runestones_db import get_all_projects, get_all_jobs, get_jobs_with_metrics

    print("=" * 60)
    print("RUNESTONES ANALYSIS LAYER TEST")
    print("=" * 60)

    # Load data
    projects_df = get_all_projects()
    jobs_df = get_all_jobs()
    jobs_with_metrics_df = get_jobs_with_metrics()

    # Test 1: Overall statistics
    print("\n1. Overall Statistics:")
    overall_stats = calculate_overall_stats(jobs_with_metrics_df)
    for key, value in overall_stats.items():
        print(f"   {key}: {value}")

    # Test 2: Project token summary
    print("\n2. Token Usage by Project:")
    token_summary = calculate_project_token_summary(jobs_with_metrics_df)
    print(token_summary.to_string(index=False))

    # Test 3: Project cost summary
    print("\n3. Cost Summary by Project:")
    cost_summary = calculate_project_cost_summary(jobs_with_metrics_df)
    print(cost_summary.to_string(index=False))

    # Test 4: Task summary
    print("\n4. Task Summary by Project:")
    task_summary = calculate_task_summary(jobs_with_metrics_df)
    print(task_summary.to_string(index=False))

    # Test 5: Model usage statistics
    print("\n5. Usage Statistics by LLM Model:")
    model_stats = calculate_model_usage_stats(jobs_with_metrics_df)
    print(model_stats.to_string(index=False))

    # Test 6: Status distribution
    print("\n6. Job Status Distribution:")
    status_dist = calculate_status_distribution(jobs_df)
    print(status_dist.to_string(index=False))

    # Test 7: Top projects by tokens
    print("\n7. Top Projects by Token Usage:")
    top_tokens = get_top_projects_by_tokens(jobs_with_metrics_df, projects_df, top_n=3)
    print(top_tokens.to_string(index=False))

    # Test 8: Top projects by cost
    print("\n8. Top Projects by Cost:")
    top_cost = get_top_projects_by_cost(jobs_with_metrics_df, projects_df, top_n=3)
    print(top_cost.to_string(index=False))

    # Test 9: Date range statistics
    print("\n9. Date Range Statistics:")
    date_stats = get_date_range_stats(jobs_df)
    print(f"   Earliest job: {date_stats['earliest_date']}")
    print(f"   Latest job: {date_stats['latest_date']}")
    print(f"   Total span: {date_stats['total_days']} days")

    print("\n" + "=" * 60)
    print("All analysis operations completed successfully!")
    print("=" * 60)

"""
Database layer for runestones monitoring system.
Handles all CSV file reading and writing operations.
"""

import pandas as pd
import os
from datetime import datetime

# Define paths to CSV files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'runestones_data')
PROJECTS_CSV = os.path.join(DATA_DIR, 'projects.csv')
JOBS_CSV = os.path.join(DATA_DIR, 'jobs.csv')
JOB_METRICS_CSV = os.path.join(DATA_DIR, 'job_metrics.csv')


def get_all_projects():
    """
    Load all projects from CSV.

    Returns:
        pd.DataFrame: All projects with columns [project_id, project_name, description, created_date]
    """
    try:
        projects_df = pd.read_csv(PROJECTS_CSV)
        return projects_df
    except FileNotFoundError:
        # Return empty DataFrame with correct columns if file doesn't exist
        return pd.DataFrame(columns=['project_id', 'project_name', 'description', 'created_date'])


def get_all_jobs():
    """
    Load all jobs from CSV.

    Returns:
        pd.DataFrame: All jobs with columns [job_id, project_id, prompt_text, llm_model, status, created_date, completed_date]
    """
    try:
        jobs_df = pd.read_csv(JOBS_CSV)
        return jobs_df
    except FileNotFoundError:
        return pd.DataFrame(columns=['job_id', 'project_id', 'prompt_text', 'llm_model', 'status', 'created_date', 'completed_date'])


def get_all_job_metrics():
    """
    Load all job metrics from CSV.

    Returns:
        pd.DataFrame: All job metrics with columns [job_id, token_count, task_count, input_tokens, output_tokens, total_cost]
    """
    try:
        metrics_df = pd.read_csv(JOB_METRICS_CSV)
        return metrics_df
    except FileNotFoundError:
        return pd.DataFrame(columns=['job_id', 'token_count', 'task_count', 'input_tokens', 'output_tokens', 'total_cost'])


def get_jobs_by_project(project_id):
    """
    Get all jobs for a specific project.

    Args:
        project_id (int): Project ID to filter by

    Returns:
        pd.DataFrame: Filtered jobs for the specified project
    """
    jobs_df = get_all_jobs()
    return jobs_df[jobs_df['project_id'] == project_id].copy()


def get_metrics_for_job(job_id):
    """
    Get metrics for a specific job.

    Args:
        job_id (int): Job ID to retrieve metrics for

    Returns:
        pd.Series or None: Metrics for the job, or None if not found
    """
    metrics_df = get_all_job_metrics()
    result = metrics_df[metrics_df['job_id'] == job_id]

    if len(result) > 0:
        return result.iloc[0]
    return None


def add_project(project_name, description):
    """
    Add a new project to the database.

    Args:
        project_name (str): Name of the project
        description (str): Project description

    Returns:
        int: The new project_id
    """
    projects_df = get_all_projects()

    # Generate new project_id
    if len(projects_df) > 0:
        new_id = projects_df['project_id'].max() + 1
    else:
        new_id = 1

    # Create new project row
    new_project = pd.DataFrame([{
        'project_id': new_id,
        'project_name': project_name,
        'description': description,
        'created_date': datetime.now().strftime('%Y-%m-%d')
    }])

    # Append and save
    projects_df = pd.concat([projects_df, new_project], ignore_index=True)
    projects_df.to_csv(PROJECTS_CSV, index=False)

    return new_id


def add_job(project_id, prompt_text, llm_model, status='pending'):
    """
    Add a new job to the database.

    Args:
        project_id (int): ID of the project this job belongs to
        prompt_text (str): The prompt text sent to the LLM
        llm_model (str): The LLM model used (e.g., 'gpt-4', 'claude-3-opus')
        status (str): Job status ('pending', 'in_progress', 'completed', 'failed')

    Returns:
        int: The new job_id
    """
    jobs_df = get_all_jobs()

    # Generate new job_id
    if len(jobs_df) > 0:
        new_id = jobs_df['job_id'].max() + 1
    else:
        new_id = 1

    # Create new job row
    new_job = pd.DataFrame([{
        'job_id': new_id,
        'project_id': project_id,
        'prompt_text': prompt_text,
        'llm_model': llm_model,
        'status': status,
        'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'completed_date': ''
    }])

    # Append and save
    jobs_df = pd.concat([jobs_df, new_job], ignore_index=True)
    jobs_df.to_csv(JOBS_CSV, index=False)

    return new_id


def add_job_metrics(job_id, token_count, task_count, input_tokens, output_tokens, total_cost):
    """
    Add metrics for a job.

    Args:
        job_id (int): ID of the job
        token_count (int): Total token count
        task_count (int): Number of tasks in the job
        input_tokens (int): Input token count
        output_tokens (int): Output token count
        total_cost (float): Total cost in dollars
    """
    metrics_df = get_all_job_metrics()

    # Create new metrics row
    new_metrics = pd.DataFrame([{
        'job_id': job_id,
        'token_count': token_count,
        'task_count': task_count,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_cost': total_cost
    }])

    # Append and save
    metrics_df = pd.concat([metrics_df, new_metrics], ignore_index=True)
    metrics_df.to_csv(JOB_METRICS_CSV, index=False)


def update_job_status(job_id, status, completed_date=None):
    """
    Update the status of a job.

    Args:
        job_id (int): ID of the job to update
        status (str): New status value
        completed_date (str, optional): Completion date if status is 'completed'
    """
    jobs_df = get_all_jobs()

    # Update the job status
    jobs_df.loc[jobs_df['job_id'] == job_id, 'status'] = status

    # Update completed_date if provided
    if completed_date:
        jobs_df.loc[jobs_df['job_id'] == job_id, 'completed_date'] = completed_date
    elif status == 'completed' and not completed_date:
        # Auto-set completed_date if status is completed but date not provided
        jobs_df.loc[jobs_df['job_id'] == job_id, 'completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Save back to CSV
    jobs_df.to_csv(JOBS_CSV, index=False)


def get_jobs_with_metrics():
    """
    Get all jobs joined with their metrics.

    Returns:
        pd.DataFrame: Jobs with their associated metrics
    """
    jobs_df = get_all_jobs()
    metrics_df = get_all_job_metrics()

    # Merge jobs with metrics on job_id
    merged_df = jobs_df.merge(metrics_df, on='job_id', how='left')

    # Fill NaN values in numeric columns with 0
    numeric_columns = ['token_count', 'task_count', 'input_tokens', 'output_tokens', 'total_cost']
    for col in numeric_columns:
        merged_df[col] = merged_df[col].fillna(0)

    return merged_df


def get_projects_with_job_counts():
    """
    Get all projects with their job counts.

    Returns:
        pd.DataFrame: Projects with an additional 'job_count' column
    """
    projects_df = get_all_projects()
    jobs_df = get_all_jobs()

    # Count jobs per project
    job_counts = jobs_df.groupby('project_id').size().reset_index(name='job_count')

    # Merge with projects
    result_df = projects_df.merge(job_counts, on='project_id', how='left')
    result_df['job_count'] = result_df['job_count'].fillna(0).astype(int)

    return result_df


if __name__ == "__main__":
    # Standalone test section - demonstrates usage of database functions
    print("=" * 60)
    print("RUNESTONES DATABASE LAYER TEST")
    print("=" * 60)

    # Test 1: Load all projects
    print("\n1. All Projects:")
    projects = get_all_projects()
    print(projects.to_string(index=False))

    # Test 2: Load all jobs
    print("\n2. All Jobs:")
    jobs = get_all_jobs()
    print(jobs[['job_id', 'project_id', 'llm_model', 'status']].to_string(index=False))

    # Test 3: Load all metrics
    print("\n3. All Job Metrics:")
    metrics = get_all_job_metrics()
    print(metrics.to_string(index=False))

    # Test 4: Get jobs for specific project
    print("\n4. Jobs for Project 1 (Content Generation):")
    project_jobs = get_jobs_by_project(1)
    print(project_jobs[['job_id', 'prompt_text', 'status']].to_string(index=False))

    # Test 5: Get jobs with metrics (joined data)
    print("\n5. Jobs with Metrics (joined):")
    joined = get_jobs_with_metrics()
    print(joined[['job_id', 'project_id', 'token_count', 'task_count', 'total_cost']].head().to_string(index=False))

    # Test 6: Get projects with job counts
    print("\n6. Projects with Job Counts:")
    projects_with_counts = get_projects_with_job_counts()
    print(projects_with_counts.to_string(index=False))

    # Test 7: Get metrics for specific job
    print("\n7. Metrics for Job 1:")
    job_metrics = get_metrics_for_job(1)
    if job_metrics is not None:
        print(f"   Token Count: {job_metrics['token_count']}")
        print(f"   Task Count: {job_metrics['task_count']}")
        print(f"   Total Cost: ${job_metrics['total_cost']:.3f}")

    print("\n" + "=" * 60)
    print("All database operations completed successfully!")
    print("=" * 60)

"""
Tests for runestones_db module.
"""

import pytest
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'runestones'))

import runestones_db as db


def test_get_all_projects():
    """Test loading all projects from CSV."""
    projects = db.get_all_projects()

    assert isinstance(projects, pd.DataFrame)
    assert 'project_id' in projects.columns
    assert 'project_name' in projects.columns
    assert len(projects) >= 3  # At least our sample data


def test_get_all_jobs():
    """Test loading all jobs from CSV."""
    jobs = db.get_all_jobs()

    assert isinstance(jobs, pd.DataFrame)
    assert 'job_id' in jobs.columns
    assert 'project_id' in jobs.columns
    assert 'llm_model' in jobs.columns
    assert len(jobs) >= 7  # At least our sample data


def test_get_all_job_metrics():
    """Test loading all job metrics from CSV."""
    metrics = db.get_all_job_metrics()

    assert isinstance(metrics, pd.DataFrame)
    assert 'job_id' in metrics.columns
    assert 'token_count' in metrics.columns
    assert 'task_count' in metrics.columns


def test_get_jobs_by_project():
    """Test filtering jobs by project ID."""
    project_jobs = db.get_jobs_by_project(1)

    assert isinstance(project_jobs, pd.DataFrame)
    assert all(project_jobs['project_id'] == 1)


def test_get_metrics_for_job():
    """Test retrieving metrics for a specific job."""
    metrics = db.get_metrics_for_job(1)

    assert metrics is not None
    assert 'token_count' in metrics.index
    assert 'task_count' in metrics.index


def test_get_jobs_with_metrics():
    """Test joining jobs with their metrics."""
    joined = db.get_jobs_with_metrics()

    assert isinstance(joined, pd.DataFrame)
    assert 'job_id' in joined.columns
    assert 'token_count' in joined.columns
    assert 'project_id' in joined.columns


def test_get_projects_with_job_counts():
    """Test getting projects with their job counts."""
    projects = db.get_projects_with_job_counts()

    assert isinstance(projects, pd.DataFrame)
    assert 'project_id' in projects.columns
    assert 'job_count' in projects.columns


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])

"""
Tests for runestones_workflow module.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'runestones'))

import runestones_workflow as workflow


def test_get_dashboard_data():
    """Test dashboard data retrieval."""
    data = workflow.get_dashboard_data()

    assert 'projects' in data
    assert 'overall_stats' in data
    assert 'model_stats' in data
    assert 'status_dist' in data
    assert 'top_projects_tokens' in data
    assert 'top_projects_cost' in data

    assert data['overall_stats']['total_jobs'] > 0


def test_get_project_details():
    """Test project details retrieval."""
    details = workflow.get_project_details(1)

    assert details is not None
    assert 'project_info' in details
    assert 'jobs' in details
    assert 'token_summary' in details
    assert 'cost_summary' in details


def test_get_project_details_invalid():
    """Test project details retrieval with invalid ID."""
    details = workflow.get_project_details(999999)
    assert details is None


def test_get_jobs_list():
    """Test jobs list retrieval."""
    jobs = workflow.get_jobs_list()

    assert len(jobs) > 0
    assert 'job_id' in jobs.columns
    assert 'project_id' in jobs.columns


def test_get_jobs_list_filtered():
    """Test jobs list retrieval with filters."""
    jobs = workflow.get_jobs_list(status='completed')

    assert len(jobs) > 0
    assert all(jobs['status'] == 'completed')


def test_create_new_project_valid():
    """Test creating a new project with valid data."""
    success, message, project_id = workflow.create_new_project(
        "Test Project for Unit Tests",
        "This is a test project"
    )

    assert success is True
    assert project_id is not None
    assert "successfully" in message.lower()


def test_create_new_project_invalid():
    """Test creating a new project with invalid data."""
    success, message, project_id = workflow.create_new_project(
        "AB",  # Too short
        "Description"
    )

    assert success is False
    assert project_id is None


def test_get_model_comparison():
    """Test model comparison data retrieval."""
    comparison = workflow.get_model_comparison()

    assert len(comparison) > 0
    assert 'llm_model' in comparison.columns
    assert 'job_count' in comparison.columns


def test_check_project_budget_status():
    """Test project budget status check."""
    status = workflow.check_project_budget_status(1, budget_limit=100.0)

    assert 'project_id' in status
    assert 'total_cost' in status
    assert 'budget_limit' in status
    assert 'over_budget' in status
    # Check that over_budget is a boolean-like value (True or False)
    assert status['over_budget'] in (True, False)


def test_get_job_efficiency_analysis():
    """Test job efficiency analysis."""
    efficiency = workflow.get_job_efficiency_analysis()

    assert len(efficiency) > 0
    assert 'efficiency_score' in efficiency.columns
    assert 'job_id' in efficiency.columns


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])

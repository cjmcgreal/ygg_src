"""
Tests for runestones_analysis module.
"""

import pytest
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'runestones'))

import runestones_db as db
import runestones_analysis as analysis


@pytest.fixture
def sample_data():
    """Fixture to load sample data for tests."""
    return {
        'projects': db.get_all_projects(),
        'jobs': db.get_all_jobs(),
        'jobs_with_metrics': db.get_jobs_with_metrics()
    }


def test_calculate_overall_stats(sample_data):
    """Test overall statistics calculation."""
    stats = analysis.calculate_overall_stats(sample_data['jobs_with_metrics'])

    assert 'total_jobs' in stats
    assert 'total_tokens' in stats
    assert 'total_cost' in stats
    assert stats['total_jobs'] > 0
    assert stats['total_tokens'] > 0


def test_calculate_project_token_summary(sample_data):
    """Test project token summary calculation."""
    summary = analysis.calculate_project_token_summary(sample_data['jobs_with_metrics'])

    assert isinstance(summary, pd.DataFrame)
    assert 'project_id' in summary.columns
    assert 'total_tokens' in summary.columns
    assert len(summary) > 0


def test_calculate_project_cost_summary(sample_data):
    """Test project cost summary calculation."""
    summary = analysis.calculate_project_cost_summary(sample_data['jobs_with_metrics'])

    assert isinstance(summary, pd.DataFrame)
    assert 'project_id' in summary.columns
    assert 'total_cost' in summary.columns
    assert 'avg_cost_per_job' in summary.columns


def test_calculate_task_summary(sample_data):
    """Test task summary calculation."""
    summary = analysis.calculate_task_summary(sample_data['jobs_with_metrics'])

    assert isinstance(summary, pd.DataFrame)
    assert 'project_id' in summary.columns
    assert 'total_tasks' in summary.columns
    assert 'avg_tasks_per_job' in summary.columns


def test_calculate_model_usage_stats(sample_data):
    """Test model usage statistics calculation."""
    stats = analysis.calculate_model_usage_stats(sample_data['jobs_with_metrics'])

    assert isinstance(stats, pd.DataFrame)
    assert 'llm_model' in stats.columns
    assert 'job_count' in stats.columns
    assert 'total_tokens' in stats.columns


def test_calculate_status_distribution(sample_data):
    """Test status distribution calculation."""
    dist = analysis.calculate_status_distribution(sample_data['jobs'])

    assert isinstance(dist, pd.DataFrame)
    assert 'status' in dist.columns
    assert 'count' in dist.columns
    assert 'percentage' in dist.columns


def test_get_top_projects_by_tokens(sample_data):
    """Test top projects by tokens calculation."""
    top = analysis.get_top_projects_by_tokens(
        sample_data['jobs_with_metrics'],
        sample_data['projects'],
        top_n=3
    )

    assert isinstance(top, pd.DataFrame)
    assert len(top) <= 3
    assert 'project_name' in top.columns
    assert 'total_tokens' in top.columns


def test_get_top_projects_by_cost(sample_data):
    """Test top projects by cost calculation."""
    top = analysis.get_top_projects_by_cost(
        sample_data['jobs_with_metrics'],
        sample_data['projects'],
        top_n=3
    )

    assert isinstance(top, pd.DataFrame)
    assert len(top) <= 3
    assert 'project_name' in top.columns
    assert 'total_cost' in top.columns


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])

"""
Tests for runestones_logic module.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'runestones'))

import runestones_logic as logic


def test_validate_project_name_valid():
    """Test project name validation with valid names."""
    is_valid, error = logic.validate_project_name("Valid Project Name")
    assert is_valid is True
    assert error is None


def test_validate_project_name_too_short():
    """Test project name validation with too short name."""
    is_valid, error = logic.validate_project_name("AB")
    assert is_valid is False
    assert "at least 3 characters" in error


def test_validate_project_name_too_long():
    """Test project name validation with too long name."""
    is_valid, error = logic.validate_project_name("A" * 101)
    assert is_valid is False
    assert "exceed 100 characters" in error


def test_validate_job_data_valid():
    """Test job data validation with valid data."""
    is_valid, error = logic.validate_job_data("Write a blog post about AI", "gpt-4")
    assert is_valid is True
    assert error is None


def test_validate_job_data_short_prompt():
    """Test job data validation with short prompt."""
    is_valid, error = logic.validate_job_data("Short", "gpt-4")
    assert is_valid is False
    assert "at least 10 characters" in error


def test_validate_job_data_invalid_model():
    """Test job data validation with invalid model."""
    is_valid, error = logic.validate_job_data("Valid prompt text", "invalid-model")
    assert is_valid is False
    assert "must be one of" in error


def test_validate_metrics_data_valid():
    """Test metrics validation with valid data."""
    is_valid, error = logic.validate_metrics_data(2500, 3, 500, 2000)
    assert is_valid is True
    assert error is None


def test_validate_metrics_data_negative():
    """Test metrics validation with negative values."""
    is_valid, error = logic.validate_metrics_data(-100, 3, 500, 2000)
    assert is_valid is False
    assert "cannot be negative" in error


def test_calculate_token_cost():
    """Test token cost calculation."""
    cost = logic.calculate_token_cost(10000, 'gpt-4')
    assert cost == 0.600  # 10000 tokens * $0.06 per 1K


def test_determine_job_priority():
    """Test job priority determination."""
    assert logic.determine_job_priority(15, "Regular Project") == 'HIGH'
    assert logic.determine_job_priority(7, "Medium Project") == 'MEDIUM'
    assert logic.determine_job_priority(3, "Regular Project") == 'LOW'
    assert logic.determine_job_priority(2, "Urgent Bug Fix") == 'HIGH'


def test_is_project_over_budget():
    """Test budget checking."""
    assert logic.is_project_over_budget(150.0, 100.0) is True
    assert logic.is_project_over_budget(75.0, 100.0) is False


def test_calculate_efficiency_score():
    """Test efficiency score calculation."""
    score = logic.calculate_efficiency_score(2500, 3)
    assert score == 1.2  # 3 tasks / 2500 tokens * 1000


def test_get_job_status_display():
    """Test status display conversion."""
    assert logic.get_job_status_display('pending') == 'Pending'
    assert logic.get_job_status_display('in_progress') == 'In Progress'
    assert logic.get_job_status_display('completed') == 'Completed'


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v'])

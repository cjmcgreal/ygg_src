"""
Pytest tests for task_selection_logic.py

Tests cover validation, scoring, and business rule functions.
Focused on 2-8 key test cases per requirement.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from task_selection.task_selection_logic import (
    validate_task_data,
    validate_domain_exists,
    validate_bandwidth_allocation,
    calculate_time_breakdown,
    calculate_greedy_score,
    calculate_weighted_score,
    calculate_knapsack_value,
    filter_tasks_by_domain,
    check_domain_constraint
)


# ==============================================================================
# VALIDATION TESTS
# ==============================================================================

def test_validate_task_data_valid():
    """Test validate_task_data with valid inputs."""
    is_valid, msg = validate_task_data("Implement feature", 5.0, 8.0, 1)
    assert is_valid == True
    assert msg == ""


def test_validate_task_data_empty_title():
    """Test validate_task_data catches empty title."""
    is_valid, msg = validate_task_data("", 5.0, 8.0, 1)
    assert is_valid == False
    assert "empty" in msg.lower()


def test_validate_task_data_zero_effort():
    """Test validate_task_data catches zero effort."""
    is_valid, msg = validate_task_data("Task", 0.0, 8.0, 1)
    assert is_valid == False
    assert "positive" in msg.lower()


def test_validate_task_data_negative_value():
    """Test validate_task_data catches negative value."""
    is_valid, msg = validate_task_data("Task", 5.0, -2.0, 1)
    assert is_valid == False
    assert "positive" in msg.lower()


def test_validate_task_data_zero_priority():
    """Test validate_task_data catches zero priority."""
    is_valid, msg = validate_task_data("Task", 5.0, 8.0, 0)
    assert is_valid == False
    assert "positive" in msg.lower() or "integer" in msg.lower()


def test_validate_domain_exists_valid():
    """Test validate_domain_exists with valid domain."""
    domains_df = pd.DataFrame({'name': ['backend', 'frontend']})
    is_valid, msg = validate_domain_exists('backend', domains_df)
    assert is_valid == True
    assert msg == ""


def test_validate_domain_exists_invalid():
    """Test validate_domain_exists catches invalid domain."""
    domains_df = pd.DataFrame({'name': ['backend', 'frontend']})
    is_valid, msg = validate_domain_exists('invalid', domains_df)
    assert is_valid == False
    assert "does not exist" in msg.lower()


# ==============================================================================
# BANDWIDTH ALLOCATION TESTS
# ==============================================================================

def test_validate_bandwidth_allocation_valid():
    """Test validate_bandwidth_allocation with sum of 100%."""
    prefs = {'backend': 40, 'frontend': 60}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    assert is_valid == True
    assert total == 100.0


def test_validate_bandwidth_allocation_invalid_sum():
    """Test validate_bandwidth_allocation catches incorrect sum."""
    prefs = {'backend': 40, 'frontend': 50}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    assert is_valid == False
    assert "100" in msg
    assert total == 90.0


def test_validate_bandwidth_allocation_negative():
    """Test validate_bandwidth_allocation catches negative percentage."""
    prefs = {'backend': -10, 'frontend': 110}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    assert is_valid == False
    assert "negative" in msg.lower()


def test_calculate_time_breakdown():
    """Test calculate_time_breakdown computes correctly."""
    prefs = {'backend': 40, 'frontend': 60}
    breakdown = calculate_time_breakdown(50, prefs, 2.0)

    assert 'backend' in breakdown
    assert 'frontend' in breakdown
    assert breakdown['backend']['percentage'] == 40
    assert breakdown['backend']['story_points'] == 20.0
    assert breakdown['backend']['hours'] == 40.0
    assert breakdown['frontend']['percentage'] == 60
    assert breakdown['frontend']['story_points'] == 30.0
    assert breakdown['frontend']['hours'] == 60.0


# ==============================================================================
# SCORING FUNCTION TESTS
# ==============================================================================

def test_calculate_greedy_score():
    """Test calculate_greedy_score computes value-to-effort ratio."""
    task = {'value': 10, 'effort': 5}
    score = calculate_greedy_score(task)
    assert score == 2.0  # 10 / 5


def test_calculate_greedy_score_zero_effort():
    """Test calculate_greedy_score raises error for zero effort."""
    task = {'value': 10, 'effort': 0}
    with pytest.raises(ValueError):
        calculate_greedy_score(task)


def test_calculate_weighted_score():
    """Test calculate_weighted_score incorporates all factors."""
    task = {'value': 10, 'effort': 5, 'priority': 1}
    score = calculate_weighted_score(task, 60)
    # Expected: (60/100) * 10 * (1/1) / 5 = 0.6 * 10 * 1 / 5 = 1.2
    assert abs(score - 1.2) < 0.001


def test_calculate_weighted_score_priority_effect():
    """Test calculate_weighted_score shows priority effect."""
    task1 = {'value': 10, 'effort': 5, 'priority': 1}
    task2 = {'value': 10, 'effort': 5, 'priority': 2}

    score1 = calculate_weighted_score(task1, 60)
    score2 = calculate_weighted_score(task2, 60)

    # Priority 1 should score higher than priority 2
    assert score1 > score2


def test_calculate_knapsack_value():
    """Test calculate_knapsack_value adjusts for preferences."""
    task = {'value': 10, 'priority': 1}
    value = calculate_knapsack_value(task, 60)
    # Expected: 10 * (60/100) * (1/1) = 6.0
    assert abs(value - 6.0) < 0.001


# ==============================================================================
# FILTERING AND CONSTRAINT TESTS
# ==============================================================================

def test_filter_tasks_by_domain():
    """Test filter_tasks_by_domain returns correct subset."""
    tasks_df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'domain': ['backend', 'frontend', 'backend', 'design', 'backend']
    })

    backend_tasks = filter_tasks_by_domain(tasks_df, 'backend')
    assert len(backend_tasks) == 3
    assert backend_tasks['id'].tolist() == [1, 3, 5]


def test_check_domain_constraint_satisfied():
    """Test check_domain_constraint when constraint is met."""
    selected_tasks = pd.DataFrame({
        'domain': ['backend', 'backend'],
        'effort': [5.0, 8.0]
    })

    is_ok, details = check_domain_constraint(selected_tasks, 'backend', 50, 40)

    assert is_ok == True
    assert details['allocated_time'] == 20.0  # 50% of 40
    assert details['used_time'] == 13.0  # 5 + 8
    assert details['remaining_time'] == 7.0  # 20 - 13


def test_check_domain_constraint_exceeded():
    """Test check_domain_constraint when constraint is exceeded."""
    selected_tasks = pd.DataFrame({
        'domain': ['backend', 'backend'],
        'effort': [15.0, 20.0]
    })

    is_ok, details = check_domain_constraint(selected_tasks, 'backend', 50, 40)

    assert is_ok == False
    assert details['allocated_time'] == 20.0  # 50% of 40
    assert details['used_time'] == 35.0  # 15 + 20
    assert details['remaining_time'] < 0  # Exceeded allocation

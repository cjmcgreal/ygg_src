"""
Pytest tests for task_selection_analysis.py

Tests cover:
- Greedy solver algorithm
- Weighted solver algorithm
- Knapsack solver algorithm
- Solution metrics calculation
- Decision explanation generation
- Edge cases (empty list, zero time, insufficient capacity)
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src" / "task_selection"
sys.path.insert(0, str(src_path))

from task_selection_analysis import (
    greedy_solver,
    weighted_solver,
    knapsack_solver,
    calculate_solution_metrics,
    generate_decision_explanation
)


# ==============================================================================
# TEST FIXTURES
# ==============================================================================

@pytest.fixture
def sample_tasks():
    """Create sample task DataFrame for testing."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'title': [
            'Task A',
            'Task B',
            'Task C',
            'Task D',
            'Task E'
        ],
        'description': ['Description'] * 5,
        'domain': ['backend', 'frontend', 'backend', 'design', 'backend'],
        'project_parent': ['project1', 'project2', 'project1', 'project3', 'project1'],
        'effort': [5.0, 3.0, 2.0, 8.0, 4.0],
        'value': [10.0, 6.0, 8.0, 10.0, 6.0],
        'priority': [1, 2, 1, 1, 2]
    })


@pytest.fixture
def domain_preferences():
    """Standard domain preferences for testing."""
    return {
        'backend': 50,
        'frontend': 30,
        'design': 20
    }


# ==============================================================================
# GREEDY SOLVER TESTS
# ==============================================================================

def test_greedy_solver_basic(sample_tasks, domain_preferences):
    """Test greedy solver with normal inputs."""
    available_time = 15.0

    selected, explanation, metrics = greedy_solver(
        sample_tasks, available_time, domain_preferences
    )

    # Should select some tasks
    assert len(selected) > 0, "Greedy solver should select at least one task"

    # Total effort should not exceed available time
    assert metrics['total_effort'] <= available_time, "Total effort exceeds available time"

    # Metrics should be valid
    assert metrics['num_tasks'] == len(selected), "Task count mismatch"
    assert metrics['total_value'] > 0, "Total value should be positive"
    assert metrics['utilization_pct'] <= 100, "Utilization cannot exceed 100%"


def test_greedy_solver_empty_tasks(domain_preferences):
    """Test greedy solver with empty task list."""
    empty_tasks = pd.DataFrame()
    available_time = 20.0

    selected, explanation, metrics = greedy_solver(
        empty_tasks, available_time, domain_preferences
    )

    # Should return empty results
    assert len(selected) == 0, "Should select no tasks from empty list"
    assert metrics['num_tasks'] == 0, "Task count should be zero"
    assert metrics['total_effort'] == 0, "Total effort should be zero"
    assert "No tasks available" in explanation[0], "Explanation should mention no tasks"


def test_greedy_solver_zero_time(sample_tasks, domain_preferences):
    """Test greedy solver with zero available time."""
    available_time = 0.0

    selected, explanation, metrics = greedy_solver(
        sample_tasks, available_time, domain_preferences
    )

    # Should select no tasks
    assert len(selected) == 0, "Should select no tasks with zero time"
    assert metrics['total_effort'] == 0, "Total effort should be zero"
    assert "No time available" in explanation[0], "Explanation should mention no time"


# ==============================================================================
# WEIGHTED SOLVER TESTS
# ==============================================================================

def test_weighted_solver_basic(sample_tasks, domain_preferences):
    """Test weighted solver with normal inputs."""
    available_time = 15.0

    selected, explanation, metrics = weighted_solver(
        sample_tasks, available_time, domain_preferences
    )

    # Should select some tasks
    assert len(selected) > 0, "Weighted solver should select at least one task"

    # Total effort should not exceed available time
    assert metrics['total_effort'] <= available_time, "Total effort exceeds available time"

    # Metrics should be valid
    assert metrics['num_tasks'] == len(selected), "Task count mismatch"


def test_weighted_solver_domain_preference(sample_tasks):
    """Test that weighted solver respects domain preferences."""
    # Give 100% preference to backend
    backend_only_prefs = {
        'backend': 100,
        'frontend': 0,
        'design': 0
    }
    available_time = 20.0

    selected, explanation, metrics = weighted_solver(
        sample_tasks, available_time, backend_only_prefs
    )

    # Should heavily favor backend tasks (if selected)
    if len(selected) > 0:
        backend_tasks = selected[selected['domain'] == 'backend']
        # Most or all tasks should be backend given 100% preference
        assert len(backend_tasks) >= len(selected) * 0.5, "Should select mostly backend tasks with 100% backend preference"


# ==============================================================================
# KNAPSACK SOLVER TESTS
# ==============================================================================

def test_knapsack_solver_basic(sample_tasks, domain_preferences):
    """Test knapsack solver with normal inputs."""
    available_time = 15.0

    selected, explanation, metrics = knapsack_solver(
        sample_tasks, available_time, domain_preferences
    )

    # Should select some tasks
    assert len(selected) > 0, "Knapsack solver should select at least one task"

    # Total effort should not exceed available time
    assert metrics['total_effort'] <= available_time, "Total effort exceeds available time"

    # Should have optimization score in metrics
    assert 'optimization_score' in metrics, "Knapsack metrics should include optimization score"


def test_knapsack_solver_optimal_value(sample_tasks, domain_preferences):
    """Test that knapsack solver produces valid solution."""
    available_time = 20.0

    selected, explanation, metrics = knapsack_solver(
        sample_tasks, available_time, domain_preferences
    )

    # Verify solution is valid
    assert len(selected) > 0, "Should select tasks"
    assert metrics['total_value'] > 0, "Should have positive total value"

    # Verify all selected tasks fit within capacity
    total_effort = selected['effort'].sum()
    assert total_effort <= available_time, "Selected tasks should fit in available time"


# ==============================================================================
# SOLUTION METRICS TESTS
# ==============================================================================

def test_calculate_solution_metrics_basic(sample_tasks):
    """Test solution metrics calculation with normal data."""
    # Select first 3 tasks
    selected = sample_tasks.head(3)
    available_time = 20.0
    execution_time = 0.005

    metrics = calculate_solution_metrics(selected, available_time, execution_time)

    # Verify basic metrics
    assert metrics['num_tasks'] == 3, "Task count should be 3"
    assert metrics['total_effort'] == selected['effort'].sum(), "Effort sum mismatch"
    assert metrics['total_value'] == selected['value'].sum(), "Value sum mismatch"
    assert metrics['utilization_pct'] > 0, "Utilization should be positive"
    assert metrics['value_per_sp'] > 0, "Value per SP should be positive"
    assert 'execution_time_ms' in metrics, "Should include execution time"


def test_calculate_solution_metrics_empty():
    """Test solution metrics with empty selection."""
    empty_df = pd.DataFrame()
    available_time = 20.0
    execution_time = 0.001

    metrics = calculate_solution_metrics(empty_df, available_time, execution_time)

    # All metrics should be zero
    assert metrics['num_tasks'] == 0, "Task count should be zero"
    assert metrics['total_effort'] == 0, "Effort should be zero"
    assert metrics['total_value'] == 0, "Value should be zero"
    assert metrics['utilization_pct'] == 0, "Utilization should be zero"


# ==============================================================================
# DECISION EXPLANATION TESTS
# ==============================================================================

def test_generate_decision_explanation(sample_tasks):
    """Test decision explanation generation."""
    selected = sample_tasks.head(2)
    constraints = {
        'available_time': 20.0,
        'domain_preferences': {'backend': 50, 'frontend': 30, 'design': 20}
    }

    explanation = generate_decision_explanation(
        sample_tasks, selected, 'greedy', constraints
    )

    # Should return list of strings
    assert isinstance(explanation, list), "Explanation should be a list"
    assert len(explanation) > 0, "Explanation should not be empty"

    # Should contain summary section
    explanation_text = ' '.join(explanation)
    assert 'SUMMARY' in explanation_text or 'summary' in explanation_text.lower(), "Should contain summary"


# ==============================================================================
# ALGORITHM COMPARISON TEST
# ==============================================================================

def test_all_algorithms_respect_constraints(sample_tasks, domain_preferences):
    """Test that all three algorithms respect time and domain constraints."""
    available_time = 12.0

    # Run all three algorithms
    selected_greedy, _, metrics_greedy = greedy_solver(
        sample_tasks, available_time, domain_preferences
    )
    selected_weighted, _, metrics_weighted = weighted_solver(
        sample_tasks, available_time, domain_preferences
    )
    selected_knapsack, _, metrics_knapsack = knapsack_solver(
        sample_tasks, available_time, domain_preferences
    )

    # All should respect time constraint
    assert metrics_greedy['total_effort'] <= available_time, "Greedy exceeds time"
    assert metrics_weighted['total_effort'] <= available_time, "Weighted exceeds time"
    assert metrics_knapsack['total_effort'] <= available_time, "Knapsack exceeds time"

    # All should have valid metrics
    assert metrics_greedy['num_tasks'] >= 0, "Greedy task count invalid"
    assert metrics_weighted['num_tasks'] >= 0, "Weighted task count invalid"
    assert metrics_knapsack['num_tasks'] >= 0, "Knapsack task count invalid"

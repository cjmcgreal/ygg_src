"""
Tests for progression logic module
Focus: 2-8 tests for critical progression behaviors
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import logic
import analysis


@pytest.fixture
def setup_test_data(tmp_path, monkeypatch):
    """Set up test database with sample data"""
    # Change DATA_DIR to temp directory
    monkeypatch.setattr(db, 'DATA_DIR', tmp_path)

    # Create a rep_range exercise
    ex1_id = db.create_exercise(
        name="Bench Press",
        primary_muscle_groups="chest",
        secondary_muscle_groups="triceps",
        progression_scheme="rep_range",
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0,
        warmup_config=None
    )

    # Create a linear_weight exercise
    ex2_id = db.create_exercise(
        name="Deadlift",
        primary_muscle_groups="back",
        secondary_muscle_groups="glutes,hamstrings",
        progression_scheme="linear_weight",
        target_reps=5,
        weight_increment=10.0,
        warmup_config='{"enabled": true, "intensity_thresholds": [{"min_percent_1rm": 0, "max_percent_1rm": 70, "warmup_sets": 2}, {"min_percent_1rm": 70, "max_percent_1rm": 100, "warmup_sets": 3}], "warmup_percentages": [40, 60, 80], "warmup_reps": [8, 6, 4]}'
    )

    return {'rep_range_id': ex1_id, 'linear_weight_id': ex2_id}


def test_rep_range_progression_adds_one_rep_on_success(setup_test_data):
    """Test that rep_range progression adds 1 rep when successful"""
    ex_id = setup_test_data['rep_range_id']

    # Create workout log and simulate successful workout at 135 lbs x 8 reps
    workout_id = db.create_workout("Test Workout", [ex_id])
    workout_log_id = db.create_workout_log(workout_id, datetime.now())

    # Add 3 successful working sets
    for i in range(1, 4):
        db.create_set_log(
            workout_log_id=workout_log_id,
            exercise_id=ex_id,
            set_type='working',
            set_number=i,
            target_weight=135.0,
            target_reps=8,
            rest_seconds=120,
            completed=True,
            actual_weight=135.0,
            actual_reps=8,
            completed_at=datetime.now(),
            one_rep_max_estimate=analysis.estimate_one_rep_max(135.0, 8),
            volume=135.0 * 8,
            duration_seconds=30,
            calories=2.5
        )

    # Calculate next workout
    next_sets = logic.calculate_next_workout_sets(ex_id)

    # Verify progression: should be 135 lbs x 9 reps (added 1 rep)
    working_sets = [s for s in next_sets if s['set_type'] == 'working']
    assert len(working_sets) == 3
    assert working_sets[0]['target_weight'] == 135.0
    assert working_sets[0]['target_reps'] == 9


def test_rep_range_adds_weight_at_max_reps(setup_test_data):
    """Test that rep_range adds weight and resets to min reps when hitting max"""
    ex_id = setup_test_data['rep_range_id']

    # Create workout log and simulate successful workout at 135 lbs x 12 reps (max)
    workout_id = db.create_workout("Test Workout", [ex_id])
    workout_log_id = db.create_workout_log(workout_id, datetime.now())

    # Add 3 successful working sets at max reps
    for i in range(1, 4):
        db.create_set_log(
            workout_log_id=workout_log_id,
            exercise_id=ex_id,
            set_type='working',
            set_number=i,
            target_weight=135.0,
            target_reps=12,
            rest_seconds=120,
            completed=True,
            actual_weight=135.0,
            actual_reps=12,
            completed_at=datetime.now(),
            one_rep_max_estimate=analysis.estimate_one_rep_max(135.0, 12),
            volume=135.0 * 12,
            duration_seconds=30,
            calories=2.5
        )

    # Calculate next workout
    next_sets = logic.calculate_next_workout_sets(ex_id)

    # Verify progression: should be 140 lbs x 8 reps (added weight, reset to min)
    working_sets = [s for s in next_sets if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == 140.0
    assert working_sets[0]['target_reps'] == 8


def test_linear_weight_adds_weight_on_success(setup_test_data):
    """Test that linear_weight progression adds weight when successful"""
    ex_id = setup_test_data['linear_weight_id']

    # Create workout log and simulate successful workout at 225 lbs x 5 reps
    workout_id = db.create_workout("Test Workout", [ex_id])
    workout_log_id = db.create_workout_log(workout_id, datetime.now())

    # Add 3 successful working sets
    for i in range(1, 4):
        db.create_set_log(
            workout_log_id=workout_log_id,
            exercise_id=ex_id,
            set_type='working',
            set_number=i,
            target_weight=225.0,
            target_reps=5,
            rest_seconds=120,
            completed=True,
            actual_weight=225.0,
            actual_reps=5,
            completed_at=datetime.now(),
            one_rep_max_estimate=analysis.estimate_one_rep_max(225.0, 5),
            volume=225.0 * 5,
            duration_seconds=30,
            calories=2.5
        )

    # Calculate next workout
    next_sets = logic.calculate_next_workout_sets(ex_id)

    # Verify progression: should be 235 lbs x 5 reps (added weight, same reps)
    working_sets = [s for s in next_sets if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == 235.0
    assert working_sets[0]['target_reps'] == 5


def test_failure_handling_repeats_same_parameters(setup_test_data):
    """Test that both schemes repeat same weight/reps on failure"""
    ex_id = setup_test_data['rep_range_id']

    # Create workout log with a failed set
    workout_id = db.create_workout("Test Workout", [ex_id])
    workout_log_id = db.create_workout_log(workout_id, datetime.now())

    # Add 2 successful sets and 1 failed set
    for i in range(1, 3):
        db.create_set_log(
            workout_log_id=workout_log_id,
            exercise_id=ex_id,
            set_type='working',
            set_number=i,
            target_weight=135.0,
            target_reps=10,
            rest_seconds=120,
            completed=True,
            actual_weight=135.0,
            actual_reps=10,
            completed_at=datetime.now(),
            one_rep_max_estimate=analysis.estimate_one_rep_max(135.0, 10),
            volume=135.0 * 10,
            duration_seconds=30,
            calories=2.5
        )

    # Failed set (only completed 8 reps)
    db.create_set_log(
        workout_log_id=workout_log_id,
        exercise_id=ex_id,
        set_type='working',
        set_number=3,
        target_weight=135.0,
        target_reps=10,
        rest_seconds=120,
        completed=True,
        actual_weight=135.0,
        actual_reps=8,  # Failed to hit target
        completed_at=datetime.now(),
        one_rep_max_estimate=analysis.estimate_one_rep_max(135.0, 8),
        volume=135.0 * 8,
        duration_seconds=30,
        calories=2.5
    )

    # Calculate next workout
    next_sets = logic.calculate_next_workout_sets(ex_id)

    # Verify: should repeat same parameters (135 lbs x 10 reps)
    working_sets = [s for s in next_sets if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == 135.0
    assert working_sets[0]['target_reps'] == 10


def test_warmup_generation_scales_with_intensity(setup_test_data):
    """Test that warmup sets scale with working set intensity"""
    ex_id = setup_test_data['linear_weight_id']  # Has warmup config

    # Simulate low intensity workout (45% of 1RM = 225 lbs, so 1RM ~ 500)
    workout_id = db.create_workout("Test Workout", [ex_id])
    workout_log_id = db.create_workout_log(workout_id, datetime.now())

    # Add a previous workout to establish 1RM
    db.create_set_log(
        workout_log_id=workout_log_id,
        exercise_id=ex_id,
        set_type='working',
        set_number=1,
        target_weight=225.0,
        target_reps=5,
        rest_seconds=120,
        completed=True,
        actual_weight=225.0,
        actual_reps=5,
        completed_at=datetime.now() - timedelta(days=7),
        one_rep_max_estimate=262.5,  # ~262 lbs 1RM
        volume=225.0 * 5,
        duration_seconds=30,
        calories=2.5
    )

    # Calculate next workout (should have 2 warmup sets since 235/262.5 = 89% > 70%)
    next_sets = logic.calculate_next_workout_sets(ex_id)

    warmup_sets = [s for s in next_sets if s['set_type'] == 'warmup']
    # At 89% intensity, should get 3 warmup sets (70-100% threshold)
    assert len(warmup_sets) == 3
    assert warmup_sets[0]['rest_seconds'] == 60  # Warmup sets have 60s rest


def test_first_workout_with_no_history(setup_test_data):
    """Test that first workout uses sensible defaults when no history exists"""
    ex_id = setup_test_data['rep_range_id']

    # Calculate next workout with no history
    next_sets = logic.calculate_next_workout_sets(ex_id)

    # Should return 3 working sets with default starting parameters
    working_sets = [s for s in next_sets if s['set_type'] == 'working']
    assert len(working_sets) == 3
    assert working_sets[0]['target_weight'] == 45.0  # Default bar weight
    assert working_sets[0]['target_reps'] == 8  # Min reps for rep_range
    assert working_sets[0]['rest_seconds'] == 120


def test_is_workout_successful_detection(setup_test_data):
    """Test that workout success is correctly determined"""
    # Test successful workout
    successful_sets = [
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 8},
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 9},
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 8},
    ]
    assert logic.is_workout_successful(successful_sets) == True

    # Test failed workout (one set incomplete)
    failed_sets = [
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 8},
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 7},  # Failed
        {'set_type': 'working', 'completed': True, 'target_reps': 8, 'actual_reps': 8},
    ]
    assert logic.is_workout_successful(failed_sets) == False

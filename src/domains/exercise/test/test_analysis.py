"""
Focused tests for analysis module
Testing critical calculations: 1RM estimation, weight estimation, latest 1RM query, set metadata calculation
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import analysis
import db


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests"""
    original_data_dir = db.DATA_DIR
    db.DATA_DIR = tmp_path / "data"
    db.DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield db.DATA_DIR
    db.DATA_DIR = original_data_dir


def test_estimate_one_rep_max_with_epley_formula():
    """Test 1RM estimation using Epley formula with known values"""
    # Test case from spec: 225 lbs × 8 reps = 285 lbs 1RM
    one_rm = analysis.estimate_one_rep_max(225.0, 8)
    assert round(one_rm, 2) == 285.0

    # Test case: 100 lbs × 10 reps = 133.33 lbs
    one_rm = analysis.estimate_one_rep_max(100.0, 10)
    assert round(one_rm, 2) == 133.33

    # Edge case: 1 rep should return weight itself
    one_rm = analysis.estimate_one_rep_max(300.0, 1)
    assert one_rm == 300.0


def test_estimate_weight_for_target_reps():
    """Test weight estimation for target reps using inverse formula"""
    # Inverse of 225 lbs × 8 reps = 285 lbs 1RM
    weight = analysis.estimate_weight_for_reps(285.0, 8)
    assert round(weight, 2) == 225.0

    # Edge case: 1 rep should return 1RM
    weight = analysis.estimate_weight_for_reps(300.0, 1)
    assert weight == 300.0


def test_get_latest_one_rep_max_returns_most_recent(temp_data_dir):
    """Test that latest 1RM query returns most recent completed working set"""
    # Create exercise
    ex_id = db.create_exercise(name="Bench Press", progression_scheme="rep_range")

    # Create workout log
    workout_id = db.create_workout(name="Push Day", exercise_ids=[ex_id])
    log_id = db.create_workout_log(workout_id=workout_id, start_time=datetime.now())

    # Create set logs with different 1RM estimates and timestamps
    db.create_set_log(
        workout_log_id=log_id,
        exercise_id=ex_id,
        set_type="working",
        set_number=1,
        target_weight=200.0,
        target_reps=8,
        rest_seconds=120,
        completed=True,
        completed_at=datetime(2025, 1, 1, 10, 0, 0),
        one_rep_max_estimate=253.33
    )

    db.create_set_log(
        workout_log_id=log_id,
        exercise_id=ex_id,
        set_type="working",
        set_number=2,
        target_weight=205.0,
        target_reps=8,
        rest_seconds=120,
        completed=True,
        completed_at=datetime(2025, 1, 1, 10, 5, 0),  # More recent
        one_rep_max_estimate=259.67
    )

    # Should return the most recent 1RM
    latest_1rm = analysis.get_latest_one_rep_max(ex_id)
    assert round(latest_1rm, 2) == 259.67


def test_get_latest_one_rep_max_returns_none_when_no_history(temp_data_dir):
    """Test that latest 1RM returns None when no history exists"""
    ex_id = db.create_exercise(name="Squat", progression_scheme="rep_range")
    latest_1rm = analysis.get_latest_one_rep_max(ex_id)
    assert latest_1rm is None


def test_calculate_set_metadata_for_working_set():
    """Test set metadata calculation includes volume, calories, and 1RM for working sets"""
    metadata = analysis.calculate_set_metadata(
        actual_weight=225.0,
        actual_reps=8,
        duration_seconds=45,
        set_type="working",
        user_body_weight_kg=70.0
    )

    # Volume = weight × reps
    assert metadata['volume'] == 1800.0

    # Calories = MET (5.0) × body_weight_kg × duration_hours
    # 5.0 × 70 × (45/3600) = 4.375
    assert round(metadata['calories'], 2) == 4.38

    # Working set should have 1RM estimate
    assert 'one_rep_max_estimate' in metadata
    assert round(metadata['one_rep_max_estimate'], 2) == 285.0


def test_calculate_set_metadata_for_warmup_set():
    """Test set metadata calculation for warmup sets (no 1RM)"""
    metadata = analysis.calculate_set_metadata(
        actual_weight=135.0,
        actual_reps=8,
        duration_seconds=30,
        set_type="warmup",
        user_body_weight_kg=70.0
    )

    # Should have volume and calories
    assert metadata['volume'] == 1080.0
    assert 'calories' in metadata

    # Warmup set should NOT have 1RM estimate
    assert 'one_rep_max_estimate' not in metadata


def test_calculate_exercise_metadata_aggregates_from_sets():
    """Test exercise metadata aggregates correctly from set list"""
    set_logs = [
        {
            'completed': True,
            'set_type': 'warmup',
            'volume': 1080.0,
            'calories': 2.5,
            'duration_seconds': 30
        },
        {
            'completed': True,
            'set_type': 'working',
            'volume': 1800.0,
            'calories': 4.38,
            'duration_seconds': 45
        },
        {
            'completed': True,
            'set_type': 'working',
            'volume': 1800.0,
            'calories': 4.38,
            'duration_seconds': 45
        },
    ]

    metadata = analysis.calculate_exercise_metadata(set_logs)

    assert metadata['total_volume'] == 4680.0
    assert round(metadata['total_calories'], 2) == 11.26
    assert metadata['total_duration'] == 120
    assert metadata['set_count'] == 3
    assert metadata['working_set_count'] == 2
    assert metadata['warmup_set_count'] == 1


def test_calculate_workout_metadata_with_duration_and_muscle_groups(temp_data_dir):
    """Test workout metadata includes duration, volume, calories, and muscle groups"""
    # Create exercises with different muscle groups
    ex1_id = db.create_exercise(
        name="Bench Press",
        primary_muscle_groups="chest",
        secondary_muscle_groups="triceps,shoulders",
        progression_scheme="rep_range"
    )
    ex2_id = db.create_exercise(
        name="Squat",
        primary_muscle_groups="quadriceps,glutes",
        secondary_muscle_groups="hamstrings",
        progression_scheme="rep_range"
    )

    # Create completed set logs
    set_logs = [
        {
            'completed': True,
            'volume': 1800.0,
            'calories': 4.38,
            'duration_seconds': 45
        },
        {
            'completed': True,
            'volume': 2000.0,
            'calories': 5.0,
            'duration_seconds': 50
        },
    ]

    start_time = datetime(2025, 1, 1, 10, 0, 0)
    end_time = datetime(2025, 1, 1, 11, 15, 0)  # 1 hour 15 minutes

    metadata = analysis.calculate_workout_metadata(
        start_time=start_time,
        end_time=end_time,
        all_set_logs=set_logs,
        exercise_ids=[ex1_id, ex2_id]
    )

    # Duration should be 75 minutes = 4500 seconds
    assert metadata['duration_seconds'] == 4500

    # Total volume and calories
    assert metadata['total_volume'] == 3800.0
    assert round(metadata['total_calories'], 2) == 9.38

    # Total sets
    assert metadata['total_sets'] == 2

    # Muscle groups should be unique and sorted
    muscle_groups = metadata['muscle_groups_trained'].split(',')
    assert 'chest' in muscle_groups
    assert 'quadriceps' in muscle_groups
    assert 'glutes' in muscle_groups
    # Should be sorted
    assert muscle_groups == sorted(muscle_groups)

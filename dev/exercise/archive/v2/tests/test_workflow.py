"""
Tests for workflow orchestration functions
Focus on critical workflows only - 2-8 tests maximum
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import workflow


@pytest.fixture
def clean_db(tmp_path, monkeypatch):
    """Use temporary directory for database during tests"""
    monkeypatch.setattr(db, 'DATA_DIR', tmp_path)
    return tmp_path


def test_handle_create_exercise_validates_and_creates(clean_db):
    """Test that handle_create_exercise validates input and creates exercise"""
    # Valid exercise data
    exercise_data = {
        'name': 'Bench Press',
        'description': 'Upper body push',
        'primary_muscle_groups': 'chest,triceps',
        'secondary_muscle_groups': 'shoulders',
        'progression_scheme': 'linear_weight',
        'target_reps': 5,
        'weight_increment': 5.0
    }

    # Should create successfully
    exercise_id = workflow.handle_create_exercise(exercise_data)
    assert exercise_id == 1

    # Verify exercise exists
    exercise = db.get_exercise_by_id(exercise_id)
    assert exercise is not None
    assert exercise['name'] == 'Bench Press'
    assert exercise['progression_scheme'] == 'linear_weight'


def test_handle_create_exercise_validates_required_fields(clean_db):
    """Test that validation errors raise ValueError"""
    # Missing name
    with pytest.raises(ValueError, match="name"):
        workflow.handle_create_exercise({'name': ''})

    # Missing primary muscle groups
    with pytest.raises(ValueError, match="primary muscle"):
        workflow.handle_create_exercise({
            'name': 'Test Exercise',
            'primary_muscle_groups': ''
        })


def test_handle_create_workout_validates_and_creates(clean_db):
    """Test that handle_create_workout validates and creates workout"""
    # Create an exercise first
    ex_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )

    # Create workout
    workout_id = workflow.handle_create_workout(
        name='Leg Day',
        exercise_ids=[ex_id],
        notes='Focus on form'
    )

    assert workout_id == 1

    # Verify workout exists
    workout = db.get_workout_by_id(workout_id)
    assert workout is not None
    assert workout['name'] == 'Leg Day'
    assert workout['exercise_ids'] == [ex_id]


def test_handle_start_workout_generates_sets_for_all_exercises(clean_db):
    """Test that handle_start_workout generates sets for all exercises"""
    # Create exercises
    ex1_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )
    ex2_id = db.create_exercise(
        name='Bench Press',
        primary_muscle_groups='chest',
        progression_scheme='linear_weight',
        target_reps=5,
        weight_increment=5.0
    )

    # Create workout
    workout_id = db.create_workout('Push/Pull Day', [ex1_id, ex2_id])

    # Start workout
    workout_plan = workflow.handle_start_workout(workout_id)

    # Verify structure
    assert 'workout_log_id' in workout_plan
    assert 'workout_name' in workout_plan
    assert 'exercises' in workout_plan
    assert len(workout_plan['exercises']) == 2

    # Verify each exercise has sets
    for exercise in workout_plan['exercises']:
        assert 'exercise_id' in exercise
        assert 'exercise_name' in exercise
        assert 'sets' in exercise
        assert len(exercise['sets']) > 0  # Should have working sets


def test_handle_complete_workout_saves_all_data_and_calculates_metadata(clean_db):
    """Test that handle_complete_workout saves data at all three levels"""
    # Create exercise
    ex_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps,glutes',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )

    # Create workout
    workout_id = db.create_workout('Leg Day', [ex_id])

    # Create workout log
    start_time = datetime.now()
    workout_log_id = db.create_workout_log(workout_id, start_time, 'in_progress')

    # Simulate set completion data
    set_data = [
        {
            'exercise_id': ex_id,
            'set_type': 'working',
            'set_number': 1,
            'target_weight': 135.0,
            'actual_weight': None,
            'target_reps': 10,
            'actual_reps': None,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        },
        {
            'exercise_id': ex_id,
            'set_type': 'working',
            'set_number': 2,
            'target_weight': 135.0,
            'actual_weight': None,
            'target_reps': 10,
            'actual_reps': None,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        }
    ]

    # Complete workout
    metadata = workflow.handle_complete_workout(workout_log_id, set_data)

    # Verify metadata returned
    assert 'total_volume' in metadata
    assert 'total_calories' in metadata
    assert 'duration_seconds' in metadata
    assert 'total_sets' in metadata
    assert 'muscle_groups_trained' in metadata

    # Verify set logs saved
    saved_sets = db.get_set_logs_for_workout(workout_log_id)
    assert len(saved_sets) == 2

    # Verify workout log updated
    workout_log = db.get_workout_log_by_id(workout_log_id)
    assert workout_log['status'] == 'completed'
    assert workout_log['total_volume'] > 0
    assert workout_log['total_sets'] == 2
    assert 'quadriceps' in workout_log['muscle_groups_trained']


def test_get_workout_history_filters_and_enriches(clean_db):
    """Test that get_workout_history filters and enriches workout logs"""
    # Create exercise and workout
    ex_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )
    workout_id = db.create_workout('Leg Day', [ex_id])

    # Create and complete a workout log
    start_time = datetime.now()
    workout_log_id = db.create_workout_log(workout_id, start_time)
    db.update_workout_log(
        workout_log_id,
        end_time=datetime.now(),
        status='completed',
        total_volume=1000.0,
        total_calories=100.0,
        total_sets=3,
        muscle_groups_trained='quadriceps'
    )

    # Get history
    history = workflow.get_workout_history()

    # Verify enrichment
    assert len(history) == 1
    assert 'workout_name' in history[0]
    assert history[0]['workout_name'] == 'Leg Day'


def test_get_workout_details_returns_workout_with_exercise_info(clean_db):
    """Test that get_workout_details returns complete workout information"""
    # Create exercises
    ex_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )

    # Create workout
    workout_id = db.create_workout('Leg Day', [ex_id], notes='Heavy day')

    # Get details
    details = workflow.get_workout_details(workout_id)

    # Verify structure
    assert details['id'] == workout_id
    assert details['name'] == 'Leg Day'
    assert 'exercises' in details
    assert len(details['exercises']) == 1
    assert details['exercises'][0]['name'] == 'Squat'

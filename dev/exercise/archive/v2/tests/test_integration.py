"""
Integration tests for exercise app - testing complete user workflows
Maximum 10 strategic tests focusing on critical end-to-end flows
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import json

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import db
import logic
import analysis
import workflow


@pytest.fixture
def clean_db(tmp_path, monkeypatch):
    """Use temporary directory for database during tests"""
    monkeypatch.setattr(db, 'DATA_DIR', tmp_path)
    return tmp_path


def test_complete_workout_flow_from_exercise_to_csv(clean_db):
    """
    Test end-to-end flow: create exercise → create workout → start → complete → verify CSV data
    This tests the complete user journey from setup to workout completion
    """
    # Step 1: Create exercise
    exercise_data = {
        'name': 'Barbell Squat',
        'description': 'Compound leg movement',
        'primary_muscle_groups': 'quadriceps,glutes',
        'secondary_muscle_groups': 'hamstrings',
        'progression_scheme': 'rep_range',
        'rep_range_min': 8,
        'rep_range_max': 12,
        'weight_increment': 5.0,
        'warmup_config': None
    }
    exercise_id = workflow.handle_create_exercise(exercise_data)
    assert exercise_id == 1

    # Step 2: Create workout template
    workout_id = workflow.handle_create_workout(
        name='Leg Day A',
        exercise_ids=[exercise_id],
        notes='Focus on form'
    )
    assert workout_id == 1

    # Step 3: Start workout - generates sets
    workout_plan = workflow.handle_start_workout(workout_id)
    assert workout_plan['workout_log_id'] == 1
    assert len(workout_plan['exercises']) == 1
    assert len(workout_plan['exercises'][0]['sets']) == 3  # 3 working sets

    # Step 4: Complete workout with set data
    workout_log_id = workout_plan['workout_log_id']
    start_time = datetime.now()

    # Get the actual target weight from the plan (will be 45 lbs for first workout)
    first_set_weight = workout_plan['exercises'][0]['sets'][0]['target_weight']

    set_data = []
    for i in range(1, 4):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': first_set_weight,
            'actual_weight': None,  # Used target weight
            'target_reps': 8,
            'actual_reps': None,  # Used target reps
            'rest_seconds': 120,
            'completed': True,
            'completed_at': start_time + timedelta(minutes=i*2),
            'duration_seconds': 45
        })

    metadata = workflow.handle_complete_workout(workout_log_id, set_data)

    # Step 5: Verify CSV data integrity
    # Check exercises.csv
    exercises_df = db.load_table('exercises')
    assert len(exercises_df) == 1
    assert exercises_df.iloc[0]['name'] == 'Barbell Squat'

    # Check workouts.csv
    workouts_df = db.load_table('workouts')
    assert len(workouts_df) == 1
    assert workouts_df.iloc[0]['name'] == 'Leg Day A'

    # Check workout_logs.csv
    workout_logs_df = db.load_table('workout_logs')
    assert len(workout_logs_df) == 1
    assert workout_logs_df.iloc[0]['status'] == 'completed'
    assert workout_logs_df.iloc[0]['total_volume'] == first_set_weight * 8 * 3
    assert 'quadriceps' in workout_logs_df.iloc[0]['muscle_groups_trained']

    # Check set_logs.csv
    set_logs_df = db.load_table('set_logs')
    assert len(set_logs_df) == 3
    assert all(set_logs_df['completed'] == True)
    assert all(set_logs_df['exercise_id'] == exercise_id)


def test_rep_range_progression_over_3_workouts(clean_db):
    """
    Test rep range progression over 3 successful workouts
    Should progress: 8 reps → 9 reps → 10 reps (weight stays constant)
    """
    # Setup exercise
    exercise_id = db.create_exercise(
        name='Bench Press',
        primary_muscle_groups='chest',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0,
        warmup_config=None
    )
    workout_id = db.create_workout('Push Day', [exercise_id])

    # Workout 1: First workout starts at bar weight (45 lbs) with min reps (8)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']

    workout1_weight = working_sets[0]['target_weight']
    assert working_sets[0]['target_reps'] == 8  # First workout starts at min

    # Complete workout 1
    set_data = []
    for i, s in enumerate(working_sets, 1):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': s['target_weight'],
            'target_reps': s['target_reps'],
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 2: Should be same weight with 9 reps (added 1 rep)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == workout1_weight
    assert working_sets[0]['target_reps'] == 9

    # Complete workout 2
    set_data = []
    for i, s in enumerate(working_sets, 1):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': s['target_weight'],
            'target_reps': s['target_reps'],
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 3: Should be same weight with 10 reps (added 1 rep)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == workout1_weight
    assert working_sets[0]['target_reps'] == 10


def test_linear_progression_over_3_workouts(clean_db):
    """
    Test linear weight progression over 3 successful workouts
    Should progress weight: 45 → 50 → 55 lbs (constant 5 reps)
    """
    # Setup exercise
    exercise_id = db.create_exercise(
        name='Deadlift',
        primary_muscle_groups='back',
        progression_scheme='linear_weight',
        target_reps=5,
        weight_increment=5.0,
        warmup_config=None
    )
    workout_id = db.create_workout('Pull Day', [exercise_id])

    # Workout 1: First workout starts at bar weight (45 lbs)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    initial_weight = working_sets[0]['target_weight']
    assert working_sets[0]['target_reps'] == 5

    # Complete workout 1
    set_data = []
    for i, s in enumerate(working_sets, 1):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': s['target_weight'],
            'target_reps': s['target_reps'],
            'rest_seconds': 180,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 2: Should add 5 lbs (weight increased, reps constant)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == initial_weight + 5.0
    assert working_sets[0]['target_reps'] == 5

    # Complete workout 2
    set_data = []
    for i, s in enumerate(working_sets, 1):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': s['target_weight'],
            'target_reps': s['target_reps'],
            'rest_seconds': 180,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 3: Should add another 5 lbs
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == initial_weight + 10.0
    assert working_sets[0]['target_reps'] == 5


def test_failure_handling_repeats_parameters(clean_db):
    """
    Test that failed workout (incomplete sets) causes parameters to repeat
    """
    # Setup exercise
    exercise_id = db.create_exercise(
        name='Overhead Press',
        primary_muscle_groups='shoulders',
        progression_scheme='linear_weight',
        target_reps=5,
        weight_increment=5.0,
        warmup_config=None
    )
    workout_id = db.create_workout('Shoulder Day', [exercise_id])

    # Workout 1: Complete successfully
    workout_plan = workflow.handle_start_workout(workout_id)
    workout1_weight = workout_plan['exercises'][0]['sets'][0]['target_weight']

    set_data = []
    for i in range(1, 4):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': workout1_weight,
            'target_reps': 5,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 2: Should progress to workout1_weight + 5 lbs
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    workout2_weight = workout1_weight + 5.0
    assert working_sets[0]['target_weight'] == workout2_weight
    assert working_sets[0]['target_reps'] == 5

    # Fail workout 2 (only complete 2 out of 3 sets)
    set_data = []
    for i in range(1, 3):  # Only complete 2 sets
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': workout2_weight,
            'target_reps': 5,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 45
        })
    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 3: Should repeat workout2_weight (no progression due to failure)
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    assert working_sets[0]['target_weight'] == workout2_weight
    assert working_sets[0]['target_reps'] == 5


def test_warmup_generation_scales_with_intensity(clean_db):
    """
    Test that warmup sets scale based on working set intensity
    High intensity (>70% 1RM) → 3 warmup sets
    """
    # Create exercise with warmup config
    warmup_config = {
        "enabled": True,
        "intensity_thresholds": [
            {"min_percent_1rm": 0, "max_percent_1rm": 50, "warmup_sets": 1},
            {"min_percent_1rm": 50, "max_percent_1rm": 70, "warmup_sets": 2},
            {"min_percent_1rm": 70, "max_percent_1rm": 100, "warmup_sets": 3}
        ],
        "warmup_percentages": [40, 60, 80],
        "warmup_reps": [8, 6, 4]
    }

    exercise_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='linear_weight',
        target_reps=5,
        weight_increment=5.0,
        warmup_config=json.dumps(warmup_config)
    )
    workout_id = db.create_workout('Leg Day', [exercise_id])

    # Establish a high 1RM by completing a heavy workout
    workout_plan = workflow.handle_start_workout(workout_id)
    workout_log_id = workout_plan['workout_log_id']

    # Complete workout at heavy weight (225 lbs x 5 reps)
    set_data = []
    for i in range(1, 4):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': 225.0,
            'actual_weight': 225.0,
            'target_reps': 5,
            'actual_reps': 5,
            'rest_seconds': 180,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 60
        })
    workflow.handle_complete_workout(workout_log_id, set_data)

    # Get 1RM estimate
    one_rm = analysis.get_latest_one_rep_max(exercise_id)
    assert one_rm is not None

    # Next workout: Should have 3 warmup sets (working at ~75% of 1RM)
    workout_plan = workflow.handle_start_workout(workout_id)
    all_sets = workout_plan['exercises'][0]['sets']
    warmup_sets = [s for s in all_sets if s['set_type'] == 'warmup']
    working_sets = [s for s in all_sets if s['set_type'] == 'working']

    # Verify we have 3 warmup sets for high intensity
    assert len(warmup_sets) == 3
    assert warmup_sets[0]['target_reps'] == 8
    assert warmup_sets[1]['target_reps'] == 6
    assert warmup_sets[2]['target_reps'] == 4

    # Verify working sets follow warmups
    assert len(working_sets) == 3
    assert working_sets[0]['target_weight'] == 230.0  # Progressive overload


def test_multi_exercise_workout_progression(clean_db):
    """
    Test workout with multiple exercises progresses each independently
    """
    # Create two exercises with different schemes
    ex1_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0,
        warmup_config=None
    )

    ex2_id = db.create_exercise(
        name='Bench Press',
        primary_muscle_groups='chest',
        progression_scheme='linear_weight',
        target_reps=5,
        weight_increment=5.0,
        warmup_config=None
    )

    # Create workout with both exercises
    workout_id = db.create_workout('Full Body', [ex1_id, ex2_id])

    # Workout 1: Complete both exercises
    workout_plan = workflow.handle_start_workout(workout_id)

    # Verify both exercises have sets
    assert len(workout_plan['exercises']) == 2

    # Get initial weights
    squat_initial_weight = workout_plan['exercises'][0]['sets'][0]['target_weight']
    bench_initial_weight = workout_plan['exercises'][1]['sets'][0]['target_weight']

    # Complete all sets for both exercises
    set_data = []
    for exercise in workout_plan['exercises']:
        for set_info in exercise['sets']:
            if set_info['set_type'] == 'working':
                set_data.append({
                    'exercise_id': exercise['exercise_id'],
                    'set_type': 'working',
                    'set_number': set_info['set_number'],
                    'target_weight': set_info['target_weight'],
                    'target_reps': set_info['target_reps'],
                    'rest_seconds': 120,
                    'completed': True,
                    'completed_at': datetime.now(),
                    'duration_seconds': 45
                })

    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Workout 2: Verify each exercise progressed according to its scheme
    workout_plan = workflow.handle_start_workout(workout_id)

    squat_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']
    bench_sets = [s for s in workout_plan['exercises'][1]['sets'] if s['set_type'] == 'working']

    # Squat should add 1 rep (rep_range scheme), same weight
    assert squat_sets[0]['target_weight'] == squat_initial_weight
    assert squat_sets[0]['target_reps'] == 9

    # Bench should add weight (linear_weight scheme), same reps
    assert bench_sets[0]['target_weight'] == bench_initial_weight + 5.0
    assert bench_sets[0]['target_reps'] == 5


def test_csv_foreign_key_integrity(clean_db):
    """
    Test that all foreign key references are valid after complete workflow
    """
    # Create exercise
    exercise_id = db.create_exercise(
        name='Pull-ups',
        primary_muscle_groups='back',
        progression_scheme='rep_range',
        rep_range_min=5,
        rep_range_max=10,
        weight_increment=2.5,
        warmup_config=None
    )

    # Create workout
    workout_id = db.create_workout('Pull Day', [exercise_id])

    # Start and complete workout
    workout_plan = workflow.handle_start_workout(workout_id)

    set_data = []
    for i in range(1, 4):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': 0.0,  # Bodyweight
            'target_reps': 8,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now(),
            'duration_seconds': 30
        })

    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Load all tables
    exercises_df = db.load_table('exercises')
    workouts_df = db.load_table('workouts')
    workout_logs_df = db.load_table('workout_logs')
    set_logs_df = db.load_table('set_logs')

    # Verify exercises exist
    assert exercise_id in exercises_df['id'].values

    # Verify workout references valid exercise
    workout_row = workouts_df[workouts_df['id'] == workout_id].iloc[0]
    workout_exercise_ids_str = workout_row['exercise_ids']
    # Handle both list and string representations
    if isinstance(workout_exercise_ids_str, list):
        workout_exercise_ids = workout_exercise_ids_str
    else:
        workout_exercise_ids = [int(x) for x in str(workout_exercise_ids_str).split(',')]
    assert exercise_id in workout_exercise_ids

    # Verify workout_log references valid workout
    workout_log_row = workout_logs_df[workout_logs_df['id'] == workout_plan['workout_log_id']].iloc[0]
    assert workout_log_row['workout_id'] == workout_id

    # Verify set_logs reference valid workout_log and exercise
    for _, set_log in set_logs_df.iterrows():
        assert set_log['workout_log_id'] == workout_plan['workout_log_id']
        assert set_log['exercise_id'] == exercise_id
        assert set_log['workout_log_id'] in workout_logs_df['id'].values
        assert set_log['exercise_id'] in exercises_df['id'].values


def test_datetime_fields_parse_correctly(clean_db):
    """
    Test that all datetime fields are stored and loaded correctly
    """
    # Create and complete a workout
    exercise_id = db.create_exercise(
        name='Rows',
        primary_muscle_groups='back',
        progression_scheme='linear_weight',
        target_reps=8,
        weight_increment=5.0,
        warmup_config=None
    )

    workout_id = db.create_workout('Back Day', [exercise_id])
    workout_plan = workflow.handle_start_workout(workout_id)

    start_time = datetime.now()

    set_data = []
    for i in range(1, 4):
        set_data.append({
            'exercise_id': exercise_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': 135.0,
            'target_reps': 8,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': start_time + timedelta(minutes=i*2),
            'duration_seconds': 45
        })

    workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Load tables and verify datetime fields
    exercises_df = db.load_table('exercises')
    assert pd.api.types.is_datetime64_any_dtype(exercises_df['created_at'])

    workouts_df = db.load_table('workouts')
    assert pd.api.types.is_datetime64_any_dtype(workouts_df['created_at'])

    workout_logs_df = db.load_table('workout_logs')
    assert pd.api.types.is_datetime64_any_dtype(workout_logs_df['start_time'])
    assert pd.api.types.is_datetime64_any_dtype(workout_logs_df['end_time'])

    set_logs_df = db.load_table('set_logs')
    assert pd.api.types.is_datetime64_any_dtype(set_logs_df['completed_at'])

    # Verify datetime values are valid and in correct sequence
    workout_log = workout_logs_df.iloc[0]
    assert workout_log['start_time'] <= workout_log['end_time']

    # Check that set completion times are within workout window
    for _, set_log in set_logs_df.iterrows():
        # Allow some tolerance for test execution time
        assert set_log['completed_at'] >= workout_log['start_time'] - timedelta(seconds=1)


def test_metadata_calculation_at_all_three_levels(clean_db):
    """
    Test that metadata is correctly calculated at set, exercise, and workout levels
    """
    # Create two exercises for more comprehensive test
    ex1_id = db.create_exercise(
        name='Squat',
        primary_muscle_groups='quadriceps,glutes',
        secondary_muscle_groups='hamstrings',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0,
        warmup_config=None
    )

    ex2_id = db.create_exercise(
        name='Leg Press',
        primary_muscle_groups='quadriceps',
        secondary_muscle_groups='glutes',
        progression_scheme='rep_range',
        rep_range_min=10,
        rep_range_max=15,
        weight_increment=10.0,
        warmup_config=None
    )

    workout_id = db.create_workout('Leg Day', [ex1_id, ex2_id])
    workout_plan = workflow.handle_start_workout(workout_id)

    # Complete workout with known values
    set_data = []

    # Exercise 1: 3 sets of 225 lbs x 10 reps
    for i in range(1, 4):
        set_data.append({
            'exercise_id': ex1_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': 225.0,
            'target_reps': 10,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now() + timedelta(minutes=i*2),
            'duration_seconds': 60
        })

    # Exercise 2: 3 sets of 315 lbs x 12 reps
    for i in range(1, 4):
        set_data.append({
            'exercise_id': ex2_id,
            'set_type': 'working',
            'set_number': i,
            'target_weight': 315.0,
            'target_reps': 12,
            'rest_seconds': 120,
            'completed': True,
            'completed_at': datetime.now() + timedelta(minutes=10 + i*2),
            'duration_seconds': 60
        })

    metadata = workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Level 1: Set metadata - verify individual sets have volume and 1RM
    set_logs = db.get_set_logs_for_workout(workout_plan['workout_log_id'])

    for set_log in set_logs:
        assert set_log['volume'] > 0
        assert set_log['calories'] > 0
        if set_log['set_type'] == 'working':
            assert set_log['one_rep_max_estimate'] is not None

    # Level 2: Exercise metadata - verify aggregation per exercise
    ex1_sets = [s for s in set_logs if s['exercise_id'] == ex1_id]
    ex1_total_volume = sum(s['volume'] for s in ex1_sets)
    assert ex1_total_volume == 225.0 * 10 * 3  # weight * reps * sets

    ex2_sets = [s for s in set_logs if s['exercise_id'] == ex2_id]
    ex2_total_volume = sum(s['volume'] for s in ex2_sets)
    assert ex2_total_volume == 315.0 * 12 * 3

    # Level 3: Workout metadata - verify total aggregation
    workout_log = db.get_workout_log_by_id(workout_plan['workout_log_id'])

    assert workout_log['total_volume'] == ex1_total_volume + ex2_total_volume
    assert workout_log['total_sets'] == 6  # 3 + 3
    assert workout_log['total_calories'] > 0
    assert workout_log['duration_seconds'] > 0

    # Verify muscle groups aggregated correctly (unique, sorted)
    muscle_groups = workout_log['muscle_groups_trained'].split(',')
    assert 'quadriceps' in muscle_groups
    assert 'glutes' in muscle_groups
    assert 'hamstrings' in muscle_groups

    # Check that muscles are unique
    assert len(muscle_groups) == len(set(muscle_groups))


def test_rep_range_hits_max_then_adds_weight(clean_db):
    """
    Test complete rep range cycle: 8 → 9 → 10 → 11 → 12 → reset to 8 with +5 lbs
    This validates the full progression algorithm over multiple workouts
    """
    exercise_id = db.create_exercise(
        name='Dumbbell Rows',
        primary_muscle_groups='back',
        progression_scheme='rep_range',
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0,
        warmup_config=None
    )
    workout_id = db.create_workout('Back Day', [exercise_id])

    # Track progression through complete cycle
    expected_reps = [8, 9, 10, 11, 12]
    initial_weight = None

    for expected_rep in expected_reps:
        workout_plan = workflow.handle_start_workout(workout_id)
        working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']

        # Capture initial weight on first workout
        if initial_weight is None:
            initial_weight = working_sets[0]['target_weight']

        # Verify expected reps
        assert working_sets[0]['target_reps'] == expected_rep
        assert working_sets[0]['target_weight'] == initial_weight

        # Complete workout successfully
        set_data = []
        for i, s in enumerate(working_sets, 1):
            set_data.append({
                'exercise_id': exercise_id,
                'set_type': 'working',
                'set_number': i,
                'target_weight': s['target_weight'],
                'target_reps': s['target_reps'],
                'rest_seconds': 120,
                'completed': True,
                'completed_at': datetime.now(),
                'duration_seconds': 45
            })
        workflow.handle_complete_workout(workout_plan['workout_log_id'], set_data)

    # Next workout should reset to 8 reps with increased weight
    workout_plan = workflow.handle_start_workout(workout_id)
    working_sets = [s for s in workout_plan['exercises'][0]['sets'] if s['set_type'] == 'working']

    assert working_sets[0]['target_reps'] == 8
    assert working_sets[0]['target_weight'] == initial_weight + 5.0

"""
Workflow orchestration layer
Aggregates frontend actions into complete workflows
All workflows are framework-independent - no Streamlit dependencies
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import db
import logic
import analysis


def handle_create_exercise(exercise_data: Dict[str, Any]) -> int:
    """
    Create a new exercise in the library

    Args:
        exercise_data: Dict with all exercise fields

    Returns:
        New exercise ID

    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    name = exercise_data.get('name', '').strip()
    if not name:
        raise ValueError("Exercise name is required")

    primary_muscle_groups = exercise_data.get('primary_muscle_groups', '').strip()
    if not primary_muscle_groups:
        raise ValueError("At least one primary muscle group is required")

    progression_scheme = exercise_data.get('progression_scheme', 'rep_range')

    # Validate progression scheme specific fields
    if progression_scheme == 'rep_range':
        rep_range_min = exercise_data.get('rep_range_min')
        rep_range_max = exercise_data.get('rep_range_max')

        if rep_range_min is None or rep_range_max is None:
            raise ValueError("Rep range progression requires rep_range_min and rep_range_max")

        if rep_range_min >= rep_range_max:
            raise ValueError("rep_range_min must be less than rep_range_max")

    elif progression_scheme == 'linear_weight':
        target_reps = exercise_data.get('target_reps')

        if target_reps is None:
            raise ValueError("Linear weight progression requires target_reps")

    elif progression_scheme == 'linear_reps':
        target_reps = exercise_data.get('target_reps')
        rep_increment = exercise_data.get('rep_increment')

        if target_reps is None:
            raise ValueError("Linear reps progression requires target_reps (starting reps)")

        if rep_increment is None:
            raise ValueError("Linear reps progression requires rep_increment")

    else:
        raise ValueError(f"Invalid progression scheme: {progression_scheme}")

    # Create exercise using db layer
    exercise_id = db.create_exercise(
        name=exercise_data.get('name'),
        description=exercise_data.get('description', ''),
        primary_muscle_groups=exercise_data.get('primary_muscle_groups', ''),
        secondary_muscle_groups=exercise_data.get('secondary_muscle_groups', ''),
        progression_scheme=exercise_data.get('progression_scheme', 'rep_range'),
        rep_range_min=exercise_data.get('rep_range_min'),
        rep_range_max=exercise_data.get('rep_range_max'),
        target_reps=exercise_data.get('target_reps'),
        rep_increment=exercise_data.get('rep_increment'),
        weight_increment=exercise_data.get('weight_increment'),
        warmup_config=exercise_data.get('warmup_config')
    )

    return exercise_id


def handle_update_exercise(exercise_id: int, exercise_data: Dict[str, Any]) -> bool:
    """
    Update an existing exercise in the library

    Args:
        exercise_id: Exercise ID to update
        exercise_data: Dict with all exercise fields

    Returns:
        True if successful

    Raises:
        ValueError: If validation fails
    """
    # Validate required fields
    name = exercise_data.get('name', '').strip()
    if not name:
        raise ValueError("Exercise name is required")

    primary_muscle_groups = exercise_data.get('primary_muscle_groups', '').strip()
    if not primary_muscle_groups:
        raise ValueError("At least one primary muscle group is required")

    progression_scheme = exercise_data.get('progression_scheme', 'rep_range')

    # Validate progression scheme specific fields
    if progression_scheme == 'rep_range':
        rep_range_min = exercise_data.get('rep_range_min')
        rep_range_max = exercise_data.get('rep_range_max')

        if rep_range_min is None or rep_range_max is None:
            raise ValueError("Rep range progression requires rep_range_min and rep_range_max")

        if rep_range_min >= rep_range_max:
            raise ValueError("rep_range_min must be less than rep_range_max")

    elif progression_scheme == 'linear_weight':
        target_reps = exercise_data.get('target_reps')

        if target_reps is None:
            raise ValueError("Linear weight progression requires target_reps")

    elif progression_scheme == 'linear_reps':
        target_reps = exercise_data.get('target_reps')
        rep_increment = exercise_data.get('rep_increment')

        if target_reps is None:
            raise ValueError("Linear reps progression requires target_reps (starting reps)")

        if rep_increment is None:
            raise ValueError("Linear reps progression requires rep_increment")

    else:
        raise ValueError(f"Invalid progression scheme: {progression_scheme}")

    # Update exercise using db layer
    success = db.update_exercise(
        exercise_id=exercise_id,
        name=exercise_data.get('name'),
        description=exercise_data.get('description', ''),
        primary_muscle_groups=exercise_data.get('primary_muscle_groups', ''),
        secondary_muscle_groups=exercise_data.get('secondary_muscle_groups', ''),
        progression_scheme=exercise_data.get('progression_scheme', 'rep_range'),
        rep_range_min=exercise_data.get('rep_range_min'),
        rep_range_max=exercise_data.get('rep_range_max'),
        target_reps=exercise_data.get('target_reps'),
        rep_increment=exercise_data.get('rep_increment'),
        weight_increment=exercise_data.get('weight_increment'),
        warmup_config=exercise_data.get('warmup_config')
    )

    if not success:
        raise ValueError(f"Exercise with ID {exercise_id} not found")

    return True


def handle_create_workout(
    name: str,
    exercise_ids: List[int],
    notes: str = ""
) -> int:
    """
    Create a new workout template

    Args:
        name: Workout name
        exercise_ids: List of exercise IDs in order
        notes: Optional notes

    Returns:
        New workout ID

    Raises:
        ValueError: If validation fails
    """
    # Validate workout name
    if not name or not name.strip():
        raise ValueError("Workout name is required")

    # Validate exercise list
    if not exercise_ids:
        raise ValueError("At least one exercise is required")

    # Verify all exercises exist
    for ex_id in exercise_ids:
        exercise = db.get_exercise_by_id(ex_id)
        if not exercise:
            raise ValueError(f"Exercise with ID {ex_id} not found")

    # Create workout
    workout_id = db.create_workout(name, exercise_ids, notes)

    return workout_id


def handle_start_workout(workout_id: int) -> Dict[str, Any]:
    """
    Initialize a workout session and generate sets for all exercises

    Args:
        workout_id: Workout template ID

    Returns:
        Dict with workout_log_id, workout_name, and exercises with sets

    Raises:
        ValueError: If workout not found
    """
    # Load workout template
    workout = db.get_workout_by_id(workout_id)
    if not workout:
        raise ValueError(f"Workout with ID {workout_id} not found")

    # Create workout log entry
    start_time = datetime.now()
    workout_log_id = db.create_workout_log(
        workout_id=workout_id,
        start_time=start_time,
        status='in_progress'
    )

    # Generate sets for each exercise
    workout_plan = {
        'workout_log_id': workout_log_id,
        'workout_name': workout['name'],
        'exercises': []
    }

    for exercise_id in workout['exercise_ids']:
        # Get exercise details
        exercise = db.get_exercise_by_id(exercise_id)

        # Generate sets using progression logic
        sets = logic.calculate_next_workout_sets(exercise_id)

        # Get last performance data
        last_performance = db.get_last_exercise_performance(exercise_id)

        workout_plan['exercises'].append({
            'exercise_id': exercise_id,
            'exercise_name': exercise['name'],
            'muscle_groups': exercise['primary_muscle_groups'],
            'sets': sets,
            'last_performance': last_performance
        })

    return workout_plan


def handle_complete_workout(
    workout_log_id: int,
    set_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Complete a workout session and save all data

    Args:
        workout_log_id: Workout log ID
        set_data: List of all set data from workout

    Returns:
        Dict with summary statistics

    Raises:
        ValueError: If workout log not found
    """
    # Get workout log to retrieve start time and workout_id
    workout_log = db.get_workout_log_by_id(workout_log_id)
    if not workout_log:
        raise ValueError(f"Workout log with ID {workout_log_id} not found")

    start_time = workout_log['start_time']
    end_time = datetime.now()

    # Get workout to find exercise IDs
    workout = db.get_workout_by_id(workout_log['workout_id'])
    exercise_ids = workout['exercise_ids']

    # Save each completed set
    for set_info in set_data:
        if set_info['completed']:
            # Determine actual weight and reps (use target if actual not provided)
            actual_weight = set_info.get('actual_weight')
            if actual_weight is None:
                actual_weight = set_info['target_weight']

            actual_reps = set_info.get('actual_reps')
            if actual_reps is None:
                actual_reps = set_info['target_reps']

            # Calculate set metadata
            metadata = analysis.calculate_set_metadata(
                actual_weight=actual_weight,
                actual_reps=actual_reps,
                duration_seconds=set_info['duration_seconds'],
                set_type=set_info['set_type']
            )

            # Save set log
            db.create_set_log(
                workout_log_id=workout_log_id,
                exercise_id=set_info['exercise_id'],
                set_type=set_info['set_type'],
                set_number=set_info['set_number'],
                target_weight=set_info['target_weight'],
                actual_weight=actual_weight if actual_weight != set_info['target_weight'] else None,
                target_reps=set_info['target_reps'],
                actual_reps=actual_reps if actual_reps != set_info['target_reps'] else None,
                rest_seconds=set_info['rest_seconds'],
                completed=True,
                completed_at=set_info['completed_at'],
                one_rep_max_estimate=metadata.get('one_rep_max_estimate'),
                volume=metadata['volume'],
                duration_seconds=set_info['duration_seconds'],
                calories=metadata['calories'],
                notes=set_info.get('notes', '')
            )

    # Get all saved set logs
    all_set_logs = db.get_set_logs_for_workout(workout_log_id)

    # Calculate workout-level metadata
    workout_metadata = analysis.calculate_workout_metadata(
        start_time=start_time,
        end_time=end_time,
        all_set_logs=all_set_logs,
        exercise_ids=exercise_ids
    )

    # Update workout log with metadata
    db.update_workout_log(
        workout_log_id=workout_log_id,
        end_time=end_time,
        status='completed',
        duration_seconds=workout_metadata['duration_seconds'],
        total_volume=workout_metadata['total_volume'],
        total_calories=workout_metadata['total_calories'],
        total_sets=workout_metadata['total_sets'],
        muscle_groups_trained=workout_metadata['muscle_groups_trained']
    )

    return workout_metadata


def get_workout_history(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    workout_id: Optional[int] = None,
    exercise_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get filtered workout history with enriched data

    Args:
        start_date: Filter by start date
        end_date: Filter by end date
        workout_id: Filter by workout template
        exercise_id: Filter by exercise

    Returns:
        List of enriched workout log dicts
    """
    # Query workout logs with basic filters
    workout_logs = db.query_workout_logs(
        start_date=start_date,
        end_date=end_date,
        workout_id=workout_id
    )

    # Convert to list of dicts
    logs_list = workout_logs.to_dict('records')

    # Filter by exercise if specified
    if exercise_id:
        filtered_logs = []
        for log in logs_list:
            set_logs = db.get_set_logs_for_workout(log['id'])
            if any(s['exercise_id'] == exercise_id for s in set_logs):
                filtered_logs.append(log)
        logs_list = filtered_logs

    # Enrich each workout log with workout name
    for log in logs_list:
        workout = db.get_workout_by_id(log['workout_id'])
        if workout:
            log['workout_name'] = workout['name']
        else:
            log['workout_name'] = 'Unknown'

    return logs_list


def get_workout_details(workout_id: int) -> Dict[str, Any]:
    """
    Get workout details with exercise information and last performance

    Args:
        workout_id: Workout template ID

    Returns:
        Dict with workout info and exercise list

    Raises:
        ValueError: If workout not found
    """
    # Get workout template
    workout = db.get_workout_by_id(workout_id)
    if not workout:
        raise ValueError(f"Workout with ID {workout_id} not found")

    # Get details for each exercise
    exercises = []
    for exercise_id in workout['exercise_ids']:
        exercise = db.get_exercise_by_id(exercise_id)
        if exercise:
            # Get last performance
            last_performance = db.get_last_exercise_performance(exercise_id)

            exercises.append({
                'id': exercise['id'],
                'name': exercise['name'],
                'primary_muscle_groups': exercise['primary_muscle_groups'],
                'progression_scheme': exercise['progression_scheme'],
                'last_performance': last_performance
            })

    # Build complete workout details
    details = {
        'id': workout['id'],
        'name': workout['name'],
        'exercise_ids': workout['exercise_ids'],
        'notes': workout.get('notes', ''),
        'created_at': workout['created_at'],
        'exercises': exercises
    }

    return details


def handle_log_old_workout(
    workout_id: int,
    workout_datetime: datetime,
    set_data: List[Dict[str, Any]],
    notes: str = ""
) -> int:
    """
    Log a workout from the past with manual set data

    Args:
        workout_id: Workout template ID
        workout_datetime: When the workout was performed
        set_data: List of set dicts with exercise_id, set_number, weight, reps, set_type
        notes: Optional workout notes

    Returns:
        Workout log ID

    Raises:
        ValueError: If validation fails
    """
    if not set_data:
        raise ValueError("At least one set must be logged")

    # Create workout log
    workout_log_id = db.create_workout_log(
        workout_id=workout_id,
        start_time=workout_datetime,
        status="completed"
    )

    # Create set logs and calculate metadata
    total_volume = 0
    muscle_groups = set()

    for set_info in set_data:
        # Get exercise info for metadata
        exercise = db.get_exercise_by_id(set_info['exercise_id'])
        if exercise:
            muscle_groups.add(exercise['primary_muscle_groups'])

        # Calculate 1RM estimate
        one_rm = analysis.estimate_one_rep_max(
            weight=set_info['weight'],
            reps_completed=set_info['reps']
        )

        # Calculate volume
        volume = set_info['weight'] * set_info['reps']
        total_volume += volume

        # Create set log
        db.create_set_log(
            workout_log_id=workout_log_id,
            exercise_id=set_info['exercise_id'],
            set_type=set_info.get('set_type', 'working'),
            set_number=set_info['set_number'],
            target_weight=set_info['weight'],
            actual_weight=set_info['weight'],
            target_reps=set_info['reps'],
            actual_reps=set_info['reps'],
            rest_seconds=0,  # Unknown for manual entry
            completed=True,
            completed_at=workout_datetime,
            one_rep_max_estimate=one_rm,
            volume=volume,
            notes=set_info.get('notes', '')
        )

    # Calculate total calories (rough estimate)
    total_calories = analysis.estimate_calories_burned(total_volume)

    # Update workout log with metadata
    db.update_workout_log(
        workout_log_id=workout_log_id,
        end_time=workout_datetime,  # Same as start for manual entry
        duration_seconds=0,  # Unknown for manual entry
        total_volume=total_volume,
        total_calories=total_calories,
        total_sets=len(set_data),
        muscle_groups_trained=','.join(muscle_groups),
        status="completed",
        notes=notes
    )

    return workout_log_id

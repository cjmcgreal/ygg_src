"""
Analysis and calculation functions
All calculations are framework-independent - no Streamlit dependencies
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
import db


def estimate_one_rep_max(weight: float, reps_completed: int, formula: str = 'epley') -> float:
    """
    Estimate one-rep max from weight and reps completed

    Args:
        weight: Weight lifted
        reps_completed: Number of reps completed
        formula: "epley" or "brzycki" (default: epley)

    Returns:
        Estimated 1RM rounded to 2 decimals
    """
    if reps_completed == 1:
        return weight

    if formula == 'epley':
        # Epley formula: 1RM = weight × (1 + reps/30)
        one_rm = weight * (1 + reps_completed / 30)
    elif formula == 'brzycki':
        # Brzycki formula: 1RM = weight × (36 / (37 - reps))
        one_rm = weight * (36 / (37 - reps_completed))
    else:
        raise ValueError(f"Unknown formula: {formula}")

    return round(one_rm, 2)


def get_latest_one_rep_max(exercise_id: int) -> Optional[float]:
    """
    Get the most recent 1RM estimate for an exercise

    Args:
        exercise_id: Exercise ID

    Returns:
        Most recent 1RM estimate or None if no history
    """
    set_logs = db.load_table("set_logs")

    # Filter for this exercise, working sets only, completed
    exercise_sets = set_logs[
        (set_logs['exercise_id'] == exercise_id) &
        (set_logs['set_type'] == 'working') &
        (set_logs['completed'] == True)
    ]

    if exercise_sets.empty:
        return None

    # Get most recent by completed_at
    latest = exercise_sets.sort_values('completed_at', ascending=False).iloc[0]
    return latest['one_rep_max_estimate']


def estimate_weight_for_reps(one_rep_max: float, target_reps: int, formula: str = 'epley') -> float:
    """
    Estimate appropriate weight for a target rep count

    Args:
        one_rep_max: Estimated 1RM
        target_reps: Desired rep count
        formula: "epley" or "brzycki" (default: epley)

    Returns:
        Estimated weight rounded to nearest 2.5 lbs
    """
    if target_reps == 1:
        return one_rep_max

    if formula == 'epley':
        # Inverse Epley: weight = one_rep_max / (1 + target_reps/30)
        weight = one_rep_max / (1 + target_reps / 30)
    elif formula == 'brzycki':
        # Inverse Brzycki: weight = one_rep_max × (37 - target_reps) / 36
        weight = one_rep_max * (37 - target_reps) / 36
    else:
        raise ValueError(f"Unknown formula: {formula}")

    # Round to nearest 2.5 lbs for practicality
    return round(weight / 2.5) * 2.5


def calculate_set_metadata(
    actual_weight: float,
    actual_reps: int,
    duration_seconds: int,
    set_type: str,
    user_body_weight_kg: float = 70.0
) -> Dict[str, float]:
    """
    Calculate metadata for a single set

    Args:
        actual_weight: Weight used
        actual_reps: Reps completed
        duration_seconds: Time to complete set
        set_type: "warmup" or "working"
        user_body_weight_kg: User's body weight in kg (default: 70.0)

    Returns:
        Dict with volume, calories, and one_rep_max_estimate (for working sets)
    """
    # Calculate volume: weight × reps
    volume = actual_weight * actual_reps

    # Calculate calories using MET formula
    # MET value for resistance training: 5.0 (moderate to vigorous)
    met = 5.0
    duration_hours = duration_seconds / 3600
    calories = met * user_body_weight_kg * duration_hours

    result = {
        'volume': volume,
        'calories': calories
    }

    # Calculate 1RM only for working sets
    if set_type == 'working':
        result['one_rep_max_estimate'] = estimate_one_rep_max(actual_weight, actual_reps)

    return result


def calculate_exercise_metadata(set_logs: List[Dict]) -> Dict[str, Any]:
    """
    Aggregate metadata for all sets of an exercise

    Args:
        set_logs: List of set log dicts for one exercise

    Returns:
        Dict with aggregated metadata
    """
    completed_sets = [s for s in set_logs if s['completed']]

    total_duration = sum(s['duration_seconds'] for s in completed_sets)
    total_volume = sum(s['volume'] for s in completed_sets)
    total_calories = sum(s['calories'] for s in completed_sets)
    set_count = len(completed_sets)
    working_set_count = len([s for s in completed_sets if s['set_type'] == 'working'])
    warmup_set_count = len([s for s in completed_sets if s['set_type'] == 'warmup'])

    return {
        'total_duration': total_duration,
        'total_volume': total_volume,
        'total_calories': total_calories,
        'set_count': set_count,
        'working_set_count': working_set_count,
        'warmup_set_count': warmup_set_count
    }


def calculate_workout_metadata(
    start_time: datetime,
    end_time: datetime,
    all_set_logs: List[Dict],
    exercise_ids: List[int]
) -> Dict[str, Any]:
    """
    Aggregate metadata for entire workout

    Args:
        start_time: Workout start timestamp
        end_time: Workout end timestamp
        all_set_logs: All set logs for this workout
        exercise_ids: List of exercise IDs in workout

    Returns:
        Dict with workout-level metadata
    """
    # Calculate workout duration
    duration_seconds = int((end_time - start_time).total_seconds())

    # Aggregate from completed sets
    completed_sets = [s for s in all_set_logs if s['completed']]
    total_volume = sum(s['volume'] for s in completed_sets)
    total_calories = sum(s['calories'] for s in completed_sets)
    total_sets = len(completed_sets)

    # Get unique muscle groups from all exercises
    muscle_groups = set()
    for ex_id in exercise_ids:
        exercise = db.get_exercise_by_id(ex_id)
        if exercise:
            # Add primary muscle groups
            primary = exercise.get('primary_muscle_groups', '')
            if primary and not pd.isna(primary):
                primary_list = primary.split(',')
                muscle_groups.update([m.strip() for m in primary_list])

            # Add secondary muscle groups
            secondary = exercise.get('secondary_muscle_groups', '')
            if secondary and not pd.isna(secondary):
                secondary_list = secondary.split(',')
                muscle_groups.update([m.strip() for m in secondary_list])

    # Sort and join muscle groups
    muscle_groups_trained = ','.join(sorted(muscle_groups))

    return {
        'duration_seconds': duration_seconds,
        'total_volume': total_volume,
        'total_calories': total_calories,
        'total_sets': total_sets,
        'muscle_groups_trained': muscle_groups_trained
    }


def estimate_calories_burned(total_volume_lbs: float) -> float:
    """
    Rough estimate of calories burned based on total volume

    Args:
        total_volume_lbs: Total volume (weight × reps) in pounds

    Returns:
        Estimated calories burned

    Note:
        This is a rough approximation. Actual calorie burn depends on many factors
        including duration, intensity, rest periods, and individual metabolism.
        General rule of thumb: ~0.05 calories per pound of volume moved.
    """
    # Rough estimate: 0.05 calories per pound of volume
    # For example: 10,000 lbs of volume ≈ 500 calories
    return round(total_volume_lbs * 0.05, 2)

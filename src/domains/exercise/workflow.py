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

    # Get exercise IDs - either from workout template or derive from set_logs
    if workout_log.get('workout_id') and not pd.isna(workout_log['workout_id']):
        # Template-based workout - get exercise list from template
        workout = db.get_workout_by_id(workout_log['workout_id'])
        exercise_ids = workout['exercise_ids']
    else:
        # Ad-hoc workout - derive exercise list from set_data
        exercise_ids = list(set(s['exercise_id'] for s in set_data))

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
        # Handle NULL/NaN workout_id (ad-hoc workouts)
        if log.get('workout_id') and not pd.isna(log['workout_id']):
            workout = db.get_workout_by_id(log['workout_id'])
            if workout:
                log['workout_name'] = workout['name']
            else:
                log['workout_name'] = 'Unknown Template'
        else:
            # Format: "Manual Entry - YYYY-MM-DD"
            workout_date = pd.to_datetime(log['start_time']).strftime('%Y-%m-%d')
            log['workout_name'] = f'Manual Entry - {workout_date}'

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
    workout_id: Optional[int] = None,
    workout_datetime: datetime = None,
    set_data: List[Dict[str, Any]] = None,
    notes: str = ""
) -> int:
    """
    Log a workout from the past with manual set data

    Args:
        workout_id: Optional workout template ID (None for ad-hoc sets)
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

    # Create workout log (workout_id can be None for ad-hoc logging)
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


# ============================================================================
# TEMPLATE MANAGEMENT WORKFLOWS
# ============================================================================

def handle_create_template(
    name: str,
    label: str,
    slot_definitions: List[Dict[str, Any]],
    notes: str = ""
) -> int:
    """
    Create a new workout template with slot definitions

    Args:
        name: Template name (e.g., "Push Day")
        label: Single letter label (A, B, C, etc.)
        slot_definitions: List of slot dicts with muscle_group, intensity, sets
        notes: Optional notes

    Returns:
        New template ID

    Raises:
        ValueError: If validation fails
    """
    # Validate template name
    if not name or not name.strip():
        raise ValueError("Template name is required")

    # Validate label (single letter)
    if not label or len(label.strip()) != 1:
        raise ValueError("Label must be a single letter (A, B, C, etc.)")

    # Validate slot definitions
    if not slot_definitions:
        raise ValueError("At least one slot definition is required")

    valid_intensities = ['strength', 'hypertrophy', 'endurance']
    for i, slot in enumerate(slot_definitions):
        if not slot.get('muscle_group'):
            raise ValueError(f"Slot {i+1}: muscle_group is required")
        if slot.get('intensity', '').lower() not in valid_intensities:
            raise ValueError(f"Slot {i+1}: intensity must be one of {valid_intensities}")
        if not slot.get('sets') or slot['sets'] < 1:
            slot['sets'] = 3  # Default to 3 sets

        # Add slot_order if not present
        slot['slot_order'] = i + 1

    # Check for duplicate label
    existing = db.get_workout_template_by_label(label)
    if existing:
        raise ValueError(f"A template with label '{label}' already exists")

    # Create template
    template_id = db.create_workout_template(name, label, slot_definitions, notes)

    # Update cycle state to include new template
    state = db.get_cycle_state()
    active_labels = state.get('active_labels', '')
    if active_labels:
        new_labels = active_labels + ',' + label.upper()
    else:
        new_labels = label.upper()
    db.update_cycle_state(active_labels=new_labels)

    return template_id


def handle_update_template(
    template_id: int,
    name: Optional[str] = None,
    label: Optional[str] = None,
    slot_definitions: Optional[List[Dict[str, Any]]] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update an existing workout template

    Args:
        template_id: Template ID to update
        name: Template name
        label: Single letter label
        slot_definitions: List of slot dicts
        notes: Optional notes

    Returns:
        True if successful

    Raises:
        ValueError: If validation fails
    """
    # Get existing template
    template = db.get_workout_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")

    # Validate new label if provided
    if label and label != template['label']:
        existing = db.get_workout_template_by_label(label)
        if existing and existing['id'] != template_id:
            raise ValueError(f"A template with label '{label}' already exists")

        # Update cycle state to reflect label change
        state = db.get_cycle_state()
        active_labels = state.get('active_labels', '')
        labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]

        old_label = template['label']
        if old_label in labels_list:
            idx = labels_list.index(old_label)
            labels_list[idx] = label.upper()
            db.update_cycle_state(active_labels=','.join(labels_list))

    # Update template
    return db.update_workout_template(template_id, name, label, slot_definitions, notes)


def handle_delete_template(template_id: int) -> bool:
    """
    Delete a workout template

    Args:
        template_id: Template ID to delete

    Returns:
        True if successful

    Raises:
        ValueError: If template not found
    """
    template = db.get_workout_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")

    # Remove from cycle state
    state = db.get_cycle_state()
    active_labels = state.get('active_labels', '')
    labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]

    if template['label'] in labels_list:
        labels_list.remove(template['label'])
        current_index = state.get('current_index', 0)

        # Adjust current index if needed
        if current_index >= len(labels_list):
            current_index = 0 if labels_list else 0

        db.update_cycle_state(
            active_labels=','.join(labels_list),
            current_index=current_index
        )

    # Clear exercise selections for this template
    db.clear_selections_for_template(template_id)

    # Delete template
    return db.delete_workout_template(template_id)


# ============================================================================
# CYCLE MANAGEMENT WORKFLOWS
# ============================================================================

def get_next_workout() -> Optional[Dict[str, Any]]:
    """
    Get the current workout from cycle state

    Returns:
        Dict with template info and populated slots, or None if no workouts
    """
    current_label = db.get_current_workout_label()
    if not current_label:
        return None

    template = db.get_workout_template_by_label(current_label)
    if not template:
        return None

    # Get exercise selections for this template
    selections = db.get_selections_for_template(template['id'])
    selection_map = {s['slot_order']: s['exercise_id'] for s in selections}

    # Populate slots with exercise info
    populated_slots = []
    for slot in template.get('slot_definitions', []):
        slot_order = slot.get('slot_order', 0)
        exercise_id = selection_map.get(slot_order)

        populated_slot = slot.copy()
        if exercise_id:
            exercise = db.get_exercise_by_id(exercise_id)
            if exercise:
                populated_slot['exercise'] = exercise
                populated_slot['exercise_id'] = exercise_id

                # Generate sets for this slot
                sets = logic.generate_sets_for_slot(
                    exercise_id,
                    slot.get('intensity', 'hypertrophy'),
                    slot.get('sets', 3)
                )
                populated_slot['generated_sets'] = sets

                # Get last performance
                last_perf = db.get_last_exercise_performance(exercise_id)
                populated_slot['last_performance'] = last_perf

        populated_slots.append(populated_slot)

    return {
        'id': template['id'],
        'name': template['name'],
        'label': template['label'],
        'notes': template.get('notes', ''),
        'slots': populated_slots
    }


def advance_to_next_workout() -> Optional[Dict[str, Any]]:
    """
    Advance to the next workout in cycle and return it

    Returns:
        Dict with next workout info, or None if no workouts
    """
    db.advance_cycle()
    return get_next_workout()


def configure_cycle(active_labels: List[str]) -> bool:
    """
    Configure which workouts are active in the cycle

    Args:
        active_labels: List of workout labels to include in rotation

    Returns:
        True if successful
    """
    # Validate all labels exist
    for label in active_labels:
        template = db.get_workout_template_by_label(label)
        if not template:
            raise ValueError(f"Template with label '{label}' not found")

    # Update cycle state
    labels_str = ','.join(l.upper() for l in active_labels)
    db.update_cycle_state(active_labels=labels_str, current_index=0)

    return True


# ============================================================================
# EXERCISE SELECTION WORKFLOWS
# ============================================================================

def handle_select_exercise_for_slot(
    template_id: int,
    slot_order: int,
    exercise_id: int
) -> int:
    """
    Select an exercise for a template slot

    Args:
        template_id: Template ID
        slot_order: Slot position in template
        exercise_id: Exercise ID to assign

    Returns:
        Selection ID

    Raises:
        ValueError: If validation fails
    """
    # Validate template exists
    template = db.get_workout_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")

    # Validate slot exists
    slots = template.get('slot_definitions', [])
    slot = next((s for s in slots if s.get('slot_order') == slot_order), None)
    if not slot:
        raise ValueError(f"Slot {slot_order} not found in template")

    # Validate exercise exists
    exercise = db.get_exercise_by_id(exercise_id)
    if not exercise:
        raise ValueError(f"Exercise with ID {exercise_id} not found")

    # Set the selection
    return db.set_exercise_for_slot(template_id, slot_order, exercise_id)


def get_exercises_for_muscle_group(muscle_group: str) -> List[Dict[str, Any]]:
    """
    Get all exercises that target a specific muscle group

    Args:
        muscle_group: Muscle group to filter by

    Returns:
        List of exercise dicts
    """
    exercises_df = db.get_all_exercises()
    if exercises_df.empty:
        return []

    # Filter by primary muscle group (case-insensitive partial match)
    mask = exercises_df['primary_muscle_groups'].str.lower().str.contains(
        muscle_group.lower(), na=False
    )
    filtered = exercises_df[mask]

    return filtered.to_dict('records')


# ============================================================================
# MARKDOWN EXPORT/IMPORT WORKFLOWS
# ============================================================================

def generate_workout_markdown(template_id: int) -> str:
    """
    Generate markdown export for a workout template

    Args:
        template_id: Template ID

    Returns:
        Markdown string

    Raises:
        ValueError: If template not found
    """
    # Import markdown utilities
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from markdown_utils import format_workout_markdown, format_goal_string

    template = db.get_workout_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")

    # Get exercise selections
    selections = db.get_selections_for_template(template_id)
    selection_map = {s['slot_order']: s['exercise_id'] for s in selections}

    # Build exercise data for markdown
    exercises = []
    for slot in template.get('slot_definitions', []):
        slot_order = slot.get('slot_order', 0)
        exercise_id = selection_map.get(slot_order)

        if not exercise_id:
            continue  # Skip slots without exercise assigned

        exercise = db.get_exercise_by_id(exercise_id)
        if not exercise:
            continue

        # Generate sets
        intensity = slot.get('intensity', 'hypertrophy')
        num_sets = slot.get('sets', 3)
        sets = logic.generate_sets_for_slot(exercise_id, intensity, num_sets)

        # Get PRs
        pr_1rm = analysis.get_latest_one_rep_max(exercise_id)
        # TODO: Get set and exercise volume PRs from history

        # Format goals
        working_sets = [s for s in sets if s['set_type'] == 'working']
        if working_sets:
            first_working = working_sets[0]
            today_goal = format_goal_string(
                len(working_sets),
                first_working['target_reps'],
                first_working['target_weight']
            )
        else:
            today_goal = "Not set"

        # Get last performances for each set
        last_perf = db.get_last_exercise_performance(exercise_id)
        last_performances = {}
        if last_perf:
            for i, s in enumerate(working_sets, 1):
                last_performances[i] = {
                    'reps': last_perf.get('last_reps', 0),
                    'weight': last_perf.get('last_weight', 0),
                    'date': last_perf.get('last_workout_date')
                }

        exercises.append({
            'exercise_name': exercise['name'],
            'muscle_group': slot.get('muscle_group', exercise.get('primary_muscle_groups', '')),
            'strategic_goal': "Not set",  # TODO: Add strategic goals to data model
            'today_goal': today_goal,
            'pr_1rm': pr_1rm,
            'pr_set_volume': None,
            'pr_exercise_volume': None,
            'sets': sets,
            'last_performances': last_performances
        })

    return format_workout_markdown(template['name'], exercises)


def export_workout_to_file(template_id: int, output_dir: str = None) -> str:
    """
    Export workout to markdown file

    Args:
        template_id: Template ID
        output_dir: Directory to save file (default: data/exports/)

    Returns:
        Path to exported file
    """
    from pathlib import Path

    template = db.get_workout_template_by_id(template_id)
    if not template:
        raise ValueError(f"Template with ID {template_id} not found")

    # Generate markdown content
    markdown_content = generate_workout_markdown(template_id)

    # Determine output directory
    if output_dir:
        export_dir = Path(output_dir)
    else:
        export_dir = Path(__file__).parent / 'data' / 'exports'

    export_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename with date
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = f"{template['label']}_{template['name'].replace(' ', '_')}_{date_str}.md"
    filepath = export_dir / filename

    # Write file
    with open(filepath, 'w') as f:
        f.write(markdown_content)

    return str(filepath)


def import_completed_workout(
    markdown_content: str,
    workout_datetime: datetime = None
) -> int:
    """
    Import a completed workout from markdown

    Only imports sets that are checked off (marked with [x]).
    Creates workout log and set log entries.

    Args:
        markdown_content: Markdown file content
        workout_datetime: When the workout was performed (default: now)

    Returns:
        Workout log ID

    Raises:
        ValueError: If no completed sets found
    """
    # Import markdown utilities
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from markdown_utils import extract_checked_sets

    workout_datetime = workout_datetime or datetime.now()

    # Extract completed sets
    completed_sets = extract_checked_sets(markdown_content)

    if not completed_sets:
        raise ValueError("No completed sets found in markdown (no checkboxes marked [x])")

    # Match exercises by name
    exercises_df = db.get_all_exercises()
    exercise_name_map = {
        row['name'].lower(): row['id']
        for _, row in exercises_df.iterrows()
    }

    # Build set data with exercise IDs
    set_data = []
    unmatched = []

    for set_info in completed_sets:
        exercise_name = set_info['exercise_name'].lower()
        exercise_id = exercise_name_map.get(exercise_name)

        if not exercise_id:
            # Try partial match
            for name, eid in exercise_name_map.items():
                if exercise_name in name or name in exercise_name:
                    exercise_id = eid
                    break

        if not exercise_id:
            unmatched.append(set_info['exercise_name'])
            continue

        set_data.append({
            'exercise_id': exercise_id,
            'set_number': set_info['set_number'],
            'set_type': set_info['set_type'],
            'weight': set_info['weight'],
            'reps': set_info['reps']
        })

    if not set_data:
        raise ValueError(f"Could not match any exercises. Unmatched: {unmatched}")

    # Use existing log_old_workout function
    workout_log_id = handle_log_old_workout(
        workout_id=None,  # Ad-hoc workout
        workout_datetime=workout_datetime,
        set_data=set_data,
        notes=f"Imported from markdown ({len(set_data)} sets)"
    )

    return workout_log_id

"""
Markdown utilities for workout export and import
Handles generation and parsing of workout markdown files with checkbox format
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional


# Standard gym plates in lbs (for plate load calculation)
AVAILABLE_PLATES = [45, 35, 25, 10, 5, 2.5]
BAR_WEIGHT = 45.0  # Standard barbell weight


def calculate_plate_load(total_weight: float, bar_weight: float = BAR_WEIGHT) -> str:
    """
    Calculate plate load per side of barbell

    Takes total weight and subtracts bar weight, then calculates
    which plates are needed per side.

    Args:
        total_weight: Total weight including bar
        bar_weight: Weight of the bar (default: 45 lbs)

    Returns:
        String describing plate load, e.g., "10 + 5 + 2.5 lb per side"
        Returns "0 lb per side" if only bar weight
    """
    weight_per_side = (total_weight - bar_weight) / 2

    if weight_per_side <= 0:
        return "0 lb per side"

    plates_used = []
    remaining = weight_per_side

    for plate in AVAILABLE_PLATES:
        while remaining >= plate:
            plates_used.append(plate)
            remaining -= plate

    if not plates_used:
        return "0 lb per side"

    # Format plate list, combining duplicates
    plate_counts = {}
    for plate in plates_used:
        plate_counts[plate] = plate_counts.get(plate, 0) + 1

    # Build string showing plates
    plate_strs = []
    for plate in AVAILABLE_PLATES:
        count = plate_counts.get(plate, 0)
        if count == 1:
            plate_strs.append(f"{plate}" if plate == int(plate) else f"{plate}")
        elif count > 1:
            plate_strs.append(f"{count}x{plate}" if plate == int(plate) else f"{count}x{plate}")

    return " + ".join(plate_strs) + " lb per side"


def format_exercise_markdown(
    exercise_name: str,
    muscle_group: str,
    strategic_goal: str,
    today_goal: str,
    pr_1rm: Optional[float],
    pr_set_volume: Optional[float],
    pr_exercise_volume: Optional[float],
    sets: List[Dict[str, Any]],
    last_performances: Dict[int, Dict[str, Any]] = None
) -> str:
    """
    Format a single exercise as markdown with checkbox format

    Args:
        exercise_name: Name of exercise
        muscle_group: Primary muscle group
        strategic_goal: Long-term goal (e.g., "3 x 10 x 135 lb")
        today_goal: Today's main set goal (e.g., "3 x 10 x 80 lb")
        pr_1rm: Personal record 1 rep max
        pr_set_volume: Personal record set volume
        pr_exercise_volume: Personal record exercise volume
        sets: List of set dicts with set_type, set_number, target_weight, target_reps
        last_performances: Dict mapping set_number to last performance data

    Returns:
        Formatted markdown string
    """
    lines = []

    # Header
    lines.append(f"**{muscle_group} - {exercise_name}**")

    # Goals and PRs
    lines.append(f"- Strategic Goal: {strategic_goal}")
    lines.append(f"- Goal today: {today_goal}")

    # PRs line
    pr_parts = []
    if pr_1rm:
        pr_parts.append(f"1 RM {pr_1rm:.0f} lb")
    if pr_set_volume:
        pr_parts.append(f"Set Volume: {pr_set_volume:.0f} lb")
    if pr_exercise_volume:
        pr_parts.append(f"Exercise volume: {pr_exercise_volume:.0f} lb")

    if pr_parts:
        lines.append(f"- PRs: {'. '.join(pr_parts)}")

    # Format each set with checkbox
    last_performances = last_performances or {}

    for set_info in sets:
        set_type = set_info.get('set_type', 'working')
        set_number = set_info.get('set_number', 1)
        target_weight = set_info.get('target_weight', 0)
        target_reps = set_info.get('target_reps', 0)

        # Format set type name
        if set_type == 'warmup':
            type_label = f"Warmup set {set_number}"
        elif set_type == 'cooldown':
            type_label = f"Cooldown Set {set_number}"
        else:
            type_label = f"Main Set {set_number}"

        # Calculate plate load
        plate_load = calculate_plate_load(target_weight)

        # Format set details
        set_details = f"{target_reps} x {target_weight:.0f} lb"

        # Build checkbox line
        lines.append(f"- [ ] {type_label}: {set_details}. ({plate_load}).")

        # Add last performance info
        last_perf = last_performances.get(set_number)
        if last_perf:
            last_date = last_perf.get('date', '')
            if isinstance(last_date, datetime):
                last_date = last_date.strftime('%Y-%m-%d')
            last_reps = last_perf.get('reps', 0)
            last_weight = last_perf.get('weight', 0)
            lines.append(f"\t- Last: {last_reps} x {last_weight:.0f} lb ({last_date})")
        else:
            lines.append("\t- New")

    return "\n".join(lines)


def format_workout_markdown(
    workout_name: str,
    exercises: List[Dict[str, Any]],
    workout_date: datetime = None
) -> str:
    """
    Format a complete workout as markdown

    Args:
        workout_name: Name of the workout
        exercises: List of exercise dicts with all data needed for format_exercise_markdown
        workout_date: Date for the frontmatter (default: today)

    Returns:
        Complete markdown document
    """
    workout_date = workout_date or datetime.now()

    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"created: {workout_date.strftime('%Y-%m-%d')}")
    lines.append("---")

    # Format each exercise
    for i, exercise in enumerate(exercises):
        if i > 0:
            lines.append("")  # Blank line between exercises

        exercise_md = format_exercise_markdown(
            exercise_name=exercise.get('exercise_name', 'Unknown'),
            muscle_group=exercise.get('muscle_group', 'Unknown'),
            strategic_goal=exercise.get('strategic_goal', 'Not set'),
            today_goal=exercise.get('today_goal', 'Not set'),
            pr_1rm=exercise.get('pr_1rm'),
            pr_set_volume=exercise.get('pr_set_volume'),
            pr_exercise_volume=exercise.get('pr_exercise_volume'),
            sets=exercise.get('sets', []),
            last_performances=exercise.get('last_performances', {})
        )
        lines.append(exercise_md)

    return "\n".join(lines)


def parse_workout_markdown(content: str) -> List[Dict[str, Any]]:
    """
    Parse markdown file and extract all sets

    Args:
        content: Markdown file content

    Returns:
        List of set dicts with exercise_name, set_type, set_number,
        weight, reps, completed (based on checkbox)
    """
    sets = []
    current_exercise = None

    # Pattern for exercise header: **Muscle Group - Exercise Name**
    exercise_pattern = re.compile(r'\*\*(.+?)\s*-\s*(.+?)\*\*')

    # Pattern for checkbox set: - [x] or - [ ]
    # Captures: checked status, set type/number, reps, weight
    set_pattern = re.compile(
        r'-\s*\[([ xX])\]\s*(.+?):\s*(\d+)\s*x\s*([\d.]+)\s*lb',
        re.IGNORECASE
    )

    for line in content.split('\n'):
        line = line.strip()

        # Check for exercise header
        exercise_match = exercise_pattern.search(line)
        if exercise_match:
            muscle_group = exercise_match.group(1).strip()
            exercise_name = exercise_match.group(2).strip()
            current_exercise = {
                'muscle_group': muscle_group,
                'exercise_name': exercise_name
            }
            continue

        # Check for set line with checkbox
        set_match = set_pattern.search(line)
        if set_match and current_exercise:
            checked = set_match.group(1).lower() == 'x'
            type_info = set_match.group(2).strip().lower()
            reps = int(set_match.group(3))
            weight = float(set_match.group(4))

            # Parse set type and number from type_info
            if 'warmup' in type_info:
                set_type = 'warmup'
            elif 'cooldown' in type_info:
                set_type = 'cooldown'
            else:
                set_type = 'working'

            # Extract set number
            number_match = re.search(r'(\d+)', type_info)
            set_number = int(number_match.group(1)) if number_match else 1

            sets.append({
                'exercise_name': current_exercise['exercise_name'],
                'muscle_group': current_exercise['muscle_group'],
                'set_type': set_type,
                'set_number': set_number,
                'weight': weight,
                'reps': reps,
                'completed': checked
            })

    return sets


def extract_checked_sets(content: str) -> List[Dict[str, Any]]:
    """
    Extract only sets with checked checkboxes from markdown

    Args:
        content: Markdown file content

    Returns:
        List of completed set dicts (only those marked [x])
    """
    all_sets = parse_workout_markdown(content)
    return [s for s in all_sets if s.get('completed', False)]


def format_goal_string(sets: int, reps: int, weight: float) -> str:
    """
    Format a goal string like "3 x 10 x 80 lb"

    Args:
        sets: Number of sets
        reps: Target reps per set
        weight: Target weight

    Returns:
        Formatted goal string
    """
    return f"{sets} x {reps} x {weight:.0f} lb"


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("Testing markdown_utils.py\n")

    # Test plate load calculation
    print("=== Plate Load Calculation ===")
    test_weights = [45, 95, 135, 185, 225, 315]
    for weight in test_weights:
        plate_load = calculate_plate_load(weight)
        print(f"{weight} lb total = {plate_load}")

    # Test exercise markdown formatting
    print("\n=== Exercise Markdown Format ===")
    sample_sets = [
        {'set_type': 'warmup', 'set_number': 1, 'target_weight': 45, 'target_reps': 10},
        {'set_type': 'warmup', 'set_number': 2, 'target_weight': 65, 'target_reps': 8},
        {'set_type': 'working', 'set_number': 1, 'target_weight': 80, 'target_reps': 10},
        {'set_type': 'working', 'set_number': 2, 'target_weight': 80, 'target_reps': 10},
        {'set_type': 'working', 'set_number': 3, 'target_weight': 80, 'target_reps': 10},
    ]

    last_perfs = {
        1: {'reps': 10, 'weight': 80, 'date': '2025-07-28'},
        2: {'reps': 10, 'weight': 80, 'date': '2025-07-28'},
        3: {'reps': 7, 'weight': 80, 'date': '2025-07-28'},
    }

    exercise_md = format_exercise_markdown(
        exercise_name="Barbell Bench Press",
        muscle_group="Chest",
        strategic_goal="3 x 10 x 135 lb",
        today_goal="3 x 10 x 80 lb",
        pr_1rm=140,
        pr_set_volume=950,
        pr_exercise_volume=2000,
        sets=sample_sets,
        last_performances=last_perfs
    )
    print(exercise_md)

    # Test parsing
    print("\n=== Markdown Parsing ===")
    sample_md = """---
created: 2025-11-29
---
**Chest - Barbell Bench Press**
- Strategic Goal: 3 x 10 x 135 lb
- Goal today: 3 x 10 x 80 lb
- PRs: 1 RM 140 lb. Set Volume: 950 lb
- [x] Warmup set 1: 10 x 45 lb. (0 lb per side).
- [ ] Warmup set 2: 8 x 65 lb. (10 lb per side).
- [x] Main Set 1: 10 x 80 lb. (10 + 5 + 2.5 lb per side).
- [x] Main Set 2: 10 x 80 lb. (10 + 5 + 2.5 lb per side).
- [ ] Main Set 3: 10 x 80 lb. (10 + 5 + 2.5 lb per side).
"""

    all_sets = parse_workout_markdown(sample_md)
    print(f"Total sets parsed: {len(all_sets)}")
    for s in all_sets:
        status = "[x]" if s['completed'] else "[ ]"
        print(f"  {status} {s['exercise_name']} - {s['set_type']} {s['set_number']}: {s['reps']} x {s['weight']} lb")

    # Test extract checked only
    print("\n=== Checked Sets Only ===")
    checked = extract_checked_sets(sample_md)
    print(f"Checked sets: {len(checked)}")
    for s in checked:
        print(f"  {s['exercise_name']} - {s['set_type']} {s['set_number']}: {s['reps']} x {s['weight']} lb")

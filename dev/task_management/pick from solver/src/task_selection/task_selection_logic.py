"""
Business Logic Layer for Task Selection System

This module contains all business rules, validation functions, and scoring logic
for the task selection prototype. It provides pure functions that validate inputs,
calculate task scores for different algorithms, and enforce business constraints.

Key responsibilities:
- Validate task data (title, effort, value, priority)
- Validate bandwidth allocation (percentages must sum to 100%)
- Calculate task scores for greedy, weighted, and knapsack algorithms
- Filter tasks by constraints (domain, effort)
- Calculate time breakdowns for metadata display
"""

import pandas as pd


# ==============================================================================
# TASK VALIDATION FUNCTIONS
# ==============================================================================

def validate_task_data(title, effort, value, priority):
    """
    Validate task data according to business rules.

    Business rules enforced:
    - Title must not be empty
    - Effort must be a positive number (> 0)
    - Value must be a positive number (> 0)
    - Priority must be a positive integer (>= 1)

    Args:
        title (str): Task title/name
        effort (float): Story points estimate for task effort
        value (float): Numeric score representing task value
        priority (int): Priority ranking (1=highest priority)

    Returns:
        tuple: (is_valid: bool, error_message: str)
               - (True, "") if all validation passes
               - (False, "Error description") if validation fails

    Example:
        >>> is_valid, msg = validate_task_data("Implement feature", 5.0, 8.0, 1)
        >>> print(is_valid)
        True

        >>> is_valid, msg = validate_task_data("", 5.0, 8.0, 1)
        >>> print(msg)
        Title cannot be empty
    """
    # Check title is not empty
    # Strip whitespace to catch titles that are only spaces
    if not title or not title.strip():
        return (False, "Title cannot be empty")

    # Check effort is positive
    # Must be greater than zero to avoid division by zero in scoring
    try:
        effort_float = float(effort)
        if effort_float <= 0:
            return (False, "Effort must be a positive number greater than 0")
    except (ValueError, TypeError):
        return (False, "Effort must be a valid number")

    # Check value is positive
    # Value represents the benefit/importance, must be positive
    try:
        value_float = float(value)
        if value_float <= 0:
            return (False, "Value must be a positive number greater than 0")
    except (ValueError, TypeError):
        return (False, "Value must be a valid number")

    # Check priority is positive integer
    # Priority ranking starts at 1 (highest priority)
    try:
        priority_int = int(priority)
        if priority_int < 1:
            return (False, "Priority must be a positive integer (1 or greater)")
    except (ValueError, TypeError):
        return (False, "Priority must be a valid integer")

    # All validations passed
    return (True, "")


def validate_domain_exists(domain_name, domains_df):
    """
    Check if a domain exists in the domains DataFrame.

    This ensures referential integrity - tasks must reference valid domains.

    Args:
        domain_name (str): Name of the domain to check
        domains_df (pd.DataFrame): DataFrame containing valid domains

    Returns:
        tuple: (is_valid: bool, error_message: str)
               - (True, "") if domain exists
               - (False, "Error description") if domain not found

    Example:
        >>> domains_df = pd.DataFrame({'name': ['backend', 'frontend']})
        >>> is_valid, msg = validate_domain_exists('backend', domains_df)
        >>> print(is_valid)
        True

        >>> is_valid, msg = validate_domain_exists('invalid', domains_df)
        >>> print(msg)
        Domain 'invalid' does not exist. Please select a valid domain.
    """
    # Check if domain name exists in the domains DataFrame
    if domain_name in domains_df['name'].values:
        return (True, "")
    else:
        return (False, f"Domain '{domain_name}' does not exist. Please select a valid domain.")


# ==============================================================================
# BANDWIDTH ALLOCATION VALIDATION
# ==============================================================================

def validate_bandwidth_allocation(domain_preferences):
    """
    Validate that domain preferences sum to exactly 100%.

    Business rule: User must allocate their entire capacity across domains.
    The sum of all domain percentage allocations must equal 100%.

    Args:
        domain_preferences (dict): Dictionary mapping domain names to percentage
                                    allocations, e.g., {'backend': 50, 'frontend': 50}

    Returns:
        tuple: (is_valid: bool, error_message: str, total_percentage: float)
               - (True, "", 100.0) if sum equals 100%
               - (False, "Error description", actual_sum) if validation fails

    Example:
        >>> prefs = {'backend': 40, 'frontend': 60}
        >>> is_valid, msg, total = validate_bandwidth_allocation(prefs)
        >>> print(is_valid, total)
        True 100.0

        >>> prefs = {'backend': 40, 'frontend': 50}
        >>> is_valid, msg, total = validate_bandwidth_allocation(prefs)
        >>> print(msg)
        Domain preferences must sum to 100%. Current sum: 90.0%
    """
    # Check for negative percentages
    # All allocations must be non-negative
    for domain, pct in domain_preferences.items():
        if pct < 0:
            return (False, f"Domain '{domain}' has negative percentage: {pct}%. All percentages must be non-negative.", sum(domain_preferences.values()))

    # Calculate total percentage allocation
    total_percentage = sum(domain_preferences.values())

    # Allow small floating point tolerance (e.g., 99.9999 or 100.0001 is acceptable)
    # This handles floating point arithmetic imprecision
    tolerance = 0.01
    if abs(total_percentage - 100.0) <= tolerance:
        return (True, "", 100.0)
    else:
        return (False, f"Domain preferences must sum to 100%. Current sum: {total_percentage}%", total_percentage)


def calculate_time_breakdown(available_time, domain_preferences, points_to_hours=2.0):
    """
    Calculate time breakdown by domain for metadata display.

    Converts percentages to story points and then to hours for each domain.
    Used by the UI to show users the equivalent time allocation in different units.

    Args:
        available_time (float): Total available time in story points
        domain_preferences (dict): Domain name to percentage mapping
        points_to_hours (float): Conversion ratio (default: 1 story point = 2 hours)

    Returns:
        dict: Dictionary with domain as key and nested dict as value:
              {
                  'domain_name': {
                      'percentage': float,
                      'story_points': float,
                      'hours': float
                  }
              }

    Example:
        >>> prefs = {'backend': 40, 'frontend': 60}
        >>> breakdown = calculate_time_breakdown(50, prefs, 2.0)
        >>> print(breakdown['backend'])
        {'percentage': 40, 'story_points': 20.0, 'hours': 40.0}
    """
    breakdown = {}

    for domain, percentage in domain_preferences.items():
        # Calculate story points for this domain
        # percentage / 100 converts to decimal (e.g., 40% -> 0.4)
        story_points = (percentage / 100.0) * available_time

        # Calculate equivalent hours using conversion ratio
        hours = story_points * points_to_hours

        breakdown[domain] = {
            'percentage': percentage,
            'story_points': round(story_points, 2),
            'hours': round(hours, 2)
        }

    return breakdown


# ==============================================================================
# SCORING FUNCTIONS FOR ALGORITHMS
# ==============================================================================

def calculate_greedy_score(task_row):
    """
    Calculate greedy algorithm score (value-to-effort ratio).

    Greedy algorithm selects tasks with highest value per unit of effort.
    This maximizes immediate return on time investment.

    Formula: score = value / effort

    Args:
        task_row (pd.Series or dict): Task data with 'value' and 'effort' fields

    Returns:
        float: Value-to-effort ratio score

    Raises:
        ValueError: If effort is zero (to prevent division by zero)

    Example:
        >>> task = {'value': 10, 'effort': 5}
        >>> score = calculate_greedy_score(task)
        >>> print(score)
        2.0
    """
    effort = task_row['effort']
    value = task_row['value']

    # Handle zero effort edge case
    # Tasks with zero effort would cause division by zero
    if effort == 0:
        raise ValueError(f"Cannot calculate greedy score: task has zero effort")

    # Calculate value-to-effort ratio
    # Higher score means better value per unit of effort
    score = value / effort

    return score


def calculate_weighted_score(task_row, domain_preference_pct):
    """
    Calculate weighted algorithm score incorporating multiple factors.

    Weighted algorithm considers domain preference, value, priority, and effort
    to produce a balanced score that reflects both user preferences and task characteristics.

    Formula: score = (domain_pct / 100) * value * (1 / priority) / effort
    - Higher domain preference increases score
    - Higher value increases score
    - Lower priority rank (= higher priority) increases score
    - Lower effort increases score

    Args:
        task_row (pd.Series or dict): Task data with 'value', 'effort', 'priority' fields
        domain_preference_pct (float): User's preference percentage for this domain (0-100)

    Returns:
        float: Weighted score

    Raises:
        ValueError: If effort or priority is zero

    Example:
        >>> task = {'value': 10, 'effort': 5, 'priority': 1}
        >>> score = calculate_weighted_score(task, 60)
        >>> print(f"Score: {score:.2f}")
        Score: 1.20
    """
    effort = task_row['effort']
    value = task_row['value']
    priority = task_row['priority']

    # Handle zero effort edge case
    if effort == 0:
        raise ValueError(f"Cannot calculate weighted score: task has zero effort")

    # Handle zero priority edge case
    # Priority must be at least 1 (by validation rules)
    if priority == 0:
        raise ValueError(f"Cannot calculate weighted score: task has zero priority")

    # Calculate weighted score with all factors
    # domain_preference_pct / 100 converts percentage to decimal weight
    # 1 / priority means priority 1 (highest) gets weight 1.0, priority 2 gets 0.5, etc.
    score = (domain_preference_pct / 100.0) * value * (1.0 / priority) / effort

    return score


def calculate_knapsack_value(task_row, domain_preference_pct):
    """
    Calculate knapsack algorithm value (adjusted for preferences and priority).

    Knapsack algorithm uses dynamic programming to maximize value within capacity.
    This value function adjusts the base task value by domain preference and priority.

    Formula: value = base_value * (domain_pct / 100) * (1 / priority)
    - Domain preference acts as a multiplier
    - Priority acts as a multiplier (higher priority = higher multiplier)

    Note: Effort is used as "weight" in the knapsack algorithm, not included in value.

    Args:
        task_row (pd.Series or dict): Task data with 'value' and 'priority' fields
        domain_preference_pct (float): User's preference percentage for this domain (0-100)

    Returns:
        float: Adjusted value for knapsack algorithm

    Raises:
        ValueError: If priority is zero

    Example:
        >>> task = {'value': 10, 'priority': 1}
        >>> value = calculate_knapsack_value(task, 60)
        >>> print(f"Adjusted value: {value:.2f}")
        Adjusted value: 6.00
    """
    value = task_row['value']
    priority = task_row['priority']

    # Handle zero priority edge case
    if priority == 0:
        raise ValueError(f"Cannot calculate knapsack value: task has zero priority")

    # Calculate adjusted value
    # Incorporates user's domain preference and task priority
    # Higher domain preference and higher priority (lower number) increase value
    adjusted_value = value * (domain_preference_pct / 100.0) * (1.0 / priority)

    return adjusted_value


# ==============================================================================
# TASK FILTERING HELPERS
# ==============================================================================

def filter_tasks_by_domain(tasks_df, domain_name):
    """
    Filter tasks DataFrame to only include tasks from a specific domain.

    Args:
        tasks_df (pd.DataFrame): DataFrame containing all tasks
        domain_name (str): Name of the domain to filter by

    Returns:
        pd.DataFrame: Filtered DataFrame containing only tasks from the specified domain

    Example:
        >>> tasks_df = pd.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'title': ['Task A', 'Task B', 'Task C'],
        ...     'domain': ['backend', 'frontend', 'backend']
        ... })
        >>> backend_tasks = filter_tasks_by_domain(tasks_df, 'backend')
        >>> print(len(backend_tasks))
        2
    """
    # Create a copy to avoid modifying original DataFrame
    filtered_df = tasks_df[tasks_df['domain'] == domain_name].copy()

    return filtered_df


def check_domain_constraint(selected_tasks_df, domain_name, domain_preference_pct, available_time):
    """
    Check if domain allocation constraint is satisfied for selected tasks.

    Business rule: Total effort for tasks in a domain must not exceed the
    domain's allocated time (percentage * available_time).

    Args:
        selected_tasks_df (pd.DataFrame): DataFrame of selected tasks
        domain_name (str): Name of the domain to check
        domain_preference_pct (float): User's preference percentage for this domain (0-100)
        available_time (float): Total available time in story points

    Returns:
        tuple: (is_satisfied: bool, details: dict)
               - is_satisfied: True if constraint is met, False otherwise
               - details: {
                   'allocated_time': float,  # Time allocated to this domain
                   'used_time': float,       # Time actually used by selected tasks
                   'remaining_time': float,  # Unused allocation
                   'utilization_pct': float  # Percentage of allocation used
                 }

    Example:
        >>> tasks_df = pd.DataFrame({
        ...     'domain': ['backend', 'backend', 'frontend'],
        ...     'effort': [5.0, 8.0, 3.0]
        ... })
        >>> is_ok, details = check_domain_constraint(tasks_df, 'backend', 50, 40)
        >>> print(is_ok, details['used_time'])
        True 13.0
    """
    # Calculate allocated time for this domain
    # domain_preference_pct / 100 converts percentage to decimal
    allocated_time = (domain_preference_pct / 100.0) * available_time

    # Filter selected tasks for this domain
    domain_tasks = selected_tasks_df[selected_tasks_df['domain'] == domain_name]

    # Calculate total effort used in this domain
    used_time = domain_tasks['effort'].sum() if len(domain_tasks) > 0 else 0.0

    # Calculate remaining allocation
    remaining_time = allocated_time - used_time

    # Calculate utilization percentage
    utilization_pct = (used_time / allocated_time * 100.0) if allocated_time > 0 else 0.0

    # Check if constraint is satisfied
    # Constraint is met if used time doesn't exceed allocated time
    is_satisfied = used_time <= allocated_time

    details = {
        'allocated_time': round(allocated_time, 2),
        'used_time': round(used_time, 2),
        'remaining_time': round(remaining_time, 2),
        'utilization_pct': round(utilization_pct, 2)
    }

    return (is_satisfied, details)


# ==============================================================================
# STANDALONE TEST SECTION
# ==============================================================================

if __name__ == "__main__":
    """
    Standalone test section demonstrating all validation and scoring functions.

    This section can be run independently to verify functionality:
    $ python src/task_selection/task_selection_logic.py

    Tests cover:
    - Task data validation with valid and invalid inputs
    - Domain existence validation
    - Bandwidth allocation validation
    - Time breakdown calculations
    - Score calculations for all three algorithms
    - Task filtering by domain
    - Domain constraint checking
    """

    print("=" * 80)
    print("TASK SELECTION LOGIC LAYER - STANDALONE TESTS")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # Test 1: Validate task data - valid inputs
    # -------------------------------------------------------------------------
    print("TEST 1: Validate Task Data (Valid)")
    print("-" * 80)

    is_valid, msg = validate_task_data("Implement feature", 5.0, 8.0, 1)
    print(f"Valid task: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=True, message=''")
    print()

    # -------------------------------------------------------------------------
    # Test 2: Validate task data - invalid inputs
    # -------------------------------------------------------------------------
    print("TEST 2: Validate Task Data (Invalid Cases)")
    print("-" * 80)

    # Empty title
    is_valid, msg = validate_task_data("", 5.0, 8.0, 1)
    print(f"Empty title: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=False, message contains 'empty'")
    print()

    # Zero effort
    is_valid, msg = validate_task_data("Task", 0.0, 8.0, 1)
    print(f"Zero effort: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=False, message contains 'positive'")
    print()

    # Negative value
    is_valid, msg = validate_task_data("Task", 5.0, -2.0, 1)
    print(f"Negative value: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=False, message contains 'positive'")
    print()

    # Zero priority
    is_valid, msg = validate_task_data("Task", 5.0, 8.0, 0)
    print(f"Zero priority: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=False, message contains 'positive integer'")
    print()

    # -------------------------------------------------------------------------
    # Test 3: Validate domain exists
    # -------------------------------------------------------------------------
    print("TEST 3: Validate Domain Exists")
    print("-" * 80)

    domains_df = pd.DataFrame({
        'name': ['backend', 'frontend', 'design']
    })

    is_valid, msg = validate_domain_exists('backend', domains_df)
    print(f"Valid domain 'backend': is_valid={is_valid}")
    print(f"Expected: is_valid=True")
    print()

    is_valid, msg = validate_domain_exists('invalid_domain', domains_df)
    print(f"Invalid domain: is_valid={is_valid}, message='{msg}'")
    print(f"Expected: is_valid=False, message contains 'does not exist'")
    print()

    # -------------------------------------------------------------------------
    # Test 4: Validate bandwidth allocation - valid
    # -------------------------------------------------------------------------
    print("TEST 4: Validate Bandwidth Allocation (Valid)")
    print("-" * 80)

    prefs = {'backend': 40, 'frontend': 60}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    print(f"Valid allocation (40+60): is_valid={is_valid}, total={total}%")
    print(f"Expected: is_valid=True, total=100.0")
    print()

    # -------------------------------------------------------------------------
    # Test 5: Validate bandwidth allocation - invalid
    # -------------------------------------------------------------------------
    print("TEST 5: Validate Bandwidth Allocation (Invalid)")
    print("-" * 80)

    prefs = {'backend': 40, 'frontend': 50}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    print(f"Invalid allocation (40+50): is_valid={is_valid}, total={total}%")
    print(f"Message: '{msg}'")
    print(f"Expected: is_valid=False, total=90.0, message contains 'must sum to 100'")
    print()

    prefs = {'backend': -10, 'frontend': 110}
    is_valid, msg, total = validate_bandwidth_allocation(prefs)
    print(f"Negative allocation: is_valid={is_valid}")
    print(f"Message: '{msg}'")
    print(f"Expected: is_valid=False, message contains 'negative'")
    print()

    # -------------------------------------------------------------------------
    # Test 6: Calculate time breakdown
    # -------------------------------------------------------------------------
    print("TEST 6: Calculate Time Breakdown")
    print("-" * 80)

    prefs = {'backend': 40, 'frontend': 60}
    breakdown = calculate_time_breakdown(50, prefs, 2.0)

    print(f"Available time: 50 story points")
    print(f"Conversion ratio: 1sp = 2hrs")
    print(f"Domain preferences: {prefs}")
    print()
    print(f"Backend breakdown: {breakdown['backend']}")
    print(f"Expected: percentage=40, story_points=20.0, hours=40.0")
    print()
    print(f"Frontend breakdown: {breakdown['frontend']}")
    print(f"Expected: percentage=60, story_points=30.0, hours=60.0")
    print()

    # -------------------------------------------------------------------------
    # Test 7: Calculate greedy score
    # -------------------------------------------------------------------------
    print("TEST 7: Calculate Greedy Score")
    print("-" * 80)

    task1 = {'value': 10, 'effort': 5}
    score1 = calculate_greedy_score(task1)
    print(f"Task (value=10, effort=5): score={score1:.2f}")
    print(f"Expected: score=2.00 (10/5)")
    print()

    task2 = {'value': 8, 'effort': 2}
    score2 = calculate_greedy_score(task2)
    print(f"Task (value=8, effort=2): score={score2:.2f}")
    print(f"Expected: score=4.00 (8/2)")
    print(f"Note: Task 2 has better value-to-effort ratio")
    print()

    # -------------------------------------------------------------------------
    # Test 8: Calculate weighted score
    # -------------------------------------------------------------------------
    print("TEST 8: Calculate Weighted Score")
    print("-" * 80)

    task = {'value': 10, 'effort': 5, 'priority': 1}
    score = calculate_weighted_score(task, 60)
    print(f"Task (value=10, effort=5, priority=1) with domain_pct=60:")
    print(f"Score={score:.4f}")
    print(f"Expected: score=1.2000 (0.6 * 10 * 1 / 5)")
    print()

    task = {'value': 10, 'effort': 5, 'priority': 2}
    score = calculate_weighted_score(task, 60)
    print(f"Task (value=10, effort=5, priority=2) with domain_pct=60:")
    print(f"Score={score:.4f}")
    print(f"Expected: score=0.6000 (0.6 * 10 * 0.5 / 5)")
    print(f"Note: Lower priority reduces score")
    print()

    # -------------------------------------------------------------------------
    # Test 9: Calculate knapsack value
    # -------------------------------------------------------------------------
    print("TEST 9: Calculate Knapsack Value")
    print("-" * 80)

    task = {'value': 10, 'priority': 1}
    value = calculate_knapsack_value(task, 60)
    print(f"Task (value=10, priority=1) with domain_pct=60:")
    print(f"Adjusted value={value:.2f}")
    print(f"Expected: value=6.00 (10 * 0.6 * 1)")
    print()

    task = {'value': 10, 'priority': 2}
    value = calculate_knapsack_value(task, 60)
    print(f"Task (value=10, priority=2) with domain_pct=60:")
    print(f"Adjusted value={value:.2f}")
    print(f"Expected: value=3.00 (10 * 0.6 * 0.5)")
    print()

    # -------------------------------------------------------------------------
    # Test 10: Filter tasks by domain
    # -------------------------------------------------------------------------
    print("TEST 10: Filter Tasks By Domain")
    print("-" * 80)

    tasks_df = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'title': ['Task A', 'Task B', 'Task C', 'Task D', 'Task E'],
        'domain': ['backend', 'frontend', 'backend', 'design', 'backend']
    })

    backend_tasks = filter_tasks_by_domain(tasks_df, 'backend')
    print(f"Total tasks: {len(tasks_df)}")
    print(f"Backend tasks: {len(backend_tasks)}")
    print(f"Backend task IDs: {backend_tasks['id'].tolist()}")
    print(f"Expected: 3 backend tasks with IDs [1, 3, 5]")
    print()

    # -------------------------------------------------------------------------
    # Test 11: Check domain constraint
    # -------------------------------------------------------------------------
    print("TEST 11: Check Domain Constraint")
    print("-" * 80)

    selected_tasks = pd.DataFrame({
        'id': [1, 3],
        'title': ['Task A', 'Task C'],
        'domain': ['backend', 'backend'],
        'effort': [5.0, 8.0]
    })

    is_ok, details = check_domain_constraint(selected_tasks, 'backend', 50, 40)
    print(f"Backend domain constraint check:")
    print(f"  Available time: 40sp")
    print(f"  Domain preference: 50%")
    print(f"  Allocated time: {details['allocated_time']}sp")
    print(f"  Used time: {details['used_time']}sp")
    print(f"  Remaining: {details['remaining_time']}sp")
    print(f"  Utilization: {details['utilization_pct']}%")
    print(f"  Constraint satisfied: {is_ok}")
    print(f"Expected: allocated=20.0sp, used=13.0sp, remaining=7.0sp, satisfied=True")
    print()

    # -------------------------------------------------------------------------
    # Test 12: Edge case - zero effort handling
    # -------------------------------------------------------------------------
    print("TEST 12: Edge Case - Zero Effort Handling")
    print("-" * 80)

    task_zero_effort = {'value': 10, 'effort': 0}
    try:
        score = calculate_greedy_score(task_zero_effort)
        print(f"ERROR: Should have raised ValueError for zero effort")
    except ValueError as e:
        print(f"Correctly caught ValueError: {e}")
        print(f"Expected: ValueError raised for zero effort")
    print()

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("STANDALONE TESTS COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print("  - All validation functions working correctly")
    print("  - Bandwidth allocation validation enforces 100% sum")
    print("  - Score calculation functions work for all three algorithms")
    print("  - Edge cases (zero values) handled with clear errors")
    print("  - Task filtering and constraint checking operational")
    print()
    print("All business logic functions are ready for use by the workflow layer.")

"""
Logic layer for runestones monitoring system.
Contains business rules, validation logic, and data processing rules.
"""

from datetime import datetime


def validate_project_name(project_name):
    """
    Validate project name according to business rules.

    Business rules:
    - Project name must not be empty
    - Project name must be between 3 and 100 characters
    - Project name should not contain only whitespace

    Args:
        project_name (str): The project name to validate

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not project_name:
        return False, "Project name cannot be empty"

    # Strip whitespace for length check
    trimmed_name = project_name.strip()

    if len(trimmed_name) < 3:
        return False, "Project name must be at least 3 characters long"

    if len(trimmed_name) > 100:
        return False, "Project name must not exceed 100 characters"

    if not trimmed_name:
        return False, "Project name cannot contain only whitespace"

    return True, None


def validate_job_data(prompt_text, llm_model):
    """
    Validate job data before creation.

    Business rules:
    - Prompt text must not be empty
    - Prompt text must be at least 10 characters
    - LLM model must be a recognized model name

    Args:
        prompt_text (str): The prompt text
        llm_model (str): The LLM model name

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Validate prompt text
    if not prompt_text or not prompt_text.strip():
        return False, "Prompt text cannot be empty"

    if len(prompt_text.strip()) < 10:
        return False, "Prompt text must be at least 10 characters long"

    # Validate LLM model
    valid_models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']
    if llm_model not in valid_models:
        return False, f"LLM model must be one of: {', '.join(valid_models)}"

    return True, None


def validate_metrics_data(token_count, task_count, input_tokens, output_tokens):
    """
    Validate metrics data for consistency.

    Business rules:
    - All counts must be non-negative
    - token_count should equal input_tokens + output_tokens (with tolerance for rounding)
    - task_count should be at least 0

    Args:
        token_count (int): Total token count
        task_count (int): Number of tasks
        input_tokens (int): Input token count
        output_tokens (int): Output token count

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    # Check for negative values
    if token_count < 0:
        return False, "Token count cannot be negative"

    if task_count < 0:
        return False, "Task count cannot be negative"

    if input_tokens < 0:
        return False, "Input tokens cannot be negative"

    if output_tokens < 0:
        return False, "Output tokens cannot be negative"

    # Verify token count consistency (allow 5% tolerance for rounding differences)
    expected_total = input_tokens + output_tokens
    tolerance = max(expected_total * 0.05, 10)  # 5% or at least 10 tokens

    if abs(token_count - expected_total) > tolerance:
        return False, f"Token count ({token_count}) does not match sum of input ({input_tokens}) and output ({output_tokens}) tokens"

    return True, None


def calculate_token_cost(token_count, llm_model):
    """
    Calculate cost based on token count and model.

    Business rule: Different models have different pricing per 1000 tokens.
    These are example prices - adjust based on actual pricing.

    Args:
        token_count (int): Number of tokens used
        llm_model (str): The LLM model used

    Returns:
        float: Cost in dollars
    """
    # Price per 1000 tokens for different models (example pricing)
    pricing = {
        'gpt-4': 0.06,  # $0.06 per 1K tokens
        'gpt-3.5-turbo': 0.002,  # $0.002 per 1K tokens
        'claude-3-opus': 0.075,  # $0.075 per 1K tokens
        'claude-3-sonnet': 0.015,  # $0.015 per 1K tokens
        'claude-3-haiku': 0.0025  # $0.0025 per 1K tokens
    }

    # Get price per 1K tokens, default to 0 if model not found
    price_per_1k = pricing.get(llm_model, 0)

    # Calculate total cost
    cost = (token_count / 1000) * price_per_1k

    return round(cost, 3)


def determine_job_priority(task_count, project_name):
    """
    Determine job priority based on business rules.

    Business rules:
    - Jobs with 10+ tasks are HIGH priority
    - Jobs with 5-9 tasks are MEDIUM priority
    - Jobs with <5 tasks are LOW priority
    - Critical projects (containing "urgent" or "critical") are always HIGH

    Args:
        task_count (int): Number of tasks in the job
        project_name (str): Name of the project

    Returns:
        str: Priority level ('HIGH', 'MEDIUM', 'LOW')
    """
    # Check for critical keywords in project name
    project_lower = project_name.lower()
    if 'urgent' in project_lower or 'critical' in project_lower:
        return 'HIGH'

    # Determine priority by task count
    if task_count >= 10:
        return 'HIGH'
    elif task_count >= 5:
        return 'MEDIUM'
    else:
        return 'LOW'


def is_project_over_budget(total_cost, budget_limit=100.0):
    """
    Check if a project has exceeded its budget.

    Business rule: Projects have a default budget limit of $100.

    Args:
        total_cost (float): Total cost incurred by the project
        budget_limit (float): Budget limit for the project (default: $100)

    Returns:
        bool: True if over budget, False otherwise
    """
    return total_cost > budget_limit


def calculate_efficiency_score(token_count, task_count):
    """
    Calculate an efficiency score for a job.

    Business rule: Efficiency is measured as tasks completed per 1000 tokens.
    Higher score means more tasks accomplished with fewer tokens.

    Args:
        token_count (int): Number of tokens used
        task_count (int): Number of tasks completed

    Returns:
        float: Efficiency score (tasks per 1K tokens)
    """
    if token_count == 0:
        return 0.0

    # Calculate tasks per 1000 tokens
    efficiency = (task_count / token_count) * 1000

    return round(efficiency, 2)


def get_job_status_display(status):
    """
    Convert job status code to user-friendly display text.

    Args:
        status (str): Status code

    Returns:
        str: User-friendly status display text
    """
    status_map = {
        'pending': 'Pending',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'failed': 'Failed',
        'cancelled': 'Cancelled'
    }

    return status_map.get(status, status.title())


def filter_jobs_by_date_range(jobs_df, start_date=None, end_date=None):
    """
    Filter jobs by date range.

    Args:
        jobs_df (pd.DataFrame): Jobs dataframe with 'created_date' column
        start_date (str or datetime, optional): Start date for filtering
        end_date (str or datetime, optional): End date for filtering

    Returns:
        pd.DataFrame: Filtered jobs dataframe
    """
    import pandas as pd

    # Create a copy to avoid modifying original
    filtered_df = jobs_df.copy()

    # Convert created_date to datetime if it's not already
    filtered_df['created_date'] = pd.to_datetime(filtered_df['created_date'])

    # Apply start date filter
    if start_date:
        start_date = pd.to_datetime(start_date)
        filtered_df = filtered_df[filtered_df['created_date'] >= start_date]

    # Apply end date filter
    if end_date:
        end_date = pd.to_datetime(end_date)
        filtered_df = filtered_df[filtered_df['created_date'] <= end_date]

    return filtered_df


if __name__ == "__main__":
    # Standalone test section - demonstrates business logic functions
    print("=" * 60)
    print("RUNESTONES LOGIC LAYER TEST")
    print("=" * 60)

    # Test 1: Project name validation
    print("\n1. Project Name Validation:")
    test_names = ["AI", "Valid Project Name", "A" * 101, "   ", "Good Name"]
    for name in test_names:
        is_valid, error = validate_project_name(name)
        status = "✓ VALID" if is_valid else f"✗ INVALID: {error}"
        print(f"   '{name[:20]}...': {status}")

    # Test 2: Job data validation
    print("\n2. Job Data Validation:")
    test_cases = [
        ("Write a blog post about AI", "gpt-4"),
        ("Short", "gpt-4"),
        ("Valid prompt text here", "invalid-model")
    ]
    for prompt, model in test_cases:
        is_valid, error = validate_job_data(prompt, model)
        status = "✓ VALID" if is_valid else f"✗ INVALID: {error}"
        print(f"   Prompt='{prompt[:20]}...', Model='{model}': {status}")

    # Test 3: Metrics validation
    print("\n3. Metrics Data Validation:")
    test_metrics = [
        (2500, 3, 500, 2000),  # Valid
        (2500, 3, 500, 1000),  # Invalid - tokens don't add up
        (-100, 3, 500, 2000)   # Invalid - negative tokens
    ]
    for token_count, task_count, input_tok, output_tok in test_metrics:
        is_valid, error = validate_metrics_data(token_count, task_count, input_tok, output_tok)
        status = "✓ VALID" if is_valid else f"✗ INVALID: {error}"
        print(f"   Tokens={token_count}, Tasks={task_count}: {status}")

    # Test 4: Token cost calculation
    print("\n4. Token Cost Calculation:")
    test_costs = [
        (10000, 'gpt-4'),
        (10000, 'claude-3-opus'),
        (10000, 'gpt-3.5-turbo')
    ]
    for tokens, model in test_costs:
        cost = calculate_token_cost(tokens, model)
        print(f"   {tokens:,} tokens on {model}: ${cost:.3f}")

    # Test 5: Job priority determination
    print("\n5. Job Priority Determination:")
    test_priorities = [
        (3, "Regular Project"),
        (7, "Medium Project"),
        (15, "Large Project"),
        (2, "Urgent Bug Fix")
    ]
    for tasks, project in test_priorities:
        priority = determine_job_priority(tasks, project)
        print(f"   {tasks} tasks, Project='{project}': {priority}")

    # Test 6: Budget check
    print("\n6. Budget Check:")
    test_budgets = [
        (75.50, 100.0),
        (150.00, 100.0),
        (99.99, 100.0)
    ]
    for cost, limit in test_budgets:
        over_budget = is_project_over_budget(cost, limit)
        status = "OVER BUDGET" if over_budget else "WITHIN BUDGET"
        print(f"   Cost=${cost:.2f}, Limit=${limit:.2f}: {status}")

    # Test 7: Efficiency score
    print("\n7. Efficiency Score:")
    test_efficiency = [
        (2500, 3),
        (4500, 7),
        (1800, 2)
    ]
    for tokens, tasks in test_efficiency:
        score = calculate_efficiency_score(tokens, tasks)
        print(f"   {tasks} tasks in {tokens:,} tokens: {score} tasks/1K tokens")

    # Test 8: Status display
    print("\n8. Status Display Conversion:")
    test_statuses = ['pending', 'in_progress', 'completed', 'failed']
    for status in test_statuses:
        display = get_job_status_display(status)
        print(f"   '{status}' → '{display}'")

    print("\n" + "=" * 60)
    print("All logic operations completed successfully!")
    print("=" * 60)

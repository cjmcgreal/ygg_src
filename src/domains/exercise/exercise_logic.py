"""
Exercise business logic.
Contains custom business rules and validation.
"""


def validate_exercise_entry(name, value):
    """
    Validate an exercise entry.

    Business rules:
    - Name must not be empty
    - Value must be positive

    Args:
        name (str): Exercise name
        value (float): Exercise value (e.g., reps, duration)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or name.strip() == "":
        return False, "Exercise name cannot be empty"

    if value < 0:
        return False, "Exercise value must be positive"

    return True, ""


def calculate_exercise_score(value, difficulty=1.0):
    """
    Calculate exercise score based on value and difficulty.

    Business rule: Score = value * difficulty multiplier

    Args:
        value (float): Exercise value
        difficulty (float): Difficulty multiplier (default 1.0)

    Returns:
        float: Calculated score
    """
    return round(value * difficulty, 2)


if __name__ == "__main__":
    # Standalone test
    print("Exercise Logic - Standalone Test")
    print("=" * 50)

    # Test validation
    print("\n1. Testing validation:")
    valid, msg = validate_exercise_entry("Push-ups", 20)
    print(f"   Valid entry: {valid}, Message: {msg}")

    valid, msg = validate_exercise_entry("", 20)
    print(f"   Empty name: {valid}, Message: {msg}")

    valid, msg = validate_exercise_entry("Squats", -5)
    print(f"   Negative value: {valid}, Message: {msg}")

    # Test score calculation
    print("\n2. Testing score calculation:")
    score = calculate_exercise_score(20, 1.5)
    print(f"   Score for 20 reps at 1.5 difficulty: {score}")

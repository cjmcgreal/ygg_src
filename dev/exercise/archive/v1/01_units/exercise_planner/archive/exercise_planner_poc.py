# -*- coding: utf-8 -*-

def plan_next_workout(exercise_data, history):
    """
    Determines the next rep/weight scheme for an exercise based on past performance.

    Parameters:
        exercise_data (dict): Dictionary with rep range, increments, and deloads for the exercise.
            Example:
                {
                    "rep_range": (8, 12),
                    "rep_increment": 1,
                    "weight_increment": 5,
                    "deload_increment": 10
                }

        history (list): List of past results.
            Each result is a dict with:
                {
                    "reps": int,
                    "weight": int,
                    "success": bool
                }

    Returns:
        dict: The next planned workout: {"reps": int, "weight": int}
    """
    if not history:
        # Starting point
        return {"reps": exercise_data["rep_range"][0], "weight": 0}

    last = history[-1]
    fails = sum(not h["success"] and h["reps"] == last["reps"] and h["weight"] == last["weight"]
                for h in history[-3:])  # look at most recent 3 attempts

    reps = last["reps"]
    weight = last["weight"]

    if last["success"]:
        if reps < exercise_data["rep_range"][1]:
            reps += exercise_data["rep_increment"]
        else:
            reps = exercise_data["rep_range"][0]
            weight += exercise_data["weight_increment"]
    else:
        if fails >= 3:
            weight = max(0, weight - exercise_data["deload_increment"])
            reps = exercise_data["rep_range"][0]  # reset reps on deload

    return {"reps": reps, "weight": weight}


exercise = {
    "rep_range": (8, 12),
    "rep_increment": 1,
    "weight_increment": 5,
    "deload_increment": 10
}

history = [
    {"reps": 8, "weight": 0, "success": True},
    {"reps": 9, "weight": 0, "success": True},
    {"reps": 10, "weight": 0, "success": True},
    {"reps": 11, "weight": 0, "success": True},
    {"reps": 12, "weight": 0, "success": True},  # triggers weight bump
    {"reps": 8, "weight": 5, "success": False},
    {"reps": 8, "weight": 5, "success": False},
    {"reps": 8, "weight": 5, "success": False},  # triggers deload
]

next_plan = plan_next_workout(exercise, history)
print(next_plan)  # Output: {'reps': 8, 'weight': 0}

def test_plan_next_workout():
    exercise = {
        "rep_range": (8, 12),
        "rep_increment": 1,
        "weight_increment": 5,
        "deload_increment": 10
    }

    # Test 1: First workout (no history)
    assert plan_next_workout(exercise, []) == {"reps": 8, "weight": 0}

    # Test 2: Success within rep range (increment reps)
    history = [{"reps": 8, "weight": 0, "success": True}]
    assert plan_next_workout(exercise, history) == {"reps": 9, "weight": 0}

    # Test 3: Success at upper end of rep range (increment weight, reset reps)
    history = [{"reps": 12, "weight": 0, "success": True}]
    assert plan_next_workout(exercise, history) == {"reps": 8, "weight": 5}

    # Test 4: One failure, stay same reps/weight
    history = [{"reps": 8, "weight": 5, "success": False}]
    assert plan_next_workout(exercise, history) == {"reps": 8, "weight": 5}

    # Test 5: Two failures, still no change
    history = [
        {"reps": 8, "weight": 5, "success": False},
        {"reps": 8, "weight": 5, "success": False}
    ]
    assert plan_next_workout(exercise, history) == {"reps": 8, "weight": 5}

    # Test 6: Third failure triggers deload
    history = [
        {"reps": 8, "weight": 5, "success": False},
        {"reps": 8, "weight": 5, "success": False},
        {"reps": 8, "weight": 5, "success": False}
    ]
    assert plan_next_workout(exercise, history) == {"reps": 8, "weight": 0}

    # Test 7: Deload doesn’t go below 0
    history = [
        {"reps": 8, "weight": 0, "success": False},
        {"reps": 8, "weight": 0, "success": False},
        {"reps": 8, "weight": 0, "success": False}
    ]
    assert plan_next_workout(exercise, history) == {"reps": 8, "weight": 0}

    print("✅ All test cases passed!")

# Run tests
test_plan_next_workout()
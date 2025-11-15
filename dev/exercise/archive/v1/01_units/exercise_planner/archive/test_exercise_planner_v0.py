#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 11:28:46 2025

@author: conrad
"""
from exercise_planner import plan_next_workout

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

def test_progression_logic():
    # Range increment test
    ex = {
        "name": "squat",
        "weight": 100,
        "reps": 8,
        "rep_range": (8, 12),
        "rep_increment": 1,
        "weight_increment": 5,
        "deload_amount": 10,
        "failures": 0,
    }
    ex = plan_next_workout(ex, success=True)
    assert ex["reps"] == 9 and ex["weight"] == 100 and ex["failures"] == 0

    # Max range, triggers weight increment and rep reset
    ex["reps"] = 12
    ex = plan_next_workout(ex, success=True)
    assert ex["reps"] == 8 and ex["weight"] == 105 and ex["failures"] == 0

    # Failure 1 and 2 (no deload yet)
    ex = plan_next_workout(ex, success=False)
    assert ex["failures"] == 1 and ex["weight"] == 105
    ex = plan_next_workout(ex, success=False)
    assert ex["failures"] == 2 and ex["weight"] == 105

    # Failure 3 → triggers deload
    ex = plan_next_workout(ex, success=False)
    assert ex["failures"] == 0 and ex["weight"] == 95  # 105 - 10 = 95

    print("✅ All tests passed.")


# Run the test
test_progression_logic()
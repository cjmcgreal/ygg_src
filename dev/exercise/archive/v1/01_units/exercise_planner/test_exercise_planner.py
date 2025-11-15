#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  6 14:10:43 2025

@author: conrad
"""

from exercise_planner import ExercisePlanner

planner = ExercisePlanner()
plan_next_workout = planner.plan_next_workout

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


test_progression_logic()

exercise_planner = ExercisePlanner()
exercise_planner.dummy()

exercise = {
    "name": "squat",
    "weight": 100,
    "reps": 8,
    "rep_range": (8, 12),
    "rep_increment": 1,
    "weight_increment": 5,
    "deload_amount": 10,
    "failures": 0,
}

ex = planner.plan_next_workout(exercise,success=True)

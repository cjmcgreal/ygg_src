#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 15:11:52 2025

@author: conrad
"""

import pytest
from exercise_planner import ExercisePlanner

planner = ExercisePlanner()
plan_next_workout = planner.plan_next_workout

# simplest possible call
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

ex = planner.plan_next_workout(exercise)
ex_1 = planner.plan_next_workout(exercise,success=True)
ex_2 = planner.plan_next_workout(exercise,success=False)

# pytest
@pytest.fixture
def default_exercise():
    return {
        "name": "Bench Press",
        "weight": 100,
        "reps": 8,
        "rep_range": (8, 12),
        "rep_increment": 1,
        "weight_increment": 5,
        "deload_increment": 10,
        "failures": 0
    }

def test_rep_increment(default_exercise):
    ex = default_exercise.copy()
    result = plan_next_workout(ex, success=True)
    assert result["reps"] == 9
    assert result["weight"] == 100
    assert result["failures"] == 0

def test_weight_increment_after_max_reps(default_exercise):
    ex = default_exercise.copy()
    ex["reps"] = 12
    result = plan_next_workout(ex, success=True)
    assert result["reps"] == 8
    assert result["weight"] == 105
    assert result["failures"] == 0

def test_failure_once(default_exercise):
    ex = default_exercise.copy()
    result = plan_next_workout(ex, success=False)
    assert result["failures"] == 1
    assert result["weight"] == 100
    assert result["reps"] == 8

def test_failure_three_times_triggers_deload(default_exercise):
    ex = default_exercise.copy()
    ex["failures"] = 2
    result = plan_next_workout(ex, success=False)
    assert result["failures"] == 3
    assert result["weight"] == 90  # 100 - 10 deload
    assert result["reps"] == 8

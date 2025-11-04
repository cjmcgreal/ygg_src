#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 15:31:46 2025

@author: conrad
"""
import pandas as pd
from exercise import Exercise

def fetch_exercise_details(exercise_name, excel_file="exercise.xlsx"):
    df = pd.read_excel(excel_file, sheet_name='exercises')
    exercise_data = df[df['name'] == exercise_name].iloc[0].to_dict()
    
    exercise_details = {
        "name": exercise_data['name'],
        "weight": exercise_data['weight'],
        "reps": exercise_data['reps'],
        "rep_range": tuple(map(int, exercise_data['rep_range'].strip('()').split(','))),
        "rep_increment": exercise_data['rep_increment'],
        "weight_increment": exercise_data['weight_increment'],
        "deload_amount": exercise_data['deload_amount'],
        "failures": exercise_data['failures']
    }
    
    return exercise_details

Ex = Exercise()

exercise_name  = "Bench Press – Hypertrophy"
ex = fetch_exercise_details(exercise_name)
new_exercise = Ex.planner.plan_next_workout(ex)

#   def save_workout: 
#      once a workout is complete:

#      fetch the existing workout from the database

#      run the exercise planner to make updates

#      write to the exercise "log".

#      update the "live" exercise info.
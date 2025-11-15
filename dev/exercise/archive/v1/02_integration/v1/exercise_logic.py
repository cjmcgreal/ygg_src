import pandas as pd
import random

EXERCISES = [
    "Barbell Bench Press", "Assisted Pullups", "Overhead Press",
    "Barbell Row", "Deadlift", "Squat", "Dumbbell Curl", "Tricep Pushdown"
]

def generate_workout(num_exercises=3):
    """Randomly generate a workout of 3-5 sets per exercise."""
    selected_exercises = random.sample(EXERCISES, num_exercises)
    rows = []
    for exercise in selected_exercises:
        sets = random.randint(3, 5)
        for _ in range(sets):
            reps = random.choice([8, 10, 12])
            weight = random.choice([40, 50, 60])
            rows.append({
                "exercise": exercise,
                "reps": reps,
                "weight": weight
            })
    return pd.DataFrame(rows)

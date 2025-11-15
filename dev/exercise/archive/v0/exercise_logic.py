import pandas as pd

class ExerciseLogic:
    def generate_workout(self, exercises: list):
        workout_data = []   # container
        for exercise in exercises:        
            if exercise == "Barbell Bench Press":
                num_sets = 3
                reps = 10
                weight = 100
                
            elif exercise == "Assisted Pullups":
                num_sets = 3
                reps = 10
                weight = 135
                
            for set_num in range(1, num_sets + 1):
                workout_data.append({
                    "Exercise": exercise,
                    "Set": set_num,
                    "Reps": reps,
                    "Weight (lbs)": weight
                    })
        
        workout_df = pd.DataFrame(workout_data)
        return workout_df


if __name__ == "__main__":
    exercises = [
        "Barbell Bench Press",
        "Assisted Pullups"
        ]
    
    el = ExerciseLogic()
    df = el.generate_workout(exercises)
    print(df)


from exercise_analysis import ExerciseAnalysis
from exercise_db import ExerciseDB
from exercise_logic import ExerciseLogic


class ExerciseWorkflow:
    def __init__(self):
        self.db = ExerciseDB()
        self.logic = ExerciseLogic()
        self.analysis = ExerciseAnalysis()
        
# Class Methods
    # Saving a workout
    def save_workout():
        print('function save_workout executed')

#%% Example usage
if __name__ == "__main__":

    ewf = ExerciseWorkflow()

    #%% db
    exercise = "Bench Press – Hypertrophy"
    exercise_details = ewf.db.fetch_exercise_details(exercise)
    
    #%% logic
    exercises = [
        "Barbell Bench Press",
        "Assisted Pullups"
        ]
    
    df = ewf.logic.generate_workout(exercises)
    print(df)

    #%% analysis
    len_df = ewf.analysis.count_sets(df)
    print("number of sets: ", len_df)
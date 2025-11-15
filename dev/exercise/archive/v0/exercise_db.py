import pandas as pd

class ExerciseDB:
    def fetch_exercise_details(self, exercise_name, excel_file="exercise.xlsx"):
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
    
if __name__ == "__main__":
    print(__file__)
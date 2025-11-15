
class ExercisePlanner:
    def plan_next_workout(self,exercise: dict, success: bool = True) -> dict:
        """
        Update the exercise progression based on whether the previous workout was successful.
        
        - Increments reps until reaching the upper bound, then adds weight and resets reps.
        - If failure occurs, increases failure count. After 3 failures, deloads and resets failure count.
        """
        if success:
            exercise["failures"] = 0
            if exercise["reps"] < exercise["rep_range"][1]:
                exercise["reps"] += exercise["rep_increment"]
            else:
                exercise["weight"] += exercise["weight_increment"]
                exercise["reps"] = exercise["rep_range"][0]
        else:
            exercise["failures"] += 1
            if exercise["failures"] >= 3:
                exercise["weight"] -= exercise["deload_amount"]
                exercise["failures"] = 0
    
        return exercise
    
    def dummy(self):
        print('hello ExercisePlanner')        

if __name__ == "__main__": 
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
    
    ep = ExercisePlanner()
    ex = ep.plan_next_workout(exercise,True)
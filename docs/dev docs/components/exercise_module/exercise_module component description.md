# Current component capability - human-readable description
We have the ability to: 
- Plan the next workout.
	- Dependencies:
	- Limitations:
- Make a checklist, for an exercise.
	- Dependencies:
	- Limitations:

# Current file index & functionality description

## file 1
file path: yggdrasill/dev/exercise/upp-7 workout planning/exercise_planner
class: ExercisePlanner
method: plan_next_workout
created_by: runestone id
header:
	def plan_next_workout(self,exercise: dict, success: bool = True) -> dict:
		"""
		Update the exercise progression based on whether the previous workout was successful.
		
		- Increments reps until reaching the upper bound, then adds weight and resets reps.
		- If failure occurs, increases failure count. After 3 failures, deloads and resets failure count.
		"""

## file 2
file path: yggdrasill/dev/exercise/upp-7 workout planning/checklist_maker/app.py
created_by: runestone id

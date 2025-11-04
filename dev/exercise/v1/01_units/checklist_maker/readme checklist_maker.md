**Links**

[[User Pain Point 7 - Ease of logging workouts]]

**Description**
Streamlit app that allows you to:
- define steps
- renders those steps as checkboxes in streamlit
- mark steps as complete
- save completed steps, time stamped, using a button
	- into *completed_steps.csv*

**Header**
Inputs: *my_steps.csv*
Output: *completed_steps.csv*

**file description**
app.py 
completed_steps.csv
my_steps.csv

**Test Directions**
todo:
- create_conda_env.sh
- rebuild_conda_env.sh
- start_app.sh 
```bash
cd this_folder
conda activate ygg
streamlit run app.py
```

- create_conda_env_and_start_app.sh
- create_requirements_file.sh

**Observations & Feedback**
Good:
- Counts number of completed steps, of total, as they are completed.

Not good:
- Overwrites *completed_steps.csv* every time
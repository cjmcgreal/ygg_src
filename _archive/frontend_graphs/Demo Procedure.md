# Procedure
Current Process to generate a git flow chart from csv DB:
1. Manually populated example_db.ods
2. Using LibreOfficeCalc, save example_db.ods as example_db.csv
3. Using Spyder, run make_git_flow_chart-from_db.py
4. Open gitgraph.md

# Caveats, Bugs, and Feedback
1. It will only populate the commits, if the "message" column is filled out.
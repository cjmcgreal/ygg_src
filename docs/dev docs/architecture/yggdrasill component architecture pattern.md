---
parent: yggdrasill
type: documentation
---
# v0 Streamlit
Files:
- ```{domain}_analysis.py```
- ```{domain}_app.py```
- ```{domain}_db.py```
- ```{domain}_logic.py```
- ```{domain}_workflow.py```

```yaml
Preferred production rules:

{

"preferred_production_layout": {

"frontend": {

"description": "Streamlit-based user interface.",

"folder_rule": "All frontend files live under /frontend/.",

"examples": [

"frontend/app.py",

"frontend/components/sidebar.py",

"frontend/components/forms.py"

]

},

"database": {

"description": "Database and database interface layer (currently Excel/CSV, extensible to SQL).",

"folder_rule": "All database interface files live under /database/.",

"examples": [

"database/db_client.py",

"database/load_csv.py",

"database/load_excel.py"

]

},

"logic": {

"description": "Core solver or planner modules performing computation and business logic.",

"folder_rule": "All core logic files live under /logic/.",

"examples": [

"logic/planner.py",

"logic/solver.py",

"logic/validators.py"

]

},

"workflow": {

"description": "Domain-scoped scripts or routines triggered by user actions.",

"folder_rule": "All workflow routines live under /workflow/.",

"examples": [

"workflow/save_workout.py",

"workflow/generate_report.py",

"workflow/sync_data.py"

]

}

},

"cross_cutting_rules": {

"dependency_flow": [

"frontend may only call workflow entrypoints, not database or logic directly",

"workflow orchestrates calls into logic and database layers",

"logic may call database but must not reference frontend",

"database must not import or depend on logic, workflow, or frontend"

],

"consistency": [

"All inter-component communication must go through explicit interfaces (function signatures, data contracts)",

"Shared data structures must be defined in a single canonical place (YAML or schema file) and imported, not duplicated"

],

"enforcement": [

"No cross-folder imports violating the dependency flow",

"Each new feature must clearly identify which layer(s) it touches and maintain separation"

]

}

}

```
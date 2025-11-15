# Specification: Task Selection Algorithm Prototype

## Goal

Build a Streamlit-based prototype for selecting optimal tasks from a backlog using configurable algorithms (greedy, weighted, knapsack) that respect time constraints and domain preferences, with full CRUD task management and solver run tracking.

## User Stories

- As a user, I want to manage a backlog of tasks with effort, value, priority, and domain categorization so that I can organize my potential work items
- As a user, I want to define my available time and domain preferences so that the algorithm understands my capacity and interests
- As a user, I want to choose between different optimization algorithms (greedy, weighted, knapsack) so that I can experiment with different selection strategies
- As a user, I want to see which tasks are selected and why so that I can understand the algorithm's decision-making process
- As a user, I want to compare historical solver runs so that I can evaluate which algorithm works best for my needs
- As a user, I want to group related tasks under a project label so that I can organize work by initiative

## Core Requirements

### Functional Requirements

**Task Management:**
- Create, read, update, and delete tasks
- Each task has: title, description, domain, project parent (text field), effort (story points), value (numeric score), priority (ranking, 1=highest)
- Tasks are independent with no dependencies
- Display tasks in a table/grid with sorting and filtering capabilities

**Domain Management:**
- Define domains with name and UI color for visual distinction
- Domains categorize tasks and enable preference-based allocation
- Domains are referenced by tasks and used in solver preferences

**Bandwidth Allocation:**
- User inputs total available time in story points
- User sets domain preferences as percentage split (must sum to 100%)
- Column layout displays metadata calculator showing equivalent hours for each domain
- Story points to hours conversion configurable (default: 1 point = 2 hours)

**Solver Execution:**
- User selects algorithm: greedy, weighted, or knapsack
- Algorithm respects total time constraint (available story points)
- Algorithm respects domain preference percentages
- Algorithm produces ranked list of selected tasks with rationale

**Solver Output:**
- Display selected tasks with summary statistics (total effort, total value, domains covered)
- Show algorithm's step-by-step decision process
- Explain why specific tasks were selected or rejected
- Display constraint satisfaction details (time used vs. available, domain allocation vs. preferences)
- Show performance metrics (execution time, optimization score)

**Historical Tracking:**
- Save each solver run with timestamp, parameters (available time, algorithm, domain preferences), and results
- Display list of historical runs with key metrics
- Allow viewing details of past runs for comparison

### Non-Functional Requirements

**Performance:**
- Solver algorithms should complete in under 5 seconds for up to 100 tasks
- CSV file operations should be performant (no noticeable lag for typical datasets)
- UI should be responsive with immediate feedback for user actions

**Usability:**
- Clear tab-based navigation (4 tabs total)
- Visual feedback for validation errors
- Color-coded domains for easy visual scanning
- Inline help text or tooltips for key concepts (story points, algorithms)

**Data Integrity:**
- Validate all numeric inputs (positive values required)
- Validate domain preferences sum to 100%
- Ensure referential integrity (tasks reference valid domains)
- Handle missing or corrupted CSV files gracefully with clear error messages

**Maintainability:**
- Follow user's Python prototype development standards
- Clear separation of concerns (app, workflow, logic, analysis, db layers)
- Comprehensive comments explaining business rules and algorithms
- Standalone test sections in all Python files

## Visual Design

No mockups provided. UI specifications:

**Layout:**
- Single-page Streamlit app with 4 horizontal tabs at top
- Tab 1: Task Management - table view with add/edit/delete controls
- Tab 2: Bandwidth Allocation - two-column layout (left: inputs, right: metadata calculator)
- Tab 3: Solver Run - algorithm selector, run button, results display
- Tab 4: Solver Output Details - detailed decision breakdown and metrics

**Color Scheme:**
- Use domain colors for visual coding in tables and charts
- Default palette suggestion: blue, green, orange, purple, red (user configurable in domains.csv)
- Success/error states use Streamlit defaults (green/red)

**Tables:**
- Sortable columns for task list
- Inline edit/delete buttons per row
- Color-coded domain column using domain colors
- Responsive to screen size (use Streamlit's native responsive features)

## Reusable Components

### Existing Code to Leverage

No existing code identified - this is a greenfield prototype project.

### New Components Required

**task_selection_app.py:**
- `render_task_selection()` function as main entry point
- Tab 1: Task CRUD interface with forms and data table
- Tab 2: Bandwidth allocation interface with percentage sliders and metadata display
- Tab 3: Solver run interface with algorithm picker and results display
- Tab 4: Detailed output interface with explanations and metrics

**task_selection_workflow.py:**
- `create_task(title, description, domain, project_parent, effort, value, priority)` - orchestrates task creation
- `update_task(task_id, **kwargs)` - orchestrates task updates
- `delete_task(task_id)` - orchestrates task deletion
- `get_all_tasks()` - retrieves all tasks for display
- `run_solver(available_time, domain_preferences, algorithm)` - orchestrates solver execution
- `get_solver_run_history()` - retrieves historical runs
- `get_solver_run_details(run_id)` - retrieves specific run details

**task_selection_logic.py:**
- `validate_task_data(title, effort, value, priority)` - business rule validation
- `validate_bandwidth_allocation(domain_preferences)` - ensures percentages sum to 100%
- `calculate_task_score(task, algorithm, domain_preference)` - scoring logic per algorithm
- `filter_tasks_by_constraints(tasks, constraints)` - constraint checking

**task_selection_analysis.py:**
- `greedy_solver(tasks, available_time, domain_preferences)` - greedy algorithm implementation
- `weighted_solver(tasks, available_time, domain_preferences)` - weighted scoring algorithm
- `knapsack_solver(tasks, available_time, domain_preferences)` - 0/1 knapsack algorithm
- `calculate_solution_metrics(selected_tasks, available_time)` - performance metrics
- `generate_decision_explanation(tasks, selected_tasks, algorithm, constraints)` - creates human-readable explanation

**task_selection_db.py:**
- `load_tasks()` - reads tasks.csv into DataFrame
- `save_tasks(tasks_df)` - writes DataFrame to tasks.csv
- `load_domains()` - reads domains.csv
- `save_domains(domains_df)` - writes domains.csv
- `load_solver_runs()` - reads solver_runs.csv
- `save_solver_run(run_data)` - appends new run to solver_runs.csv
- `get_solver_run_by_id(run_id)` - retrieves specific run

**task_selection_data/:**
- tasks.csv
- domains.csv
- solver_runs.csv

## Technical Approach

### Architecture

Follow user's Python prototype development standards with domain-based structure:

```
project_root/
├── app.py                           # Main entry point, imports render_task_selection()
├── src/
│   └── task_selection/
│       ├── task_selection_app.py       # Streamlit UI, 4 tabs
│       ├── task_selection_workflow.py  # Orchestration layer
│       ├── task_selection_logic.py     # Business rules, validation
│       ├── task_selection_analysis.py  # Solver algorithms
│       ├── task_selection_db.py        # CSV I/O operations
│       └── task_selection_data/
│           ├── tasks.csv
│           ├── domains.csv
│           └── solver_runs.csv
├── tests/
│   └── task_selection/
│       ├── test_task_selection_app.py
│       ├── test_task_selection_workflow.py
│       ├── test_task_selection_logic.py
│       ├── test_task_selection_analysis.py
│       └── test_task_selection_db.py
└── requirements.txt
```

### Data Model

**tasks.csv Schema:**
```
id,title,description,domain,project_parent,effort,value,priority
1,"Implement login","Add user authentication",backend,auth_project,5,8,1
2,"Design homepage","Create new landing page",frontend,,8,10,1
3,"Fix bug #123","Resolve null pointer error",backend,bugfix_sprint,2,6,2
```

Fields:
- id: Integer, auto-increment, unique identifier
- title: String, required, task name
- description: String, optional, detailed description
- domain: String, required, references domain name in domains.csv
- project_parent: String, optional, free text for grouping
- effort: Float, required, story points (positive)
- value: Float, required, numeric score (positive)
- priority: Integer, required, ranking within domain (1=highest, positive)

**domains.csv Schema:**
```
id,name,color
1,backend,#3498db
2,frontend,#2ecc71
3,design,#e74c3c
4,devops,#9b59b6
```

Fields:
- id: Integer, auto-increment, unique identifier
- name: String, required, unique, domain name
- color: String, required, hex color code for UI

**solver_runs.csv Schema:**
```
id,timestamp,available_time,algorithm,domain_preferences_json,selected_tasks_json,metrics_json,explanation_json
1,2025-11-11T10:30:00,40,greedy,"{""backend"":40,""frontend"":60}","[1,2,3]","{""total_effort"":15,""total_value"":24}","[""Explanation text""]"
```

Fields:
- id: Integer, auto-increment, unique identifier
- timestamp: ISO 8601 datetime string
- available_time: Float, story points allocated
- algorithm: String, one of: "greedy", "weighted", "knapsack"
- domain_preferences_json: JSON string, domain name to percentage mapping
- selected_tasks_json: JSON string, array of selected task IDs
- metrics_json: JSON string, performance metrics dictionary
- explanation_json: JSON string, array of explanation strings

### Algorithm Specifications

**Greedy Solver:**
- Sort all tasks by value-to-effort ratio (value/effort) descending
- Iterate through sorted tasks:
  - Check if task fits in remaining time
  - Check if task's domain allocation is not exceeded (based on domain_preferences)
  - If both true, select task
- Continue until no more tasks can be selected
- Return selected tasks with explanation of selection order

**Weighted Solver:**
- For each task, calculate weighted score: (domain_preference_pct / 100) * value * (1/priority) / effort
  - Higher domain preference increases score
  - Higher value increases score
  - Lower priority rank (higher priority) increases score
  - Lower effort increases score
- Sort tasks by weighted score descending
- Iterate through sorted tasks:
  - Check if task fits in remaining time
  - Check if task's domain allocation is not exceeded
  - If both true, select task
- Continue until no more tasks can be selected
- Return selected tasks with explanation including score calculations

**Knapsack Solver:**
- Implement 0/1 knapsack dynamic programming algorithm
- Capacity = available_time (in story points)
- Item weight = task effort
- Item value = task value * (domain_preference_pct / 100) * (1/priority)
  - Adjust value based on domain preference
  - Adjust value based on priority (higher priority = higher value multiplier)
- Apply domain constraints as secondary check:
  - After finding optimal selection, verify domain allocations
  - If domain limits exceeded, remove lowest-value tasks from over-allocated domains
- Return selected tasks with explanation of optimization score

**Common Constraint Checking:**
- Total effort of selected tasks <= available_time
- For each domain: sum(effort of selected tasks in domain) <= (domain_preference_pct / 100) * available_time
- Tasks are selected at most once (no duplicates)

**Decision Explanation Generation:**
- For each selected task: "Selected [task_title] (Domain: [domain], Effort: [effort]sp, Value: [value], Score: [calculated_score]) - Reason: [why it scored high]"
- For each rejected task: "Rejected [task_title] - Reason: [constraint violation or lower score]"
- Summary: "Total effort: [X]sp of [Y]sp available ([Z]% utilization). Total value: [V]. Domain breakdown: [by domain]"
- Algorithm-specific metrics: execution time, number of comparisons, optimization iterations

### UI/UX Specifications

**Tab 1: Task Management**
- Top section: "Add New Task" form
  - Fields: title (text), description (textarea), domain (dropdown), project_parent (text), effort (number), value (number), priority (number)
  - Submit button: "Add Task"
  - Clear button: "Reset Form"
- Middle section: "Existing Tasks" table
  - Columns: ID, Title, Description (truncated), Domain (color-coded), Project, Effort, Value, Priority, Actions
  - Actions: Edit icon, Delete icon
  - Sortable by clicking column headers
  - Filter by domain (multiselect above table)
- Edit mode: Modal or expander with pre-filled form, "Update" and "Cancel" buttons

**Tab 2: Bandwidth Allocation**
- Two-column layout using Streamlit columns
- Left column: "Input Your Allocation"
  - Number input: "Available Time (story points)" with help text explaining story points
  - For each domain from domains.csv:
    - Slider: "[Domain Name] Preference (%)" range 0-100
  - Real-time validation: Display error if sum != 100%
  - Info message: "Total allocation: [X]% (must equal 100%)"
- Right column: "Metadata Calculator"
  - Display header: "Time Breakdown"
  - Configurable conversion rate selector: "Story points to hours ratio" (default 1sp = 2hrs)
  - For each domain:
    - Show: "[Domain Name]: [percentage]% = [story_points]sp = [hours]hrs"
  - Show total: "Total: [total_sp]sp = [total_hrs]hrs"
  - Use domain colors for visual coding

**Tab 3: Solver Run**
- Top section: "Algorithm Selection"
  - Radio buttons: "Greedy", "Weighted", "Knapsack"
  - Info expander for each algorithm explaining how it works
- Middle section: "Run Parameters" (read-only summary)
  - Display: Available time, domain preferences, selected algorithm
  - Link/button: "Modify Parameters" (switches to Tab 2)
- Action: Large button "Run Solver"
- Bottom section: "Results Summary" (appears after run)
  - Metric tiles: Total Effort Used, Total Value, Number of Tasks Selected
  - Selected tasks table: ID, Title, Domain (color-coded), Effort, Value
  - Domain breakdown bar chart: effort allocated per domain vs. preference
  - Button: "View Detailed Explanation" (switches to Tab 4)
  - Button: "Save This Run" (persists to solver_runs.csv)

**Tab 4: Solver Output Details**
- Only accessible after a solver run (show message otherwise)
- Section 1: "Run Overview"
  - Display timestamp, algorithm used, available time, domain preferences
  - If viewing historical run, show run ID and date
- Section 2: "Algorithm Decision Process"
  - Step-by-step explanation as numbered list or timeline
  - For each task considered: show score calculation and selection decision
- Section 3: "Task Selection Rationale"
  - Expandable section per selected task with detailed justification
  - Expandable section for notable rejected tasks with rejection reason
- Section 4: "Constraint Satisfaction"
  - Table showing domain allocation vs. preference with % utilization
  - Progress bars or gauges for visual representation
  - Time constraint satisfaction: used vs. available
- Section 5: "Performance Metrics"
  - Execution time
  - Optimization score (algorithm-specific)
  - Number of tasks evaluated
  - Efficiency metrics (value per story point, etc.)
- Section 6: "Historical Comparison" (if applicable)
  - Dropdown: "Compare with previous run"
  - Side-by-side comparison table of key metrics

### Testing Strategy

**Unit Tests (pytest):**
- test_task_selection_logic.py:
  - Test validation functions with valid/invalid inputs
  - Test score calculation for each algorithm
  - Test constraint checking logic
- test_task_selection_analysis.py:
  - Test each solver with known inputs and expected outputs
  - Test edge cases: empty task list, zero time, impossible constraints
  - Test metrics calculation accuracy
  - Test explanation generation
- test_task_selection_db.py:
  - Test CSV read/write operations
  - Test handling of missing files (should create with defaults)
  - Test data integrity after save/load cycle
- test_task_selection_workflow.py:
  - Test orchestration functions with mocked dependencies
  - Test error propagation from lower layers
- test_task_selection_app.py:
  - Test that render_task_selection() can be called independently
  - Test form validation before submission

**Standalone Test Sections:**
- Every Python file must include `if __name__ == "__main__":` section
- Demonstrates typical usage of functions in that file
- Provides manual testing capability without pytest
- Example outputs with expected vs. actual comparisons

**Test Data:**
- Create sample_tasks.csv with 10-15 diverse tasks for testing
- Cover edge cases: very high effort, very low effort, equal scores, same priorities
- Include multiple domains with varying preferences

## Out of Scope

- Task scheduling or calendar integration
- Recurring tasks or task templates
- Team collaboration or multi-user features
- Advanced analytics or reporting dashboards beyond solver output
- Time tracking or actual vs. estimated comparisons
- Task dependencies or prerequisite relationships (tasks are independent)
- Complex project hierarchies (only simple text field grouping)
- User authentication or access control
- Real-time collaboration or live updates
- Integration with external project management tools (Jira, Trello, Asana)
- Mobile-responsive design optimization (basic Streamlit responsive is sufficient)
- Task import/export beyond CSV files
- Gantt charts or timeline visualizations
- Notifications or reminders
- Task archival or soft delete
- Version control for task changes
- Commenting or discussion on tasks

## Success Criteria

**Functional Completeness:**
- User can create, read, update, delete tasks with all required fields
- User can define domains with colors
- User can set bandwidth allocation and domain preferences that sum to 100%
- User can execute all three algorithms (greedy, weighted, knapsack) successfully
- Solver produces valid results respecting time and domain constraints
- Detailed explanation clearly communicates algorithm decisions
- Historical runs are saved and can be retrieved for comparison

**Performance:**
- Solver completes in under 5 seconds for 50 tasks
- No noticeable UI lag during normal operations
- CSV operations complete without errors

**Usability:**
- User can navigate between tabs without confusion
- Validation errors provide clear, actionable feedback
- Domain colors make visual scanning easy
- Metadata calculator accurately converts story points to hours
- Algorithm explanations help user understand how selection works

**Code Quality:**
- All code follows user's Python prototype development standards
- Clear separation of concerns across 5 file types per domain
- Comprehensive docstrings and inline comments
- All files include standalone test sections
- Pytest tests cover core functionality with >80% coverage

**Data Integrity:**
- No data loss during CRUD operations
- CSV files remain valid after all operations
- Referential integrity maintained (tasks reference valid domains)
- Constraint violations prevented by validation

**User Satisfaction:**
- User can compare algorithm effectiveness by running multiple times
- User gains insight into why specific tasks were recommended
- User can experiment with different domain preferences and see impact
- User can organize tasks by project for better mental model

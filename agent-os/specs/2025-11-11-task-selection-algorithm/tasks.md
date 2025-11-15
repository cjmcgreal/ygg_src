# Task Breakdown: Task Selection Algorithm Prototype

## Overview
Total Task Groups: 7
Development Approach: Python prototype with Streamlit
Domain: task_selection
Architecture: 5-file domain pattern (app, workflow, logic, analysis, db)

## Task List

### Phase 1: Foundation Setup

#### Task Group 1: Project Structure and CSV Data Files
**Dependencies:** None
**Estimated Effort:** 1-2 hours

- [x] 1.0 Set up project foundation
  - [x] 1.1 Create project root directory structure
    - Create `app.py` at root
    - Create `src/task_selection/` directory
    - Create `src/task_selection/task_selection_data/` directory
    - Create `tests/task_selection/` directory
    - Create `requirements.txt` with dependencies: streamlit, pandas, pytest
  - [x] 1.2 Create initial CSV data files with sample data
    - Create `src/task_selection/task_selection_data/domains.csv`
      - Schema: id,name,color
      - Add 4-5 sample domains (backend, frontend, design, devops, etc.)
      - Use hex color codes (#3498db, #2ecc71, #e74c3c, #9b59b6, #f39c12)
    - Create `src/task_selection/task_selection_data/tasks.csv`
      - Schema: id,title,description,domain,project_parent,effort,value,priority
      - Add 10-15 diverse sample tasks covering multiple domains
      - Include edge cases: high effort, low effort, equal scores, different priorities
    - Create `src/task_selection/task_selection_data/solver_runs.csv`
      - Schema: id,timestamp,available_time,algorithm,domain_preferences_json,selected_tasks_json,metrics_json,explanation_json
      - Start with empty file (header row only)
  - [x] 1.3 Create root app.py entry point
    - Import streamlit
    - Set page config (title, layout)
    - Add placeholder for importing render_task_selection()
    - Add comment explaining this will call the main domain render function

**Acceptance Criteria:**
- Directory structure matches user's Python prototype standards
- All three CSV files exist with proper headers
- Sample data includes diverse task scenarios for testing
- requirements.txt has all necessary dependencies
- Root app.py is ready to import domain render function

---

### Phase 2: Database Layer

#### Task Group 2: CSV Database Operations
**Dependencies:** Task Group 1 (COMPLETED)
**Estimated Effort:** 2-3 hours

- [x] 2.0 Implement CSV database layer (task_selection_db.py)
  - [x] 2.1 Write 2-8 focused tests in standalone section
    - Test load_domains() with valid CSV
    - Test save_domains() and verify data integrity
    - Test load_tasks() with valid CSV
    - Test save_tasks() preserves all fields
    - Test handling of missing files (should create with headers)
    - Test load_solver_runs() with empty and populated files
    - Limit to 2-8 highly focused tests maximum
  - [x] 2.2 Implement domain CSV operations
    - Function: `load_domains()` - reads domains.csv into DataFrame
    - Function: `save_domains(domains_df)` - writes DataFrame to domains.csv
    - Function: `get_domain_by_name(domain_name)` - retrieves specific domain
    - Handle missing file gracefully (create with sample data)
    - Include docstrings explaining parameters and return values
  - [x] 2.3 Implement task CSV operations
    - Function: `load_tasks()` - reads tasks.csv into DataFrame
    - Function: `save_tasks(tasks_df)` - writes DataFrame to tasks.csv
    - Function: `get_next_task_id()` - returns next available ID for new task
    - Function: `get_task_by_id(task_id)` - retrieves specific task
    - Function: `delete_task_by_id(task_id)` - removes task from DataFrame
    - Handle missing file gracefully (create with sample data)
    - Include docstrings explaining parameters and return values
  - [x] 2.4 Implement solver run CSV operations
    - Function: `load_solver_runs()` - reads solver_runs.csv into DataFrame
    - Function: `save_solver_run(run_data)` - appends new run to solver_runs.csv
    - Function: `get_solver_run_by_id(run_id)` - retrieves specific run
    - Function: `get_all_solver_runs()` - returns all runs sorted by timestamp
    - Handle JSON serialization for complex fields (preferences, results)
    - Include docstrings explaining parameters and return values
  - [x] 2.5 Add standalone test section (if __name__ == "__main__")
    - Demonstrate loading and saving each CSV type
    - Show sample CRUD operations on tasks
    - Print before/after data for manual inspection
    - Include expected vs actual output comments
  - [x] 2.6 Run database layer tests
    - Execute standalone test section manually
    - Run pytest tests for task_selection_db.py
    - Verify CSV files are created and data persists correctly

**Acceptance Criteria:**
- All CSV operations work correctly (load, save, get, delete)
- Missing files are handled gracefully with default data
- Data integrity maintained after save/load cycle
- Standalone test section demonstrates all key functions
- 2-8 focused tests pass successfully
- Comprehensive docstrings on all functions

---

### Phase 3: Business Logic Layer

#### Task Group 3: Validation and Business Rules
**Dependencies:** Task Group 2
**Estimated Effort:** 2-3 hours

- [x] 3.0 Implement business logic layer (task_selection_logic.py)
  - [x] 3.1 Write 2-8 focused tests in standalone section
    - Test validate_task_data() with valid and invalid inputs
    - Test validate_bandwidth_allocation() with various percentage sums
    - Test calculate_task_score() for each algorithm type
    - Test filter_tasks_by_domain() returns correct subset
    - Limit to 2-8 highly focused tests maximum
  - [x] 3.2 Implement task validation functions
    - Function: `validate_task_data(title, effort, value, priority)`
      - Returns (is_valid, error_message) tuple
      - Check title is not empty
      - Check effort is positive number
      - Check value is positive number
      - Check priority is positive integer
      - Include clear error messages for each validation
    - Function: `validate_domain_exists(domain_name, domains_df)`
      - Check if domain exists in domains DataFrame
      - Return boolean and error message if invalid
  - [x] 3.3 Implement bandwidth allocation validation
    - Function: `validate_bandwidth_allocation(domain_preferences)`
      - Input: dictionary of {domain_name: percentage}
      - Check sum equals 100% (allow small floating point tolerance)
      - Check all percentages are non-negative
      - Return (is_valid, error_message, total_percentage) tuple
    - Function: `calculate_time_breakdown(available_time, domain_preferences, points_to_hours=2.0)`
      - Input: total story points, domain preference dict, conversion ratio
      - Return: dictionary with {domain: {percentage, story_points, hours}}
      - Use for metadata calculator display
  - [x] 3.4 Implement scoring functions for algorithms
    - Function: `calculate_greedy_score(task_row)`
      - Returns: value-to-effort ratio (value/effort)
      - Handle zero effort edge case
    - Function: `calculate_weighted_score(task_row, domain_preference_pct)`
      - Returns: (domain_preference_pct / 100) * value * (1/priority) / effort
      - Incorporate domain preference, value, priority, and effort
      - Handle zero effort and zero priority edge cases
    - Function: `calculate_knapsack_value(task_row, domain_preference_pct)`
      - Returns: value * (domain_preference_pct / 100) * (1/priority)
      - Used as item value in knapsack algorithm
      - Handle zero priority edge case
  - [x] 3.5 Implement task filtering helpers
    - Function: `filter_tasks_by_domain(tasks_df, domain_name)`
      - Returns DataFrame filtered by domain
    - Function: `check_domain_constraint(selected_tasks_df, domain_name, allocated_time, available_time)`
      - Check if domain allocation doesn't exceed limit
      - Return boolean and constraint details
  - [x] 3.6 Add standalone test section (if __name__ == "__main__")
    - Demonstrate validation with valid and invalid examples
    - Show score calculations for sample tasks
    - Display time breakdown calculations
    - Include expected vs actual output comments
  - [x] 3.7 Run logic layer tests
    - Execute standalone test section manually
    - Run pytest tests for task_selection_logic.py
    - Verify all validation and scoring functions work correctly

**Acceptance Criteria:**
- Validation functions catch all invalid inputs with clear messages
- Bandwidth allocation validation enforces 100% sum requirement
- Score calculation functions work for all three algorithm types
- Edge cases handled (zero effort, zero priority, missing data)
- Standalone test section demonstrates all key functions
- 2-8 focused tests pass successfully
- Comprehensive docstrings explaining business rules

---

### Phase 4: Analysis and Solver Algorithms

#### Task Group 4: Solver Algorithm Implementation
**Dependencies:** Task Group 3
**Estimated Effort:** 4-5 hours

- [x] 4.0 Implement solver algorithms (task_selection_analysis.py)
  - [x] 4.1 Write 2-8 focused tests in standalone section
    - Test greedy_solver() with known task set and expected output
    - Test weighted_solver() with domain preferences
    - Test knapsack_solver() with capacity constraint
    - Test edge cases: empty task list, zero time, single task
    - Test calculate_solution_metrics() accuracy
    - Limit to 2-8 highly focused tests maximum
  - [x] 4.2 Implement greedy solver algorithm
    - Function: `greedy_solver(tasks_df, available_time, domain_preferences)`
      - Sort tasks by value-to-effort ratio descending
      - Iterate through sorted tasks
      - For each task:
        - Check if task effort fits in remaining time
        - Check if domain allocation not exceeded
        - If both true, add to selected list
        - Update remaining time and domain allocations
      - Return: (selected_tasks_df, explanation_list, metrics_dict)
      - Explanation includes: selection order, scores, reasons
    - Include detailed comments explaining algorithm steps
    - Handle edge case: no tasks fit constraints
  - [x] 4.3 Implement weighted solver algorithm
    - Function: `weighted_solver(tasks_df, available_time, domain_preferences)`
      - Calculate weighted score for each task using calculate_weighted_score()
      - Sort tasks by weighted score descending
      - Iterate through sorted tasks (same selection logic as greedy)
      - For each task:
        - Check if task effort fits in remaining time
        - Check if domain allocation not exceeded
        - If both true, add to selected list
        - Update remaining time and domain allocations
      - Return: (selected_tasks_df, explanation_list, metrics_dict)
      - Explanation includes: weighted scores, domain preferences impact
    - Include detailed comments explaining scoring formula
    - Handle edge case: all tasks score zero
  - [x] 4.4 Implement knapsack solver algorithm
    - Function: `knapsack_solver(tasks_df, available_time, domain_preferences)`
      - Implement 0/1 knapsack dynamic programming algorithm
      - Capacity = available_time (story points)
      - Item weight = task effort
      - Item value = calculate_knapsack_value() adjusted for preferences
      - Build DP table to find optimal selection
      - Backtrack to identify selected tasks
      - Apply domain constraint check as secondary validation:
        - If domain limits exceeded, remove lowest-value tasks from over-allocated domains
      - Return: (selected_tasks_df, explanation_list, metrics_dict)
      - Explanation includes: optimization score, DP iterations
    - Include detailed comments explaining DP algorithm
    - Handle edge case: capacity too small for any task
  - [x] 4.5 Implement solution metrics calculation
    - Function: `calculate_solution_metrics(selected_tasks_df, available_time, execution_time)`
      - Calculate total effort used
      - Calculate total value achieved
      - Calculate number of tasks selected
      - Calculate effort utilization percentage
      - Calculate value per story point (efficiency)
      - Calculate domain breakdown (effort per domain)
      - Return: dictionary with all metrics
    - Include docstring explaining each metric
  - [x] 4.6 Implement decision explanation generation
    - Function: `generate_decision_explanation(all_tasks_df, selected_tasks_df, algorithm, constraints, scores_df)`
      - For each selected task: "Selected [title] (Domain: [domain], Effort: [X]sp, Value: [Y], Score: [Z]) - Reason: [high score/good fit]"
      - For notable rejected tasks (top 5 by score): "Rejected [title] - Reason: [constraint violation or lower score]"
      - Summary: "Total effort: [X]sp of [Y]sp available ([Z]% utilization). Total value: [V]."
      - Domain breakdown: "Backend: [X]sp ([Y]% of [Z]sp allocated)"
      - Return: list of explanation strings
    - Generate human-readable, clear explanations
  - [x] 4.7 Add standalone test section (if __name__ == "__main__")
    - Create sample task set (10 tasks)
    - Run all three algorithms with same inputs
    - Display selected tasks for each algorithm
    - Show metrics and explanations
    - Compare results side by side
    - Include expected behavior comments
  - [x] 4.8 Run analysis layer tests
    - Execute standalone test section manually
    - Run pytest tests for task_selection_analysis.py
    - Verify all three algorithms produce valid results
    - Confirm algorithms respect time and domain constraints
    - Check explanations are clear and accurate

**Acceptance Criteria:**
- Greedy solver maximizes value-to-effort ratio within constraints
- Weighted solver incorporates domain preferences and priority
- Knapsack solver finds optimal solution using DP approach
- All solvers respect time and domain constraints
- Solution metrics are accurate and comprehensive
- Decision explanations clearly communicate algorithm reasoning
- Edge cases handled gracefully (empty list, zero time, etc.)
- Standalone test section demonstrates all three algorithms
- 2-8 focused tests pass successfully
- Algorithms complete in under 5 seconds for 50+ tasks

---

### Phase 5: Workflow Orchestration

#### Task Group 5: Workflow Layer
**Dependencies:** Task Groups 2, 3, 4 (ALL COMPLETED)
**Estimated Effort:** 2-3 hours

- [x] 5.0 Implement workflow orchestration (task_selection_workflow.py)
  - [x] 5.1 Write 2-8 focused tests in standalone section
    - Test create_task() orchestration with valid data
    - Test update_task() modifies correct task
    - Test delete_task() removes task correctly
    - Test run_solver() orchestrates algorithm execution
    - Test error propagation from lower layers
    - Limit to 2-8 highly focused tests maximum
  - [x] 5.2 Implement task CRUD orchestration
    - Function: `create_task(title, description, domain, project_parent, effort, value, priority)`
      - Call validation from logic layer
      - If valid, load tasks from db layer
      - Generate new task ID
      - Append new task to DataFrame
      - Save tasks via db layer
      - Return: (success, message, task_id)
    - Function: `update_task(task_id, **kwargs)`
      - Load tasks from db layer
      - Find task by ID
      - Update specified fields
      - Validate updated data
      - Save tasks via db layer
      - Return: (success, message)
    - Function: `delete_task(task_id)`
      - Load tasks from db layer
      - Remove task by ID using db function
      - Save updated tasks
      - Return: (success, message)
    - Function: `get_all_tasks()`
      - Call db layer to load tasks
      - Return: tasks DataFrame
  - [x] 5.3 Implement domain orchestration
    - Function: `get_all_domains()`
      - Call db layer to load domains
      - Return: domains DataFrame
    - Function: `get_domain_names()`
      - Load domains
      - Return: list of domain names for dropdowns
  - [x] 5.4 Implement solver run orchestration
    - Function: `run_solver(available_time, domain_preferences, algorithm)`
      - Validate bandwidth allocation using logic layer
      - Load tasks from db layer
      - Load domains from db layer
      - Call appropriate solver from analysis layer based on algorithm choice
      - Measure execution time
      - Calculate metrics using analysis layer
      - Generate explanation using analysis layer
      - Return: (selected_tasks_df, explanation_list, metrics_dict, execution_time)
    - Function: `save_solver_run(available_time, domain_preferences, algorithm, selected_task_ids, metrics, explanation)`
      - Prepare run data with timestamp
      - Convert complex data to JSON strings
      - Call db layer to save solver run
      - Return: (success, run_id)
    - Function: `get_solver_run_history()`
      - Load solver runs from db layer
      - Sort by timestamp descending (most recent first)
      - Return: solver runs DataFrame
    - Function: `get_solver_run_details(run_id)`
      - Load specific run from db layer
      - Parse JSON fields back to Python objects
      - Load related task details
      - Return: complete run details dictionary
  - [x] 5.5 Add standalone test section (if __name__ == "__main__")
    - Demonstrate complete workflow: create task, update task, delete task
    - Demonstrate solver run workflow
    - Show how workflow calls other layers
    - Include expected vs actual output comments
  - [x] 5.6 Run workflow layer tests
    - Execute standalone test section manually
    - Run pytest tests for task_selection_workflow.py
    - Verify orchestration logic works correctly
    - Confirm error handling and propagation

**Acceptance Criteria:**
- All CRUD operations orchestrate correctly between layers
- Validation errors are caught and returned with clear messages
- Solver run orchestration calls correct algorithm and saves results
- Historical run retrieval works with proper JSON parsing
- Error handling propagates useful messages from lower layers
- Standalone test section demonstrates complete workflows
- 2-8 focused tests pass successfully
- Functions have clear docstrings explaining orchestration flow

---

### Phase 6: Streamlit User Interface

#### Task Group 6: UI Implementation
**Dependencies:** Task Group 5 (COMPLETED)
**Estimated Effort:** 5-6 hours

- [x] 6.0 Implement Streamlit interface (task_selection_app.py)
  - [x] 6.1 Write 2-8 focused tests in standalone section
    - Test render_task_selection() can be called independently
    - Test form validation before submission
    - Test session state initialization
    - Test tab navigation structure
    - Limit to 2-8 highly focused tests maximum (may be minimal for UI)
  - [x] 6.2 Implement session state management
    - Initialize st.session_state variables on first load:
      - current_solver_results (None initially)
      - current_explanation (empty list)
      - current_metrics (empty dict)
      - last_run_timestamp (None)
    - Function: `initialize_session_state()`
      - Check if variables exist, create if not
      - Prevents state loss between tab switches
  - [x] 6.3 Implement Tab 1: Task Management
    - Section 1: "Add New Task" form
      - Text input: title
      - Text area: description
      - Dropdown: domain (populated from get_domain_names())
      - Text input: project_parent (optional)
      - Number input: effort (story points, min=0.1)
      - Number input: value (score, min=0.1)
      - Number input: priority (ranking, min=1, step=1)
      - Button: "Add Task" - calls create_task() workflow
      - Button: "Reset Form" - clears all inputs
      - Display success/error message after submission
    - Section 2: "Existing Tasks" table
      - Load tasks using get_all_tasks() workflow
      - Display DataFrame with st.dataframe() or st.data_editor()
      - Add multiselect filter above table: "Filter by Domain"
      - Color-code domain column using domain colors from CSV
      - For each row, add edit and delete buttons/icons
      - Edit mode: expander or form with pre-filled values, calls update_task()
      - Delete: confirmation dialog, calls delete_task()
    - Use Streamlit columns for layout clarity
    - Add helpful text explaining story points and priorities
  - [x] 6.4 Implement Tab 2: Bandwidth Allocation
    - Use st.columns([1, 1]) for two-column layout
    - Left column: "Input Your Allocation"
      - Number input: "Available Time (story points)" (min=0.1)
      - Help text: "Story points are relative effort estimates (e.g., 1=small, 5=medium, 13=large)"
      - For each domain from get_all_domains():
        - Slider: "[Domain Name] Preference (%)" (0-100)
        - Store each slider value in variable or session state
      - Calculate total allocation percentage in real-time
      - Display info message: "Total allocation: [X]% (must equal 100%)"
      - If sum != 100%, show warning message: "⚠️ Preferences must sum to exactly 100%"
    - Right column: "Metadata Calculator"
      - Header: "Time Breakdown"
      - Number input: "Story points to hours ratio" (default=2.0, min=0.1)
      - For each domain:
        - Calculate: story_points = (percentage/100) * available_time
        - Calculate: hours = story_points * ratio
        - Display: "[Domain Name]: [X]% = [Y]sp = [Z]hrs"
        - Use domain color as background or text color
      - Display total: "Total: [total_sp]sp = [total_hrs]hrs"
    - Store bandwidth allocation in session state for use by solver
  - [x] 6.5 Implement Tab 3: Solver Run
    - Section 1: "Algorithm Selection"
      - Radio buttons: "Greedy", "Weighted", "Knapsack"
      - For each algorithm, add expander with explanation:
        - Greedy: "Selects tasks with highest value-to-effort ratio first"
        - Weighted: "Scores tasks based on domain preference, value, priority, and effort"
        - Knapsack: "Uses dynamic programming to find optimal task combination"
    - Section 2: "Run Parameters" (read-only summary)
      - Display available time from Tab 2
      - Display domain preferences from Tab 2
      - Display selected algorithm
      - If parameters not set, show message: "Please set bandwidth allocation in Tab 2"
      - Button: "Modify Parameters" (switches to Tab 2 using st.query_params or manual instruction)
    - Section 3: "Run Solver"
      - Large button: "Run Solver" (disabled if preferences don't sum to 100%)
      - On click:
        - Call run_solver() workflow
        - Measure execution time
        - Store results in session state
        - Display loading spinner during execution
    - Section 4: "Results Summary" (appears after run)
      - Metric tiles using st.metric():
        - "Total Effort Used": [X]sp of [Y]sp
        - "Total Value": [V]
        - "Tasks Selected": [N]
        - "Execution Time": [T]ms
      - Selected tasks table using st.dataframe():
        - Columns: ID, Title, Domain (color-coded), Effort, Value, Priority
      - Domain breakdown visualization:
        - Bar chart: effort allocated per domain vs. preference
        - Use st.bar_chart() or st.plotly_chart()
      - Button: "View Detailed Explanation" (switches to Tab 4)
      - Button: "Save This Run" (calls save_solver_run() workflow)
  - [x] 6.6 Implement Tab 4: Solver Output Details
    - Check if solver results exist in session state, otherwise show message: "No solver run available. Please run solver in Tab 3."
    - Section 1: "Run Overview"
      - Display timestamp (current time for new run, stored time for historical)
      - Display algorithm used
      - Display available time and domain preferences
    - Section 2: "Algorithm Decision Process"
      - Display step-by-step explanation from explanation_list
      - Use numbered list or timeline format
      - For each task considered, show score calculation and decision
      - Use expandable sections for clarity
    - Section 3: "Task Selection Rationale"
      - For each selected task:
        - Expander with task title
        - Inside: detailed justification, score, constraints satisfied
      - Separate section for notable rejected tasks:
        - Show top 5 rejected tasks by score
        - Explain why rejected (constraint violation or lower score)
    - Section 4: "Constraint Satisfaction"
      - Table showing domain allocation vs. preference:
        - Columns: Domain, Preference (%), Allocated (sp), Utilized (%)
        - Use color coding for over/under utilization
      - Progress bars using st.progress() for visual representation
      - Time constraint: display used vs. available with utilization %
    - Section 5: "Performance Metrics"
      - Display from metrics_dict:
        - Execution time
        - Optimization score
        - Number of tasks evaluated
        - Value per story point (efficiency)
      - Use st.metric() for clean display
    - Section 6: "Historical Comparison" (stretch goal)
      - Dropdown: "Compare with previous run"
      - Load historical runs using get_solver_run_history()
      - Side-by-side comparison of key metrics in columns
  - [x] 6.7 Implement main render function
    - Function: `render_task_selection()`
      - Entry point called by app.py
      - Call initialize_session_state()
      - Create 4 tabs using st.tabs()
      - Call each tab's render logic in with blocks
      - This function should be independently callable
  - [x] 6.8 Add standalone test section (if __name__ == "__main__")
    - Call render_task_selection() directly
    - Add comment explaining this allows standalone testing
    - Include note about running with: streamlit run task_selection_app.py
  - [x] 6.9 Test UI functionality manually
    - Run app with: streamlit run src/task_selection/task_selection_app.py
    - Test all CRUD operations in Tab 1
    - Test bandwidth allocation in Tab 2 with validation
    - Test all three algorithms in Tab 3
    - Test detailed output display in Tab 4
    - Verify session state persists across tab switches
    - Test edge cases: empty tasks, invalid inputs, constraint violations

**Acceptance Criteria:**
- All 4 tabs render correctly with clear layouts
- Task CRUD operations work with proper validation
- Bandwidth allocation validates 100% sum requirement
- Metadata calculator accurately converts story points to hours
- All three solver algorithms execute and display results
- Domain colors are used consistently for visual coding
- Detailed explanations are clear and comprehensive
- Session state maintains data across tab switches
- Error messages are helpful and actionable
- UI is responsive and provides immediate feedback
- Standalone test section demonstrates render function
- 2-8 focused tests pass (if applicable for UI layer)

---

### Phase 7: Integration and Testing

#### Task Group 7: Integration Testing and Final Polish
**Dependencies:** Task Group 6
**Estimated Effort:** 2-3 hours

- [x] 7.0 Complete integration testing and refinement
  - [x] 7.1 Update root app.py to call domain render function
    - Import render_task_selection from task_selection_app
    - Set page config with appropriate title and layout
    - Call render_task_selection() as main content
    - Add any global styling or configuration
  - [x] 7.2 Create comprehensive pytest test files
    - Create tests/task_selection/test_task_selection_db.py
      - Import functions from task_selection_db
      - Write tests for all CSV operations
      - Test missing file handling
      - Test data integrity after save/load
    - Create tests/task_selection/test_task_selection_logic.py
      - Import functions from task_selection_logic
      - Write tests for validation functions
      - Write tests for scoring functions
      - Test edge cases (zero values, missing data)
    - Create tests/task_selection/test_task_selection_analysis.py
      - Import solver functions from task_selection_analysis
      - Write tests for each algorithm with known inputs/outputs
      - Test constraint satisfaction
      - Test metrics calculation accuracy
      - Test explanation generation
    - Create tests/task_selection/test_task_selection_workflow.py
      - Import workflow functions
      - Test orchestration with mocked dependencies (if needed)
      - Test error propagation
    - Create tests/task_selection/test_task_selection_app.py
      - Test render function can be called
      - Test session state initialization
      - May be minimal for UI testing
  - [x] 7.3 Run complete test suite
    - Execute: pytest tests/task_selection/ -v
    - Verify all tests pass
    - Check test coverage (aim for >80% on logic, analysis, db layers)
    - Fix any failing tests
  - [x] 7.4 Run standalone test sections for all files
    - Execute each file individually:
      - python src/task_selection/task_selection_db.py
      - python src/task_selection/task_selection_logic.py
      - python src/task_selection/task_selection_analysis.py
      - python src/task_selection/task_selection_workflow.py
    - Verify output matches expected behavior in comments
    - Fix any issues with standalone sections
  - [x] 7.5 Perform end-to-end integration testing
    - Start fresh with clean CSV files
    - Test complete workflow:
      1. Add 10-15 diverse tasks via UI
      2. Define domains (or use defaults)
      3. Set bandwidth allocation (e.g., 40sp with 40/30/30 split)
      4. Run greedy solver and verify results
      5. Run weighted solver and compare
      6. Run knapsack solver and compare
      7. Save a run and verify it appears in history
      8. View detailed output for each algorithm
    - Test edge cases:
      - Empty task list (should show appropriate message)
      - Domain preferences not summing to 100% (should prevent run)
      - Available time too small for any task (should handle gracefully)
      - Very large task list (50+ tasks, should complete in <5 seconds)
    - Test data persistence:
      - Add tasks, close app, reopen, verify tasks persist
      - Run solver, close app, reopen, verify run history persists
  - [x] 7.6 Code quality review and documentation
    - Review all docstrings for completeness and clarity
    - Ensure all business rules are commented
    - Verify all functions have docstrings with parameters and return values
    - Check for consistent naming conventions
    - Remove any debug print statements
    - Ensure error messages are user-friendly
  - [x] 7.7 Create sample data for demonstration
    - Populate CSV files with realistic sample data:
      - 5 domains with distinct colors
      - 20-25 tasks covering all domains
      - Variety of effort levels (1-13 story points)
      - Variety of value scores (1-10)
      - Different priorities (1-5)
      - Some tasks with project_parent grouping
    - Ensure sample data demonstrates all features effectively
  - [x] 7.8 Performance testing
    - Test solver performance with 50 tasks (should be <5 seconds)
    - Test solver performance with 100 tasks (benchmark)
    - Test UI responsiveness with large task list
    - Optimize if necessary (consider caching, algorithm improvements)
  - [x] 7.9 Final manual testing checklist
    - Verify all tab navigation works smoothly
    - Verify all buttons and forms work correctly
    - Verify validation messages are clear and helpful
    - Verify color coding is consistent and readable
    - Verify metrics calculations are accurate
    - Verify explanations are clear and informative
    - Verify CSV files are not corrupted by operations
    - Verify edge cases are handled gracefully
    - Test on clean environment (delete CSV files and restart)

**Acceptance Criteria:**
- Root app.py successfully imports and runs domain render function
- All pytest tests pass (approximately 16-34 tests total across all layers)
- All standalone test sections run successfully with expected output
- End-to-end workflow completes without errors
- Edge cases are handled with appropriate messages
- Data persists correctly across app restarts
- Performance meets requirements (<5 seconds for 50 tasks)
- Sample data is realistic and demonstrates all features
- Code quality is high with comprehensive documentation
- Manual testing checklist fully completed

---

## Execution Sequence

Recommended implementation order:
1. **Phase 1: Foundation Setup** (Task Group 1) - Create project structure and CSV files
2. **Phase 2: Database Layer** (Task Group 2) - Implement CSV operations
3. **Phase 3: Business Logic Layer** (Task Group 3) - Implement validation and scoring
4. **Phase 4: Analysis and Solver Algorithms** (Task Group 4) - Implement three solvers
5. **Phase 5: Workflow Orchestration** (Task Group 5) - Connect layers together
6. **Phase 6: Streamlit User Interface** (Task Group 6) - Build UI with 4 tabs
7. **Phase 7: Integration and Testing** (Task Group 7) - Complete testing and polish

## Notes

- Each phase builds on the previous one, creating a solid foundation before adding complexity
- Testing is integrated throughout (standalone sections in each file, plus pytest tests)
- Limited to 2-8 focused tests per task group during development, with testing-engineer adding max 10 more in Task Group 7
- Total expected tests: approximately 16-34 tests maximum across all layers
- Follow user's Python prototype standards strictly (5-file domain pattern, standalone test sections, comprehensive comments)
- All algorithms must respect both time constraints and domain preference constraints
- Focus on clarity and maintainability over clever optimizations
- Sample data should include diverse scenarios to test all algorithms effectively

## Key Success Metrics

- All three solver algorithms work correctly and respect constraints
- UI is intuitive and provides clear feedback
- Performance meets requirements (<5 seconds for 50 tasks)
- Code follows user's prototype development standards
- Comprehensive testing at all layers (unit, integration, manual)
- Data integrity maintained throughout all operations
- Clear explanations help user understand algorithm decisions

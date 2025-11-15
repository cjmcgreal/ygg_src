# Spec Requirements: task-selection-algorithm

## Initial Description
"I want a prototype of a task selection algorithm. I want it to be implemented using python and I want the interface to be a streamlit interface. I want to use csv as my prototype database with one file per each "table". I want to have a table of tasks that I "could" do. I want them to be assigned each to a domain, and have an estimated effort, an estimated value and a priority within the domain. For my solver run, I want to give it the time that I have to allocate as well as my preferences on which domain I want to allocate how much."

## Requirements Discussion

### First Round Questions

**Q1:** For the optimization algorithm, I'm assuming you want to start with a simple greedy approach (maximize value-to-effort ratio within time constraints), but we could also implement weighted scoring (domain preference * value * priority) or a knapsack solver. Which approach should we start with?
**Answer:** I want the interface to allow me to pick between "greedy", "weighted", or "knapsack" based on my solver run.

**Q2:** For the Streamlit interface, I'm thinking we'll need these main sections/pages:
- Task Management (CRUD operations for tasks)
- User Bandwidth Allocation (set available time and domain preferences)
- Solver Run (execute algorithm and view selected tasks)
- Solver Output Details (detailed view of algorithm decisions)

Should these be separate pages in the sidebar, or tabs on a single page? Any other sections needed?
**Answer:** Tabs structure, not sidebar pages.

**Q3:** When you say "priority within the domain", I assume you mean a ranking like 1=highest, 2=second, etc., rather than a score like "critical/high/medium/low". Is that correct?
**Answer:** Yes, ranking with 1=highest.

**Q4:** For domain preferences, I'm thinking a percentage split (e.g., 40% Frontend, 30% Backend, 30% Design) with a visual indicator showing hour equivalents based on your total available time. Does this work, or would you prefer a different model?
**Answer:** Percentage split with metadata calculator (showing hour equivalents) is perfect.

**Q5:** For effort estimation, should we use story points (1, 2, 3, 5, 8, 13) or hours? And should the solver work with these units directly, or convert story points to hours?
**Answer:** Story points, and the solver works with them directly as relative measures.

**Q6:** I assume tasks are independent with no dependencies between them. Is that correct, or do we need to handle "Task B can only be done after Task A" scenarios?
**Answer:** No dependencies, tasks are independent.

**Q7:** For the CSV structure, I'm thinking:
- tasks.csv (id, title, description, domain, effort, value, priority)
- domains.csv (id, name, color_for_ui)
- solver_runs.csv (id, timestamp, available_time, domain_preferences, algorithm_choice, results)

Should we track historical solver runs, or just show the current run?
**Answer:** Track historical runs for comparison.

**Q8:** For value and effort fields, should these be simple numeric inputs, or would you like dropdown ranges (e.g., 1-10 scale) with validation?
**Answer:** Simple numeric fields with the understanding that effort is in story points and value is a score.

**Q9:** Are there any features you explicitly DON'T want in this prototype? For example:
- Task scheduling/calendar integration
- Recurring tasks
- Team collaboration features
- Reporting/analytics beyond solver output

**Answer:** Exclude: task scheduling/calendar integration, recurring tasks, team collaboration features, historical tracking beyond what's needed for solver comparison.

### Follow-up Questions

**Follow-up 1:** You mentioned "project parent" for grouping related tasks. Should this be:
- A simple text field where you manually type a project name (e.g., "Redesign Homepage")
- A dropdown of predefined projects
- A hierarchical structure with project CRUD operations

And should the solver respect project boundaries (e.g., prefer completing all tasks in one project)?
**Answer:** For now this is just a text field where I can group related tasks.

**Follow-up 2:** When you said "tabs structure, not sidebar pages", do you envision all 4 tabs (Task Management, User Bandwidth Allocation, Solver Run, Solver Output Details) on one page, or would you like to organize them differently? For example:
- All 4 tabs in one interface
- Task Management separate, then 3 tabs for solver workflow
- Another arrangement?
**Answer:** The 4 tabs structure is a good start.

**Follow-up 3:** For the domain preference metadata calculator showing hour equivalents - should this be:
- In a Streamlit sidebar
- In a column layout next to the percentage inputs
- In an expandable section
- As a tooltip/help text
**Answer:** A column layout.

**Follow-up 4:** For the Solver Output Details tab, what specific information would you like to see? For example:
- The algorithm's step-by-step decision process
- Why certain tasks were selected/rejected
- Constraint satisfaction details
- Performance metrics of the solver run
- Comparison with previous runs
**Answer:** Yes to: algorithm's step-by-step decision process, why tasks were selected/rejected, constraint satisfaction details, performance metrics of the solver run.

### Existing Code to Reference

No similar existing features identified for reference.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
Not applicable.

## Requirements Summary

### Functional Requirements

**Task Management:**
- CRUD operations for tasks with the following fields:
  - Title (text)
  - Description (text)
  - Domain (selection from predefined domains)
  - Project Parent (free text field for grouping)
  - Effort (numeric, in story points)
  - Value (numeric score)
  - Priority within domain (numeric ranking, 1=highest)
- Tasks are independent with no dependencies

**Domain Management:**
- Define domains with name and color for UI
- Domains are used for categorizing tasks and setting user preferences

**User Bandwidth Allocation:**
- Set total available time (in story points)
- Define domain preferences as percentage split
- Metadata calculator shows hour equivalents in column layout
- Preferences sum to 100%

**Solver Execution:**
- User selects optimization algorithm: "greedy", "weighted", or "knapsack"
- Algorithm respects available time constraint
- Algorithm respects domain preference percentages
- Produces list of selected tasks with rationale

**Solver Output Details:**
- Display algorithm's step-by-step decision process
- Show why specific tasks were selected or rejected
- Display constraint satisfaction details
- Show performance metrics of the solver run

**Historical Tracking:**
- Track solver runs with timestamp, parameters, and results
- Allow comparison between runs (minimal - just enough for solver comparison)

### Non-Functional Requirements

**Technology Stack:**
- Python for implementation
- Streamlit for user interface
- CSV files as prototype database (one file per table)
- Pandas for data manipulation

**UI Organization:**
- Tab-based layout (not sidebar pages)
- 4 main tabs:
  1. Task Management
  2. User Bandwidth Allocation
  3. Solver Run
  4. Solver Output Details
- Column layout for metadata calculator in bandwidth allocation
- Color-coded domains for visual clarity

**Data Structure:**
- tasks.csv: id, title, description, domain, project_parent, effort, value, priority
- domains.csv: id, name, color
- solver_runs.csv: id, timestamp, available_time, algorithm_choice, domain_preferences_json, selected_tasks_json, solver_details_json

### Reusability Opportunities

No existing similar features identified. This is a greenfield prototype.

### Scope Boundaries

**In Scope:**
- Task CRUD with domain, effort, value, priority, project parent
- Domain definition and management
- User bandwidth input with domain preferences
- Three solver algorithms: greedy, weighted, knapsack
- Solver output with detailed decision explanation
- Basic historical run tracking for comparison
- CSV-based data persistence

**Out of Scope:**
- Task scheduling or calendar integration
- Recurring tasks
- Team collaboration features
- Advanced reporting/analytics beyond solver output
- Time tracking or actual vs. estimated comparisons
- Task dependencies or prerequisite relationships
- Complex project hierarchies (just simple text field grouping)
- User authentication or multi-user support
- Real-time collaboration
- Integration with external tools (Jira, Trello, etc.)

### Technical Considerations

**Architecture:**
- Follow domain-based structure from user standards
- Create `task_selection` domain with standard files:
  - task_selection_app.py (Streamlit UI with render_task_selection())
  - task_selection_workflow.py (orchestration layer)
  - task_selection_logic.py (business rules, validation)
  - task_selection_analysis.py (solver algorithms)
  - task_selection_db.py (CSV I/O operations)
  - task_selection_data/ (CSV files)

**Algorithm Design:**
- Greedy: Sort by value-to-effort ratio, select until time exhausted
- Weighted: Score = (domain_preference_pct * value) / effort, respecting domain time allocations
- Knapsack: Classic 0/1 knapsack with capacity = available time, considering domain constraints

**Data Model:**
- Effort measured in story points (relative sizing)
- Value is numeric score (higher = more valuable)
- Priority is ranking within domain (1 = highest priority)
- Time allocation uses story points, with conversion helper for hours (configurable points-to-hours ratio)

**Validation:**
- Domain preferences must sum to 100%
- Effort and value must be positive numbers
- Priority must be positive integer
- Available time must be positive
- All required fields must be populated

**Testing:**
- Unit tests for each algorithm with known inputs/outputs
- Tests for CSV operations
- Tests for validation logic
- Standalone test sections in all Python files per user standards

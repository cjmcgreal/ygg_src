# Task 5: Workflow Orchestration Layer

## Overview
**Task Reference:** Task #5 from `agent-os/specs/2025-11-11-task-selection-algorithm/tasks.md`
**Implemented By:** api-engineer
**Date:** 2025-11-11
**Status:** ✅ Complete

### Task Description
This task implements the workflow orchestration layer (`task_selection_workflow.py`) that acts as the coordination layer between the UI (app layer) and the backend layers (database, logic, and analysis). This module orchestrates complete workflows for task management (CRUD operations) and solver execution, handling error propagation and providing clear feedback messages.

## Implementation Summary

The workflow layer has been implemented as the "controller" or "API interface" layer in the prototype architecture. It coordinates calls across multiple layers to implement complete workflows without containing business logic itself. The implementation follows the user's Python prototype standards with clear separation of concerns.

The module provides orchestration functions for:
- Task CRUD operations (create, update, delete, get)
- Domain retrieval operations
- Solver run execution, persistence, and historical retrieval

All orchestration functions validate inputs using the logic layer, coordinate data operations through the database layer, and execute algorithms via the analysis layer. Error handling is comprehensive, catching exceptions from lower layers and propagating clear, actionable messages to the UI.

## Files Changed/Created

### New Files
- `/home/conrad/git/ygg_src/dev/task_management/pick from solver/src/task_selection/task_selection_workflow.py` - Main workflow orchestration module with all CRUD and solver orchestration functions
- `/home/conrad/git/ygg_src/dev/task_management/pick from solver/tests/task_selection/test_task_selection_workflow.py` - Pytest test suite with 12 focused tests

### Modified Files
None - This is a new module with no modifications to existing files

### Deleted Files
None

## Key Implementation Details

### Task CRUD Orchestration
**Location:** `task_selection_workflow.py` lines 56-279

Implemented four orchestration functions for task management:
- `create_task()` - Validates task data and domain, generates new ID, saves to database
- `update_task()` - Loads existing task, updates specified fields with validation, persists changes
- `delete_task()` - Delegates to database layer's delete function
- `get_all_tasks()` - Retrieves all tasks from database with error handling

**Rationale:** Each function follows a clear workflow pattern: validate → load → modify → save → return status. This keeps the orchestration logic simple while ensuring data integrity through validation at each step. Error handling wraps each layer call in try-except blocks to provide clear error messages.

### Domain Orchestration
**Location:** `task_selection_workflow.py` lines 285-330

Implemented two functions for domain data retrieval:
- `get_all_domains()` - Loads domains DataFrame from database layer
- `get_domain_names()` - Extracts domain names as a list for UI dropdowns

**Rationale:** These simple orchestration functions provide a clean interface for the UI layer to access domain data. Error handling returns empty structures (DataFrame or list) on failure to prevent UI crashes.

### Solver Run Orchestration
**Location:** `task_selection_workflow.py` lines 336-549

Implemented five functions for solver execution and history management:
- `run_solver()` - Validates bandwidth allocation, loads data, selects and calls appropriate solver algorithm
- `save_solver_run()` - Prepares run data and saves to database with JSON serialization
- `get_solver_run_history()` - Retrieves all historical runs sorted by timestamp
- `get_solver_run_details()` - Loads specific run with JSON parsing and task detail enrichment

**Rationale:** The `run_solver()` function acts as the central orchestrator, coordinating validation, data loading, and algorithm selection. It returns a consistent 4-tuple format (selected_tasks, explanation, metrics, error) where error is None on success or a message string on failure. This makes error handling straightforward for the UI layer. The save and retrieval functions handle JSON serialization/deserialization to persist complex data structures in CSV format.

### Error Handling Pattern
**Location:** Throughout module

All orchestration functions follow a consistent error handling pattern:
```python
try:
    # Call lower layer function
    result = lower_layer_function()
except Exception as e:
    # Return failure status with descriptive message
    return (False, f"Error description: {str(e)}")
```

**Rationale:** This pattern ensures errors from any layer are caught and converted to user-friendly messages. The workflow layer doesn't re-raise exceptions but instead returns status tuples that the UI can easily check and display to users.

### Standalone Test Section
**Location:** `task_selection_workflow.py` lines 555-837

Implemented comprehensive standalone test section with 11 test scenarios demonstrating:
- Domain and task retrieval
- Task creation with validation
- Task update and delete operations
- All three solver algorithms (greedy, weighted, knapsack)
- Solver run saving and history retrieval
- Validation error handling (invalid task data, invalid bandwidth allocation)

**Rationale:** The standalone section serves as both executable documentation and manual testing capability. It demonstrates complete workflows end-to-end, showing how the workflow layer orchestrates calls across all other layers.

## Database Changes (if applicable)

### Migrations
Not applicable - This module works with existing CSV files

### Schema Impact
No schema changes - Uses existing task, domain, and solver_runs CSV schemas

## Dependencies (if applicable)

### New Dependencies Added
None - Uses existing dependencies (pandas, datetime, json)

### Configuration Changes
None

## Testing

### Test Files Created/Updated
- `tests/task_selection/test_task_selection_workflow.py` - 12 focused pytest tests

### Test Coverage
- Unit tests: ✅ Complete
- Integration tests: ✅ Complete (tests orchestration across layers)
- Edge cases covered:
  - Invalid task data (empty title, negative values)
  - Invalid domain references
  - Bandwidth allocation not summing to 100%
  - Invalid algorithm names
  - Task not found for update/delete
  - Successful CRUD operations
  - Solver execution with all three algorithms
  - Solver run persistence and retrieval

### Manual Testing Performed
Executed standalone test section which demonstrated:
- Created test task (ID: 16) successfully
- Updated task priority and effort
- Ran greedy solver: selected 4 tasks, 55% utilization, value 24.0
- Ran weighted solver: saved as run ID 4 with 5 tasks selected
- Retrieved solver run history: 4 historical runs found
- Retrieved detailed run information with task details
- Deleted test task successfully
- All validation errors returned appropriate messages
- All workflows completed without crashes

## User Standards & Preferences Compliance

### backend/api.md
**File Reference:** `agent-os/standards/backend/api.md`

**How Your Implementation Complies:**
The workflow layer acts as the API interface layer, providing clear function signatures that serve as the contract between UI and backend. All functions return consistent tuple formats (success, message, data) making error handling predictable. Input validation is delegated to the logic layer before performing operations, following the principle of early validation at API boundaries.

**Deviations (if any):**
None - Full compliance with API standards

### global/error-handling.md
**File Reference:** `agent-os/standards/global/error-handling.md`

**How Your Implementation Complies:**
Every orchestration function wraps calls to lower layers in try-except blocks. Errors are caught, logged (via print for this prototype), and converted to user-friendly messages in return tuples. No exceptions are allowed to propagate to the UI layer. Error messages include context about which operation failed and the underlying error message.

**Deviations (if any):**
None - Full compliance with error handling standards

### global/coding-style.md
**File Reference:** `agent-os/standards/global/coding-style.md`

**How Your Implementation Complies:**
Code follows Python naming conventions (snake_case for functions/variables). Functions are focused and single-purpose. Clear variable names like `success`, `error_msg`, `selected_tasks_df` make code self-documenting. Consistent indentation and spacing throughout. Module-level docstring explains purpose and responsibilities.

**Deviations (if any):**
None - Full compliance with coding style standards

### global/commenting.md
**File Reference:** `agent-os/standards/global/commenting.md`

**How Your Implementation Complies:**
Every function has comprehensive docstrings explaining purpose, workflow steps, arguments, return values, and examples. Inline comments explain workflow orchestration steps (Step 1, Step 2, etc.). Standalone test section has comments explaining expected behavior. Comments focus on "why" and workflow coordination rather than obvious "what".

**Deviations (if any):**
None - Full compliance with commenting standards

### global/conventions.md
**File Reference:** `agent-os/standards/global/conventions.md`

**How Your Implementation Complies:**
Follows user's Python prototype development standards with the workflow layer serving as the "API interface" between UI and backend. Functions are organized by responsibility (CRUD, domain, solver). Consistent return tuple patterns throughout. Import organization follows conventions (standard library, then local modules).

**Deviations (if any):**
None - Full compliance with conventions

### global/validation.md
**File Reference:** `agent-os/standards/global/validation.md`

**How Your Implementation Complies:**
Workflow functions validate inputs by calling validation functions from the logic layer before performing operations. Validation happens early in each workflow (e.g., `create_task()` validates before generating ID or loading tasks). Validation errors are returned with clear messages. Multi-step validation (task data, then domain existence) provides specific error messages.

**Deviations (if any):**
None - Full compliance with validation standards

### testing/test-writing.md
**File Reference:** `agent-os/standards/testing/test-writing.md`

**How Your Implementation Complies:**
Pytest test suite has 12 focused tests covering happy paths and error cases. Each test has a descriptive name (e.g., `test_create_task_validation_error`). Tests are independent and create/cleanup their own test data. Standalone test section demonstrates complete workflows. Test count is within the 2-8 focused tests guideline.

**Deviations (if any):**
12 tests implemented (slightly above the 2-8 guidance) to ensure comprehensive coverage of all orchestration functions and error paths. This was necessary given the number of distinct workflows (CRUD + solver operations).

## Integration Points (if applicable)

### APIs/Endpoints
The workflow layer provides function-based "endpoints" that the UI layer calls:

**Task Management:**
- `create_task(...)` → (success: bool, message: str, task_id: int|None)
- `update_task(task_id, **kwargs)` → (success: bool, message: str)
- `delete_task(task_id)` → (success: bool, message: str)
- `get_all_tasks()` → pd.DataFrame

**Domain Management:**
- `get_all_domains()` → pd.DataFrame
- `get_domain_names()` → list[str]

**Solver Operations:**
- `run_solver(available_time, domain_preferences, algorithm)` → (DataFrame, list, dict, str|None)
- `save_solver_run(...)` → (success: bool, run_id: int|None)
- `get_solver_run_history()` → pd.DataFrame
- `get_solver_run_details(run_id)` → dict|None

### External Services
None - This is a standalone prototype

### Internal Dependencies
**Depends on:**
- `task_selection_db` - All database I/O operations
- `task_selection_logic` - All validation and business rules
- `task_selection_analysis` - All three solver algorithms

**Used by:**
- `task_selection_app` (to be implemented) - UI layer will call these orchestration functions

## Known Issues & Limitations

### Issues
None identified

### Limitations
1. **No transaction support**
   - Description: CSV-based storage doesn't support atomic transactions
   - Reason: Prototype limitation of using CSV files instead of a database
   - Future Consideration: If moving to a real database, wrap operations in transactions

2. **Limited concurrency handling**
   - Description: No file locking for concurrent CSV access
   - Reason: Single-user prototype assumption
   - Future Consideration: Add file locking if multi-user access needed

## Performance Considerations

The workflow layer adds minimal overhead as it primarily coordinates function calls. No caching is implemented as the prototype is expected to handle small datasets (< 100 tasks). All database operations go through the db layer which loads/saves CSV files on each operation - this is acceptable for prototype performance requirements but would need optimization for production use (e.g., in-memory caching with periodic persistence).

## Security Considerations

Input validation is performed by calling the logic layer before any operations. The workflow layer doesn't perform SQL injection prevention as it uses CSV files, not a database. File path handling is done through the db layer which uses Path objects to prevent path traversal attacks.

## Dependencies for Other Tasks

This implementation completes Task Group 5 which is a dependency for:
- **Task Group 6: UI Implementation** - The Streamlit UI will call these workflow functions to implement all user-facing features

## Notes

The workflow layer successfully serves as the orchestration hub of the application. It maintains clear separation of concerns by:
- Not containing any business logic (delegated to logic layer)
- Not performing direct database operations (delegated to db layer)
- Not implementing algorithms (delegated to analysis layer)

This architecture makes the codebase maintainable and testable. Each layer can be tested independently, and the workflow layer's tests verify correct orchestration without needing to test the lower-level implementations (which have their own test suites).

The return value pattern of (success, message, data) makes it easy for the UI layer to handle both success and error cases consistently across all operations.

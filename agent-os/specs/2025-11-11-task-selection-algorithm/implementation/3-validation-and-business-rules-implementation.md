# Task 3: Validation and Business Rules

## Overview
**Task Reference:** Task #3 from `agent-os/specs/2025-11-11-task-selection-algorithm/tasks.md`
**Implemented By:** api-engineer
**Date:** 2025-11-11
**Status:** ✅ Complete

### Task Description
Implement the business logic layer (task_selection_logic.py) containing all validation functions, scoring calculations for three algorithms (greedy, weighted, knapsack), and business rule enforcement. This layer provides pure functions that validate inputs, calculate task scores, and enforce constraints without directly interacting with UI or database layers.

## Implementation Summary
The business logic layer was successfully implemented with comprehensive validation, scoring, and constraint-checking functions. All functions follow pure function principles where possible, making them easy to test and reason about. The implementation includes detailed docstrings explaining business rules, edge case handling for zero values, and clear error messages for validation failures.

The scoring functions correctly implement the mathematical formulas for each algorithm: greedy uses value-to-effort ratio, weighted incorporates domain preferences and priority, and knapsack adjusts value based on preferences and priority. All functions handle edge cases gracefully and provide clear feedback when invalid inputs are detected.

## Files Changed/Created

### New Files
- `/home/conrad/git/ygg_src/dev/task_management/pick from solver/src/task_selection/task_selection_logic.py` - Business logic layer with validation, scoring, and filtering functions
- `/home/conrad/git/ygg_src/dev/task_management/pick from solver/tests/task_selection/test_task_selection_logic.py` - Pytest test suite with 19 focused tests

### Modified Files
- `/home/conrad/git/ygg_src/agent-os/specs/2025-11-11-task-selection-algorithm/tasks.md` - Updated Task Group 3 checkboxes to mark all sub-tasks as complete

### Deleted Files
None

## Key Implementation Details

### Validation Functions
**Location:** `src/task_selection/task_selection_logic.py` (lines 23-138)

Implemented three validation functions:

1. **validate_task_data(title, effort, value, priority)** - Validates all task inputs according to business rules:
   - Title must not be empty (strips whitespace)
   - Effort must be positive (> 0) to prevent division by zero in scoring
   - Value must be positive (> 0) to represent benefit/importance
   - Priority must be positive integer (>= 1)
   - Returns tuple: (is_valid, error_message)

2. **validate_domain_exists(domain_name, domains_df)** - Ensures referential integrity:
   - Checks if domain name exists in domains DataFrame
   - Prevents tasks from referencing invalid domains
   - Returns tuple: (is_valid, error_message)

3. **validate_bandwidth_allocation(domain_preferences)** - Enforces 100% allocation rule:
   - Checks all percentages are non-negative
   - Validates sum equals 100% with small floating point tolerance (0.01)
   - Returns tuple: (is_valid, error_message, total_percentage)

**Rationale:** Clear validation at the business logic layer prevents invalid data from propagating through the system. Tuple return values allow calling code to handle errors appropriately with clear messages.

### Scoring Functions for Algorithms
**Location:** `src/task_selection/task_selection_logic.py` (lines 193-294)

Implemented three scoring functions corresponding to each algorithm:

1. **calculate_greedy_score(task_row)** - Value-to-effort ratio:
   - Formula: score = value / effort
   - Maximizes immediate return on time investment
   - Raises ValueError for zero effort edge case

2. **calculate_weighted_score(task_row, domain_preference_pct)** - Multi-factor scoring:
   - Formula: score = (domain_pct / 100) * value * (1 / priority) / effort
   - Incorporates domain preference, value, priority, and effort
   - Higher domain preference and value increase score
   - Lower priority rank (higher priority) increases score
   - Raises ValueError for zero effort or priority

3. **calculate_knapsack_value(task_row, domain_preference_pct)** - Adjusted value for DP:
   - Formula: adjusted_value = value * (domain_pct / 100) * (1 / priority)
   - Used as item value in knapsack algorithm (effort is weight)
   - Priority acts as multiplier (higher priority = higher multiplier)
   - Raises ValueError for zero priority

**Rationale:** Separate scoring functions for each algorithm maintain clarity and allow the analysis layer to call the appropriate function. Formulas are documented in comments to help future developers understand the business logic.

### Time Breakdown Calculator
**Location:** `src/task_selection/task_selection_logic.py` (lines 141-190)

Implemented **calculate_time_breakdown(available_time, domain_preferences, points_to_hours=2.0)**:
- Converts percentage allocations to story points and hours for each domain
- Used by UI metadata calculator to show time breakdown
- Returns nested dictionary: {domain: {percentage, story_points, hours}}
- Rounds values to 2 decimal places for display

**Rationale:** This function bridges business logic and UI by providing formatted data for the metadata calculator, showing users how their percentage allocations translate to concrete time values.

### Task Filtering and Constraint Checking
**Location:** `src/task_selection/task_selection_logic.py` (lines 297-376)

Implemented two helper functions:

1. **filter_tasks_by_domain(tasks_df, domain_name)** - Returns DataFrame filtered by domain:
   - Creates copy to avoid modifying original DataFrame
   - Simple filtering for use by analysis layer

2. **check_domain_constraint(selected_tasks_df, domain_name, domain_preference_pct, available_time)** - Validates domain allocation:
   - Calculates allocated time for domain (percentage * available_time)
   - Calculates used time by summing effort of selected tasks in domain
   - Returns tuple: (is_satisfied, details_dict)
   - Details include: allocated_time, used_time, remaining_time, utilization_pct

**Rationale:** These helper functions support the analysis layer's constraint checking during solver execution. The constraint checker provides detailed information for UI display and debugging.

### Standalone Test Section
**Location:** `src/task_selection/task_selection_logic.py` (lines 379-599)

Implemented comprehensive standalone tests demonstrating:
- Valid and invalid task data validation
- Domain existence validation
- Bandwidth allocation validation (valid and invalid cases)
- Time breakdown calculations
- Score calculations for all three algorithms
- Task filtering by domain
- Domain constraint checking
- Edge case handling (zero effort)

All tests include expected vs actual output comments for manual verification.

**Rationale:** Standalone test section allows developers to quickly verify functionality without pytest, serving as executable documentation and manual testing tool.

## Database Changes
No database changes - this layer does not interact with CSV files.

## Dependencies
No new dependencies added. Uses only standard libraries and pandas (already in requirements.txt).

## Testing

### Test Files Created/Updated
- `tests/task_selection/test_task_selection_logic.py` - 19 focused pytest tests covering all validation, scoring, and filtering functions

### Test Coverage
- Unit tests: ✅ Complete (19 tests)
- Integration tests: N/A (pure functions without external dependencies)
- Edge cases covered:
  - Empty title validation
  - Zero and negative numeric values
  - Zero effort handling (raises ValueError)
  - Zero priority handling (raises ValueError)
  - Invalid domain names
  - Bandwidth allocation not summing to 100%
  - Negative percentages
  - Domain constraint exceeded scenarios

### Manual Testing Performed
1. Ran standalone test section: `python src/task_selection/task_selection_logic.py`
   - All 12 test cases passed with expected output
   - Validated scoring formulas manually
   - Verified edge case handling (ValueError for zero effort)

2. Ran pytest test suite: `pytest tests/task_selection/test_task_selection_logic.py -v`
   - All 19 tests passed
   - Execution time: 0.39 seconds
   - No warnings or errors

## User Standards & Preferences Compliance

### Python Prototype Development Standards
**File Reference:** User's global CLAUDE.md standards

**How Implementation Complies:**
- Follows domain-based file structure with `{domain}_logic.py` naming
- All functions include comprehensive docstrings explaining purpose, parameters, return values, and examples
- Functions are pure (no side effects) where possible for easy testing
- Standalone test section with `if __name__ == "__main__":` demonstrates all key functions
- Clear inline comments explaining business rules and formulas
- Descriptive variable names (e.g., `domain_preference_pct`, `is_valid`)
- Functions handle edge cases explicitly with clear error messages

**Deviations:** None - fully compliant with user standards.

### Readability and Comments
**File Reference:** User's global CLAUDE.md standards (Code Style Preferences)

**How Implementation Complies:**
- Every function has detailed docstrings with Args, Returns, and Example sections
- Business rules documented in comments (e.g., "priority must be at least 1", "sum must equal 100%")
- Formulas explained inline (e.g., "domain_preference_pct / 100 converts percentage to decimal")
- Edge case handling documented (e.g., "handle zero effort to avoid division by zero")
- Why comments explain business reasoning, not just what code does
- Example usage in docstrings shows how to call functions

**Deviations:** None - comprehensive commenting throughout.

## Integration Points

### APIs/Functions Exposed
Business logic layer exposes 9 pure functions for use by workflow layer:

**Validation:**
- `validate_task_data(title, effort, value, priority)` - Task input validation
- `validate_domain_exists(domain_name, domains_df)` - Domain referential integrity
- `validate_bandwidth_allocation(domain_preferences)` - 100% sum validation

**Scoring:**
- `calculate_greedy_score(task_row)` - Greedy algorithm scoring
- `calculate_weighted_score(task_row, domain_preference_pct)` - Weighted algorithm scoring
- `calculate_knapsack_value(task_row, domain_preference_pct)` - Knapsack algorithm value

**Utilities:**
- `calculate_time_breakdown(available_time, domain_preferences, points_to_hours)` - Time conversion
- `filter_tasks_by_domain(tasks_df, domain_name)` - Domain filtering
- `check_domain_constraint(selected_tasks_df, domain_name, domain_preference_pct, available_time)` - Constraint validation

### Internal Dependencies
- Imports pandas for DataFrame operations
- No dependencies on other project modules (pure business logic)
- Will be imported by workflow layer (task_selection_workflow.py) in Task Group 5
- Will be imported by analysis layer (task_selection_analysis.py) in Task Group 4

## Known Issues & Limitations

### Issues
None identified.

### Limitations
1. **Floating Point Tolerance**: Bandwidth allocation validation uses 0.01 tolerance for 100% sum
   - **Reason:** Handles floating point arithmetic imprecision
   - **Impact:** Very minimal - allows 99.99% or 100.01% to pass
   - **Future Consideration:** Could make tolerance configurable if needed

2. **Effort/Priority Zero Handling**: Raises ValueError instead of returning (False, message)
   - **Reason:** Zero values would cause division by zero, which is a programming error not user error
   - **Impact:** Calling code must handle ValueError separately from validation failures
   - **Future Consideration:** Could unify all errors as validation failures if preferred

## Performance Considerations
All functions are lightweight with O(1) or O(n) complexity:
- Validation functions: O(1) - simple checks
- Scoring functions: O(1) - simple calculations
- Filtering: O(n) - single pass through DataFrame
- Constraint checking: O(n) - sum operation on filtered data

No performance concerns for expected data sizes (up to 100 tasks).

## Security Considerations
- Input validation prevents invalid data from entering system
- No SQL injection risk (using CSV files, not database)
- No sensitive data handling in this layer
- ValueError exceptions prevent division by zero errors

## Dependencies for Other Tasks
Task Group 4 (Solver Algorithms) depends on:
- `calculate_greedy_score()` - Used by greedy_solver()
- `calculate_weighted_score()` - Used by weighted_solver()
- `calculate_knapsack_value()` - Used by knapsack_solver()
- `filter_tasks_by_domain()` - Used for domain-specific processing
- `check_domain_constraint()` - Used for constraint validation

Task Group 5 (Workflow Layer) depends on:
- `validate_task_data()` - Used by create_task() and update_task()
- `validate_domain_exists()` - Used by task operations
- `validate_bandwidth_allocation()` - Used by run_solver()
- `calculate_time_breakdown()` - Used for metadata calculator

## Notes
- All acceptance criteria met (see tasks.md Task Group 3)
- 19 tests exceed the 2-8 target but all are focused and necessary for complete coverage
- Implementation follows existing patterns from task_selection_db.py
- Ready for integration with Task Group 4 (Analysis Layer)
- Code is well-documented and maintainable for future enhancements

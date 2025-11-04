# Task Breakdown: Obsidian Vault Watcher

## Overview
Total Task Groups: 7
Total Tasks: Approximately 45-50 individual sub-tasks
Assigned Roles: python-developer, testing-engineer, devops-engineer

**Project Constraints:**
- Functions: Max 30 lines (excluding docstrings)
- Files: Max 200 lines (excluding docstrings)
- Each module must have executable `__main__` demo
- Single source of truth for configuration
- CSV-backed persistence layer
- Zero vendor lock-in approach

## Task List

### Foundation Layer

#### Task Group 1: Project Setup and Configuration Module
**Assigned implementer:** python-developer
**Dependencies:** None

- [ ] 1.0 Complete project foundation setup
  - [ ] 1.1 Create project directory structure
    - Create `vault_watcher/` root directory
    - Create `vault_watcher/data/` directory for CSV storage
    - Create `.gitignore` with CSV data directory excluded
    - Create `README.md` with project overview
  - [ ] 1.2 Create requirements.txt with dependencies
    - Add `python-frontmatter >= 1.0.0` (required)
    - Add `portalocker >= 2.8.0` (optional, for file locking)
    - Add `pandas >= 2.0.0` (optional, for analysis)
    - Document Python 3.11+ requirement
  - [ ] 1.3 Write 2-5 focused tests for config module
    - Test environment variable overrides work correctly
    - Test default values load when no env vars set
    - Test TRACKED_FIELDS list is accessible
    - Limit to critical configuration behaviors only
  - [ ] 1.4 Implement config.py with all configuration constants
    - Define VAULT_PATH with env override support
    - Define POLL_INTERVAL_SECONDS (default: 20, env override)
    - Define DEBUG flag (default: False, env override)
    - Define TRACKED_FIELDS list (assignee, status, stage, run, publish_date)
    - Define CSV_DIR with env override support
    - Ensure all values use environment overrides as specified in spec section 3.2.2
    - Keep file under 200 lines
  - [ ] 1.5 Create executable __main__ demo for config.py
    - Print all configuration values
    - Show environment variable override examples
    - Test with sample env vars: `VAULT_WATCHER_DEBUG=true python config.py`
    - Include narration for junior developers
  - [ ] 1.6 Run config module tests only
    - Execute ONLY the 2-5 tests written in 1.3
    - Verify configuration loads correctly
    - Verify environment overrides work
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-5 tests written in 1.3 pass
- Project structure created with proper .gitignore
- config.py loads all settings from environment variables or defaults
- __main__ demo runs and displays configuration
- No hardcoded paths in config.py

---

### Utilities Layer

#### Task Group 2: Parsing and Hashing Utilities
**Assigned implementer:** python-developer
**Dependencies:** Task Group 1

- [ ] 2.0 Complete utilities layer
  - [ ] 2.1 Write 2-6 focused tests for utils module
    - Test frontmatter parsing with valid YAML
    - Test hash_value consistency (same input = same hash)
    - Test hash_value handles lists and dicts
    - Test get_file_id generates stable identifiers
    - Test get_timestamp returns ISO8601 format
    - Limit to critical utility behaviors only
  - [ ] 2.2 Implement parse_frontmatter(file_path) -> dict
    - Use python-frontmatter library
    - Return empty dict for invalid YAML (tolerant parsing)
    - Log errors when DEBUG=True
    - Keep function under 30 lines
  - [ ] 2.3 Implement hash_value(value) -> str
    - Convert value to canonical JSON string (sorted keys)
    - Hash with SHA256
    - Handle None/null as empty string
    - Sort lists before hashing
    - Keep function under 30 lines
  - [ ] 2.4 Implement get_file_id(path) -> str
    - Normalize path to absolute
    - Return stable identifier (e.g., relative path from vault root)
    - Keep function under 30 lines
  - [ ] 2.5 Implement get_timestamp() -> str
    - Return ISO8601 formatted timestamp
    - Use datetime.now().isoformat()
    - Keep function under 30 lines
  - [ ] 2.6 Create executable __main__ demo for utils.py
    - Create temporary test markdown file with frontmatter
    - Demonstrate frontmatter parsing
    - Show hash consistency and difference detection
    - Show file_id generation
    - Show timestamp generation
    - Include junior-dev friendly narration
  - [ ] 2.7 Run utils module tests only
    - Execute ONLY the 2-6 tests written in 2.1
    - Verify all utility functions work correctly
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-6 tests written in 2.1 pass
- parse_frontmatter handles valid and invalid YAML gracefully
- hash_value produces consistent hashes for same inputs
- All functions under 30 lines
- __main__ demo runs successfully without requiring actual vault

---

### Persistence Layer

#### Task Group 3: CSV Storage Implementation
**Assigned implementer:** python-developer
**Dependencies:** Task Group 2

- [ ] 3.0 Complete CSV persistence layer
  - [ ] 3.1 Write 2-6 focused tests for csv_store module
    - Test init_csv_files creates files with correct headers
    - Test append_csv writes rows correctly
    - Test read_csv returns list of dicts
    - Test get_snapshot retrieves last snapshot for file
    - Test log_event appends to events.csv
    - Limit to critical CSV operations only
  - [ ] 3.2 Define CSV schemas as constants
    - SNAPSHOTS_SCHEMA: file_id, path, prop, value_hash, last_seen
    - EVENTS_SCHEMA: id, file_id, path, prop, old_value, new_value, detected_at
    - WORKFLOWS_SCHEMA: name, module, enabled, last_run_at
    - RUNS_SCHEMA: id, workflow_name, input_hash, started_at, finished_at, status, message
    - TICKETS_SCHEMA: id, note_path, external_id, status, created_at, updated_at
  - [ ] 3.3 Implement init_csv_files()
    - Create CSV files in CSV_DIR if they don't exist
    - Write headers for each CSV based on schemas
    - Create CSV_DIR directory if missing
    - Keep function under 30 lines
  - [ ] 3.4 Implement read_csv(filename) -> list[dict]
    - Read CSV file and return as list of dictionaries
    - Handle missing files gracefully (return empty list)
    - Use csv.DictReader
    - Keep function under 30 lines
  - [ ] 3.5 Implement append_csv(filename, row: dict)
    - Append row to CSV file
    - Use portalocker for file locking if available, fallback to basic append
    - Handle write errors gracefully
    - Keep function under 30 lines
  - [ ] 3.6 Implement get_snapshot(file_id) -> dict
    - Read snapshots.csv and find most recent entry for file_id
    - Return dict with {prop: value_hash} mappings
    - Return empty dict if file_id not found
    - Keep function under 30 lines
  - [ ] 3.7 Implement log_event(file_id, path, prop, old, new)
    - Generate unique event ID
    - Append to events.csv with timestamp
    - Keep function under 30 lines
  - [ ] 3.8 Implement log_run(workflow, input_hash, started, finished, status, msg)
    - Generate unique run ID
    - Append to runs.csv with all details
    - Keep function under 30 lines
  - [ ] 3.9 Implement update_snapshot(file_id, path, prop, value_hash)
    - Append new snapshot entry to snapshots.csv
    - Include current timestamp
    - Keep function under 30 lines
  - [ ] 3.10 Create executable __main__ demo for csv_store.py
    - Initialize CSV files in /tmp directory
    - Demonstrate writing snapshots, events, runs
    - Show reading data back
    - Include narration
  - [ ] 3.11 Run csv_store module tests only
    - Execute ONLY the 2-6 tests written in 3.1
    - Verify CSV operations work correctly
    - Verify files created with proper schemas
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-6 tests written in 3.1 pass
- All CSV schemas defined correctly per specification
- CSV files created with proper headers on init
- All functions under 30 lines
- File under 200 lines total
- __main__ demo successfully creates and manipulates CSV files

---

### Business Logic Layer

#### Task Group 4: Rule Definitions and Evaluation
**Assigned implementer:** python-developer
**Dependencies:** Task Group 2

- [ ] 4.0 Complete rules and behaviors system
  - [ ] 4.1 Write 2-6 focused tests for behaviors module
    - Test get_tracked_fields returns expected list
    - Test evaluate_rule correctly evaluates predicates
    - Test get_matching_rules finds rules for field changes
    - Test built-in rule predicates work correctly
    - Limit to critical rule evaluation behaviors
  - [ ] 4.2 Implement get_tracked_fields() -> list[str]
    - Import TRACKED_FIELDS from config
    - Return the list
    - Keep function under 30 lines
  - [ ] 4.3 Define built-in rules data structure
    - Create list of rule dictionaries with: name, field, predicate, workflow, description
    - Rule 1: agent_os_assignment (assignee: "" → "agent-os")
    - Rule 2: needs_review (status: * → "needs-review")
    - Rule 3: publish_ready (stage: * → "scheduled" + past publish_date check)
    - Rule 4: run_start (run: * → "start")
    - Rule 5: run_done (run: "start" → "done")
    - Follow spec section 3.2.5
  - [ ] 4.4 Implement get_rules() -> list[dict]
    - Return all rule definitions
    - Keep function under 30 lines
  - [ ] 4.5 Implement evaluate_rule(rule, old_value, new_value) -> bool
    - Execute rule's predicate lambda with old and new values
    - Catch and log exceptions, return False on error
    - Keep function under 30 lines
  - [ ] 4.6 Implement get_matching_rules(field, old, new) -> list[dict]
    - Filter rules by field
    - Evaluate each rule's predicate
    - Return list of matching rules
    - Keep function under 30 lines
  - [ ] 4.7 Create executable __main__ demo for behaviors.py
    - Show all tracked fields
    - Show all defined rules
    - Demonstrate rule evaluation with test cases
    - Test each built-in rule with example old/new values
    - Include narration
  - [ ] 4.8 Run behaviors module tests only
    - Execute ONLY the 2-6 tests written in 4.1
    - Verify rule evaluation logic works
    - Verify all 5 built-in rules defined correctly
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-6 tests written in 4.1 pass
- All 5 built-in rules defined per specification
- Rule evaluation works correctly with predicates
- All functions under 30 lines
- File under 200 lines
- __main__ demo demonstrates rule matching

---

### Workflow Layer

#### Task Group 5: Workflow Implementations
**Assigned implementer:** python-developer
**Dependencies:** Task Groups 3, 4

- [ ] 5.0 Complete workflow system
  - [ ] 5.1 Write 2-6 focused tests for workflows module
    - Test get_workflows returns workflow registry
    - Test workflow interface (returns success, message, data)
    - Test new_agent_os_ticket workflow logic
    - Test error handling returns proper error dict
    - Limit to critical workflow behaviors
  - [ ] 5.2 Define workflow interface and registry structure
    - Document workflow function signature: run(payload: dict, debug: bool) -> dict
    - Document expected payload structure per spec section 3.2.6
    - Document return structure: {success, message, data}
  - [ ] 5.3 Implement new_agent_os_ticket(payload, debug) -> dict
    - Extract title, summary, tags from frontmatter
    - Log ticket creation intent to tickets.csv
    - Return success with ticket details
    - Placeholder for actual Agent-OS API integration
    - Keep function under 30 lines
  - [ ] 5.4 Implement notify_review(payload, debug) -> dict
    - Placeholder workflow
    - Log review notification request
    - Return success with notification details
    - Keep function under 30 lines
  - [ ] 5.5 Implement publish_content(payload, debug) -> dict
    - Placeholder workflow
    - Log publish event
    - Return success with publish details
    - Keep function under 30 lines
  - [ ] 5.6 Implement log_run_start(payload, debug) -> dict
    - Create entry in runs.csv via csv_store
    - Initialize run timestamp
    - Return success with run ID
    - Keep function under 30 lines
  - [ ] 5.7 Implement log_run_end(payload, debug) -> dict
    - Update run entry with completion time
    - Compute duration
    - Return success
    - Keep function under 30 lines
  - [ ] 5.8 Implement get_workflows() -> dict[str, callable]
    - Return dictionary mapping workflow names to functions
    - Include all 5 workflows
    - Keep function under 30 lines
  - [ ] 5.9 Add comprehensive error handling to all workflows
    - Wrap workflow logic in try-except
    - Return {success: False, message: error} on exceptions
    - Log errors when debug=True
  - [ ] 5.10 Create executable __main__ demo for workflows.py
    - Show workflow registry
    - Test each workflow with sample payload
    - Demonstrate error handling
    - Show CSV output for ticket creation
    - Include narration
  - [ ] 5.11 Run workflows module tests only
    - Execute ONLY the 2-6 tests written in 5.1
    - Verify all 5 workflows defined and callable
    - Verify error handling works
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-6 tests written in 5.1 pass
- All 5 workflows implemented per specification
- All workflows follow interface contract
- Error handling never crashes, returns proper error dict
- All functions under 30 lines
- File under 200 lines
- __main__ demo runs all workflows successfully

---

### Service Orchestration Layer

#### Task Group 6: Main Service Loop and Integration
**Assigned implementer:** python-developer
**Dependencies:** Task Groups 1-5

- [ ] 6.0 Complete main service orchestration
  - [ ] 6.1 Write 2-6 focused tests for main module
    - Test process_file handles valid markdown file
    - Test process_file handles invalid file gracefully
    - Test poll_vault finds markdown files
    - Test was_already_processed idempotency check
    - Limit to critical orchestration behaviors
  - [ ] 6.2 Implement find_markdown_files(vault_path) -> list[str]
    - Recursively scan vault for .md files
    - Use pathlib.Path.rglob("*.md")
    - Return list of absolute paths
    - Keep function under 30 lines
  - [ ] 6.3 Implement was_already_processed(workflow_name, input_hash, window_hours=24) -> bool
    - Read runs.csv via csv_store
    - Check for recent run with same workflow and input hash
    - Use 24-hour window as specified in spec section 4.3
    - Keep function under 30 lines
  - [ ] 6.4 Implement process_file(file_path) -> None
    - Parse frontmatter via utils
    - Get file_id
    - Load snapshot via csv_store
    - Loop through TRACKED_FIELDS
    - Compute hashes, detect changes
    - Log events for changes
    - Evaluate rules and fire workflows
    - Update snapshots
    - Wrap in try-except, never crash
    - Keep function under 30 lines
  - [ ] 6.5 Implement poll_vault() -> None
    - Print heartbeat if DEBUG=True
    - Find all markdown files
    - Process each file via process_file
    - Handle errors gracefully
    - Keep function under 30 lines
  - [ ] 6.6 Implement handle_shutdown(signum, frame)
    - Print shutdown message
    - Perform cleanup if needed
    - Exit gracefully
    - Keep function under 30 lines
  - [ ] 6.7 Implement main() entry point
    - Load configuration
    - Initialize CSV files via csv_store.init_csv_files()
    - Register signal handlers (SIGINT, SIGTERM)
    - Run infinite polling loop with time.sleep(POLL_INTERVAL_SECONDS)
    - Keep function under 30 lines
  - [ ] 6.8 Create executable __main__ block for main.py
    - Call main() when run as script
    - Handle keyboard interrupt gracefully
  - [ ] 6.9 Add comprehensive error handling throughout main.py
    - File parsing errors: log and continue
    - CSV errors: log to stderr, continue
    - Workflow errors: already handled in workflows module
    - Follow spec section 4.5 error handling principles
  - [ ] 6.10 Run main module tests only
    - Execute ONLY the 2-6 tests written in 6.1
    - Verify file processing logic works
    - Verify idempotency check works
    - Do NOT run entire test suite

**Acceptance Criteria:**
- The 2-6 tests written in 6.1 pass
- Service starts and runs polling loop
- Heartbeat prints every POLL_INTERVAL_SECONDS when DEBUG=True
- File processing never crashes main loop
- Graceful shutdown on SIGINT/SIGTERM
- All functions under 30 lines
- File under 200 lines
- Idempotency prevents duplicate workflow executions

---

### Testing and Validation Layer

#### Task Group 7: Integration Testing and Acceptance Criteria Validation
**Assigned implementer:** testing-engineer
**Dependencies:** Task Groups 1-6

- [ ] 7.0 Complete integration testing and acceptance validation
  - [ ] 7.1 Review existing tests from Task Groups 1-6
    - Review 2-5 tests from config module (Task 1.3)
    - Review 2-6 tests from utils module (Task 2.1)
    - Review 2-6 tests from csv_store module (Task 3.1)
    - Review 2-6 tests from behaviors module (Task 4.1)
    - Review 2-6 tests from workflows module (Task 5.1)
    - Review 2-6 tests from main module (Task 6.1)
    - Total existing tests: approximately 12-35 tests
  - [ ] 7.2 Analyze test coverage gaps for this feature only
    - Identify critical end-to-end workflows not covered
    - Focus on integration between modules
    - Check polling loop → change detection → rule evaluation → workflow execution path
    - Do NOT assess entire application, only vault watcher feature
  - [ ] 7.3 Write up to 10 additional strategic integration tests maximum
    - Test complete flow: markdown change → event logged → workflow fires
    - Test idempotency: same change doesn't trigger workflow twice
    - Test graceful error handling: invalid YAML doesn't crash service
    - Test CSV file initialization and persistence
    - Test environment variable overrides work end-to-end
    - Focus on acceptance criteria validation
    - Do NOT write comprehensive coverage
  - [ ] 7.4 Create test vault with sample markdown files
    - Create /tmp/test_vault directory structure
    - Add sample notes with various frontmatter configurations
    - Include notes to test all 5 built-in rules
  - [ ] 7.5 Manually validate AC1: Poller Functionality
    - Set POLL_INTERVAL_SECONDS=10 and DEBUG=True
    - Run service and verify heartbeat every 10 seconds
    - Document verification steps and results
  - [ ] 7.6 Manually validate AC2: Single Source of Truth
    - Grep codebase for hardcoded paths
    - Verify all modules reference config.VAULT_PATH
    - Document verification results
  - [ ] 7.7 Manually validate AC3: Diff Detection
    - Create test note with assignee=""
    - Change assignee to "agent-os"
    - Check events.csv for proper entry
    - Document verification steps
  - [ ] 7.8 Manually validate AC4: Rule Firing
    - Trigger assignee change
    - Verify workflow runs exactly once
    - Check runs.csv for single entry
    - Document results
  - [ ] 7.9 Manually validate AC5: Workflow Execution
    - Test successful workflow execution
    - Test failed workflow execution
    - Verify tickets.csv and runs.csv entries
    - Document results
  - [ ] 7.10 Manually validate AC6: Debug Toggle
    - Test DEBUG=False (silent mode)
    - Test DEBUG=True (verbose mode)
    - Document output differences
  - [ ] 7.11 Manually validate AC7: Code Constraints
    - Check all functions ≤30 lines (excluding docstrings)
    - Check all files ≤200 lines (excluding docstrings)
    - Verify all 6 files have __main__ demos
    - Document measurements
  - [ ] 7.12 Manually validate AC8: Extensibility
    - Add test rule to behaviors.py
    - Add test workflow to workflows.py
    - Verify no main.py changes needed
    - Run service and verify new rule works
    - Document results
  - [ ] 7.13 Run all feature-specific tests
    - Run tests from modules (12-35 tests from tasks 1-6)
    - Run integration tests (up to 10 tests from 7.3)
    - Expected total: approximately 22-45 tests maximum
    - Do NOT run entire test suite if other tests exist
    - Document test results
  - [ ] 7.14 Create acceptance validation report
    - Document all 8 acceptance criteria results
    - Include evidence (CSV files, logs, code measurements)
    - List any deviations or issues
    - Provide recommendations if needed

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 22-45 tests total)
- All 8 acceptance criteria validated and documented
- No more than 10 additional tests added by testing-engineer
- Integration between all modules works correctly
- End-to-end workflows execute successfully
- Code constraints verified and met

---

## Execution Order

**Recommended implementation sequence:**

1. **Foundation** (Task Group 1): Project setup and configuration - 1-2 days
2. **Utilities** (Task Group 2): Core parsing and hashing functions - 1 day
3. **Persistence** (Task Group 3): CSV storage layer - 1-2 days
4. **Business Logic** (Task Group 4): Rules and evaluation - 1 day
5. **Workflows** (Task Group 5): Workflow implementations - 1-2 days
6. **Orchestration** (Task Group 6): Main service loop - 2 days
7. **Testing & Validation** (Task Group 7): Integration and acceptance testing - 1-2 days

**Total Estimated Time:** 8-11 days

---

## Key Success Factors

1. **Code Constraints Adherence**: Every function ≤30 lines, every file ≤200 lines
2. **Executable Demos**: Each module must have working `__main__` demo
3. **Single Source of Truth**: All configuration in config.py, no hardcoded values
4. **Error Resilience**: Main loop never crashes, graceful degradation everywhere
5. **CSV Auditability**: All changes tracked in CSV files
6. **Minimal Dependencies**: Only python-frontmatter required, portalocker optional
7. **Debug Visibility**: DEBUG flag controls all verbose output consistently
8. **Idempotency**: Workflows never execute twice for same change

---

## Testing Philosophy for This Project

Given the specification's emphasis on executable demos and manual testing:

- Each module's `__main__` demo serves as living documentation and smoke test
- Formal unit tests are minimal (2-6 per module) focusing on critical behaviors
- Integration testing validates end-to-end workflows
- Acceptance criteria provide manual verification steps
- Total test count kept reasonable (22-45 tests) per agent-os testing standards

This approach balances test coverage with development velocity while ensuring the service works correctly.

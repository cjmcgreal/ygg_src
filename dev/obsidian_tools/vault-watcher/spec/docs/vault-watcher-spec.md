# Obsidian Vault Watcher - Technical Specification

**Version:** 1.0
**Last Updated:** 2025-10-18
**Status:** Draft

---

## 1. Executive Summary

The Obsidian Vault Watcher is a lightweight Python service that bridges planning and execution by monitoring frontmatter property changes in Obsidian vaults and triggering configurable workflows. It provides a zero-dependency, file-based automation system with full auditability through CSV storage.

### Key Value Propositions

- **Planning ↔ Execution Bridge**: Converts note changes into executable jobs
- **Zero Vendor Lock-in**: Pure file/polling approach, no Obsidian API required
- **Governed Automation**: CSV-backed audit trail with explicit rules
- **Developer-First**: Strict code constraints (<30 lines/function, <200 lines/file)

---

## 2. Product Overview

### 2.1 Problem Statement

Users need a reliable, auditable way to automate workflows based on changes in their Obsidian notes. Existing solutions either:
- Require plugins that lock you into the Obsidian ecosystem
- Lack auditability and traceability
- Don't integrate well with agent-based execution systems like Agent-OS

### 2.2 Solution

A polling-based Python service that:
1. Monitors markdown files in an Obsidian vault
2. Detects frontmatter property changes
3. Evaluates rules against changes
4. Fires workflows when rules match
5. Logs everything to CSV for auditability

### 2.3 Target Users

**Primary Personas:**
- **Power Obsidian Users**: Want event-driven automation from note changes
- **Agent-OS/Claude Code Users**: Need ticket/queue bridge from markdown to agents
- **Solo Devs/Small Teams**: Prefer plain-text ops and CSVs over SaaS solutions

**User Scenarios:**
1. **Auto-ticketing**: `assignee: agent-os` → create Agent-OS ticket
2. **Review Gates**: `status: needs-review` → notify reviewers
3. **Content Pipeline**: `stage: scheduled` + past date → publish workflow
4. **Procedures Tracking**: `run: start/done` → log runs with timestamps

---

## 3. Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Poller Loop (every N seconds)                       │   │
│  │  1. Scan vault for .md files                         │   │
│  │  2. Parse frontmatter                                │   │
│  │  3. Compute diffs vs snapshots                       │   │
│  │  4. Evaluate rules                                   │   │
│  │  5. Fire workflows                                   │   │
│  │  6. Update snapshots & audit logs                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    config.py    behaviors.py   workflows.py   csv_store.py
    (settings)   (rules)        (actions)      (persistence)
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                        │
                        ▼
                   utils.py
              (parsing, hashing)
                        │
                        ▼
                   CSV Files
         ┌─────────────┴─────────────┐
         │  snapshots.csv            │
         │  events.csv               │
         │  workflows.csv            │
         │  runs.csv                 │
         │  tickets.csv              │
         └───────────────────────────┘
```

### 3.2 Module Responsibilities

#### 3.2.1 main.py
**Purpose:** Service orchestration and polling loop
**Responsibilities:**
- Load configuration
- Initialize CSV storage
- Run polling loop at configured interval
- Coordinate diff detection, rule evaluation, and workflow execution
- Handle graceful shutdown

**Key Functions:**
- `main()`: Entry point, initializes and starts service
- `poll_vault()`: Single poll iteration
- `process_file(path)`: Process one markdown file
- `handle_shutdown(signum, frame)`: Graceful shutdown handler

**Constraints:**
- Must be <200 lines
- All functions <30 lines
- No hardcoded paths or intervals

#### 3.2.2 config.py
**Purpose:** Single source of truth for all configuration
**Responsibilities:**
- Define vault path
- Set polling interval
- Configure debug mode
- Specify tracked frontmatter fields
- Define CSV storage paths

**Configuration Variables:**
```python
VAULT_PATH: str              # Absolute path to Obsidian vault
POLL_INTERVAL_SECONDS: int   # Polling frequency
DEBUG: bool                  # Global debug toggle
TRACKED_FIELDS: list[str]    # Frontmatter fields to monitor
CSV_DIR: str                 # Directory for CSV files
```

**Environment Overrides:**
- `VAULT_PATH` → `VAULT_WATCHER_VAULT_PATH`
- `DEBUG` → `VAULT_WATCHER_DEBUG`
- `POLL_INTERVAL_SECONDS` → `VAULT_WATCHER_INTERVAL`

#### 3.2.3 utils.py
**Purpose:** Shared utilities for parsing and hashing
**Responsibilities:**
- Parse YAML frontmatter from markdown files
- Hash property values for change detection
- Timestamp utilities
- File path normalization

**Key Functions:**
- `parse_frontmatter(file_path) -> dict`: Extract frontmatter as dict
- `hash_value(value) -> str`: Consistent hashing for change detection
- `get_file_id(path) -> str`: Generate stable file identifier
- `get_timestamp() -> str`: ISO8601 timestamp

**Error Handling:**
- Tolerant parsing: invalid YAML returns empty dict
- Logs errors when DEBUG=True
- Never crashes the main loop

#### 3.2.4 csv_store.py
**Purpose:** CSV persistence layer
**Responsibilities:**
- Initialize CSV files with headers
- Read/write rows with optional locking
- Query helpers for common operations
- Schema validation

**Key Functions:**
- `init_csv_files()`: Create CSV files with headers if missing
- `read_csv(filename) -> list[dict]`: Read CSV as list of dicts
- `append_csv(filename, row)`: Append row with optional file lock
- `get_snapshot(file_id) -> dict`: Get last snapshot for file
- `log_event(file_id, path, prop, old, new)`: Log property change
- `log_run(workflow, input_hash, status, message)`: Log workflow run

**CSV Schemas:**

**snapshots.csv:**
```
file_id, path, prop, value_hash, last_seen
```

**events.csv:**
```
id, file_id, path, prop, old_value, new_value, detected_at
```

**workflows.csv:**
```
name, module, enabled, last_run_at
```

**runs.csv:**
```
id, workflow_name, input_hash, started_at, finished_at, status, message
```

**tickets.csv:**
```
id, note_path, external_id, status, created_at, updated_at
```

**Locking Strategy:**
- Use `portalocker` for file locks if available
- Fallback to basic append (safe for single writer)
- Lock acquisition timeout: 5 seconds

#### 3.2.5 behaviors.py
**Purpose:** Rule definitions and evaluation
**Responsibilities:**
- Define which frontmatter fields trigger rules
- Implement rule predicates
- Maintain rule registry
- Evaluate rules against property changes

**Key Concepts:**

**Rule Structure:**
```python
{
    "name": "agent_os_assignment",
    "field": "assignee",
    "predicate": lambda old, new: old == "" and new == "agent-os",
    "workflow": "new_agent_os_ticket",
    "description": "Create Agent-OS ticket when assignee set to agent-os"
}
```

**Key Functions:**
- `get_tracked_fields() -> list[str]`: Return fields to monitor
- `get_rules() -> list[dict]`: Return all rule definitions
- `evaluate_rule(rule, old_value, new_value) -> bool`: Test rule predicate
- `get_matching_rules(field, old, new) -> list[dict]`: Find rules that match change

**Built-in Rules:**
1. **agent_os_assignment**: `assignee: "" → "agent-os"`
2. **needs_review**: `status: * → "needs-review"`
3. **publish_ready**: `stage: * → "scheduled"` + past publish_date
4. **run_start**: `run: * → "start"`
5. **run_done**: `run: "start" → "done"`

**Extensibility:**
- Add new rules by appending to rules list
- No changes to main.py required
- Rules are evaluated in order

#### 3.2.6 workflows.py
**Purpose:** Workflow implementations
**Responsibilities:**
- Define workflow interface
- Implement workflow actions
- Handle workflow errors
- Log workflow outcomes

**Workflow Interface:**
```python
def run(payload: dict, debug: bool = False) -> dict:
    """
    Execute workflow.

    Args:
        payload: {
            "note_path": str,
            "field": str,
            "old_value": any,
            "new_value": any,
            "frontmatter": dict
        }
        debug: Enable verbose logging

    Returns:
        {
            "success": bool,
            "message": str,
            "data": dict  # workflow-specific output
        }
    """
```

**Key Functions:**
- `get_workflows() -> dict[str, callable]`: Return workflow registry
- `new_agent_os_ticket(payload, debug)`: Create Agent-OS ticket
- `notify_review(payload, debug)`: Send review notification
- `publish_content(payload, debug)`: Publish workflow
- `log_run_start(payload, debug)`: Initialize run tracking
- `log_run_end(payload, debug)`: Finalize run tracking

**Built-in Workflows:**

1. **new_agent_os_ticket**
   - Extract title, summary, tags from note
   - Call Agent-OS API/CLI to create ticket
   - Write ticket ID to tickets.csv
   - Optionally update note frontmatter with ticket_id
   - Return ticket details

2. **notify_review** (placeholder)
   - Log review request
   - Return notification details

3. **publish_content** (placeholder)
   - Log publish event
   - Return publish details

4. **log_run_start**
   - Create entry in runs.csv
   - Initialize run timestamp

5. **log_run_end**
   - Update run entry with completion time
   - Compute duration

**Error Handling:**
- Catch all exceptions within workflow
- Return `success=False` with error message
- Log to runs.csv with `status='error'`
- Never crash main loop

---

## 4. Detailed Design

### 4.1 Polling Loop Algorithm

```python
while True:
    if DEBUG:
        print(f"[{timestamp}] Poll heartbeat")

    # 1. Scan vault for .md files
    markdown_files = find_markdown_files(VAULT_PATH)

    for file_path in markdown_files:
        # 2. Parse frontmatter
        frontmatter = parse_frontmatter(file_path)
        file_id = get_file_id(file_path)

        # 3. Load previous snapshot
        snapshot = get_snapshot(file_id)

        # 4. Compute diffs for tracked fields
        for field in TRACKED_FIELDS:
            old_value = snapshot.get(field, "")
            new_value = frontmatter.get(field, "")
            old_hash = hash_value(old_value)
            new_hash = hash_value(new_value)

            if old_hash != new_hash:
                # 5. Log event
                log_event(file_id, file_path, field, old_value, new_value)

                # 6. Evaluate rules
                matching_rules = get_matching_rules(field, old_value, new_value)

                for rule in matching_rules:
                    # 7. Fire workflow
                    workflow_name = rule["workflow"]
                    workflow = get_workflow(workflow_name)

                    payload = {
                        "note_path": file_path,
                        "field": field,
                        "old_value": old_value,
                        "new_value": new_value,
                        "frontmatter": frontmatter
                    }

                    input_hash = hash_value(json.dumps(payload, sort_keys=True))

                    # Check for duplicate (idempotency)
                    if not was_already_processed(workflow_name, input_hash):
                        started_at = get_timestamp()
                        result = workflow(payload, debug=DEBUG)
                        finished_at = get_timestamp()

                        log_run(
                            workflow_name,
                            input_hash,
                            started_at,
                            finished_at,
                            "success" if result["success"] else "error",
                            result["message"]
                        )

                # 8. Update snapshot
                update_snapshot(file_id, file_path, field, new_hash)

    # Sleep until next poll
    time.sleep(POLL_INTERVAL_SECONDS)
```

### 4.2 Change Detection Strategy

**Hashing Approach:**
- Convert value to canonical JSON string
- Hash with SHA256
- Store hash (not raw value) in snapshots.csv
- Compare hashes to detect changes

**Benefits:**
- Handles complex values (lists, dicts)
- Privacy-friendly (doesn't store raw values in snapshot)
- Consistent across runs

**Edge Cases:**
- Missing field: treat as empty string
- Null/None: normalize to empty string
- Lists: sort before hashing
- Dicts: sort keys before hashing

### 4.3 Idempotency Strategy

**Problem:** Same change could trigger workflow multiple times if:
- Multiple polls before snapshot update
- Service restart during workflow execution

**Solution:**
1. Hash workflow input payload (note_path, field, old, new)
2. Before running workflow, check runs.csv for recent run with same hash
3. Skip if duplicate found within last 24 hours
4. Log attempted duplicate for debugging

**Implementation:**
```python
def was_already_processed(workflow_name, input_hash, window_hours=24):
    """Check if workflow already ran for this input recently."""
    cutoff = datetime.now() - timedelta(hours=window_hours)
    recent_runs = read_csv("runs.csv")

    for run in recent_runs:
        if (run["workflow_name"] == workflow_name and
            run["input_hash"] == input_hash and
            datetime.fromisoformat(run["started_at"]) > cutoff):
            return True

    return False
```

### 4.4 Debug Mode Implementation

**Global Toggle:**
```python
# config.py
DEBUG = os.getenv("VAULT_WATCHER_DEBUG", "false").lower() == "true"
```

**Propagation:**
- Import DEBUG in all modules: `from config import DEBUG`
- Pass `debug=DEBUG` to workflow calls
- Wrap debug prints: `if DEBUG: print(...)`

**Debug Output Guidelines:**
- Main loop: heartbeat every poll
- File processing: file path being processed
- Change detection: old/new values
- Rule evaluation: rule name, match result
- Workflow execution: start/end timestamps, result
- CSV operations: file writes

### 4.5 Error Handling

**Principles:**
1. **Never crash the main loop**: All file/workflow operations in try-except
2. **Log all errors**: Write to stderr and runs.csv
3. **Continue on failure**: Skip problematic file, continue to next
4. **Graceful degradation**: Missing CSV columns → add defaults

**Error Categories:**

**File Parsing Errors:**
```python
try:
    frontmatter = parse_frontmatter(file_path)
except Exception as e:
    if DEBUG:
        print(f"Error parsing {file_path}: {e}")
    continue  # Skip file
```

**CSV Errors:**
```python
try:
    append_csv("events.csv", row)
except Exception as e:
    print(f"ERROR: Failed to write event: {e}", file=sys.stderr)
    # Continue - don't crash on CSV failure
```

**Workflow Errors:**
```python
try:
    result = workflow(payload, debug=DEBUG)
except Exception as e:
    result = {
        "success": False,
        "message": f"Workflow exception: {str(e)}"
    }
```

---

## 5. Implementation Requirements

### 5.1 Code Quality Constraints

**Hard Limits:**
- Functions: ≤30 lines (excluding docstrings)
- Files: ≤200 lines (excluding docstrings)
- Line length: ≤100 characters
- Cyclomatic complexity: ≤10 per function

**Style Requirements:**
- Type hints on all function signatures
- Docstrings (Google style) for all public functions
- Clear variable names (no single letters except loop indices)
- Comments for non-obvious logic

**Testing Requirements:**
- Each file has `if __name__ == "__main__":` demo
- Demo includes narration for junior developers
- Demo can run standalone without vault
- Demo shows key behaviors

### 5.2 Manual Test Examples

**utils.py:**
```python
if __name__ == "__main__":
    print("=== utils.py Manual Test ===")
    print("This demonstrates frontmatter parsing and hashing.\n")

    # Create test markdown
    test_md = """---
title: Test Note
assignee: agent-os
tags: [work, urgent]
---
# Note content
"""
    test_file = "/tmp/test_note.md"
    with open(test_file, "w") as f:
        f.write(test_md)

    print("1. Parsing frontmatter...")
    fm = parse_frontmatter(test_file)
    print(f"   Result: {fm}")

    print("\n2. Hashing values...")
    h1 = hash_value("agent-os")
    h2 = hash_value("agent-os")
    h3 = hash_value("different")
    print(f"   Same values match: {h1 == h2}")
    print(f"   Different values differ: {h1 != h3}")

    print("\n✓ Demo complete")
```

### 5.3 Dependencies

**Required:**
```
python >= 3.11
python-frontmatter >= 1.0.0
```

**Optional:**
```
portalocker >= 2.8.0  # For CSV file locking
pandas >= 2.0.0       # For ad-hoc analysis (not runtime)
```

**Standard Library:**
```
pathlib, hashlib, csv, json, time, datetime, os, sys, signal
```

### 5.4 Configuration

**config.py defaults:**
```python
import os
from pathlib import Path

# Vault location
VAULT_PATH = os.getenv(
    "VAULT_WATCHER_VAULT_PATH",
    str(Path.home() / "Documents" / "ObsidianVault")
)

# Polling interval (seconds)
POLL_INTERVAL_SECONDS = int(os.getenv("VAULT_WATCHER_INTERVAL", "20"))

# Debug mode
DEBUG = os.getenv("VAULT_WATCHER_DEBUG", "false").lower() == "true"

# Tracked frontmatter fields
TRACKED_FIELDS = [
    "assignee",
    "status",
    "stage",
    "run",
    "publish_date"
]

# CSV storage directory
CSV_DIR = os.getenv(
    "VAULT_WATCHER_CSV_DIR",
    str(Path.home() / ".vault_watcher" / "data")
)
```

### 5.5 Project Structure

```
vault_watcher/
├── README.md
├── requirements.txt
├── main.py                 # Service loop & orchestration
├── config.py               # Configuration & constants
├── utils.py                # Parsing & hashing utilities
├── csv_store.py            # CSV persistence layer
├── behaviors.py            # Rule definitions & evaluation
├── workflows.py            # Workflow implementations
└── data/                   # CSV storage (created at runtime)
    ├── snapshots.csv
    ├── events.csv
    ├── workflows.csv
    ├── runs.csv
    └── tickets.csv
```

---

## 6. Acceptance Criteria

### AC1: Poller Functionality
**Given** the service is configured with `POLL_INTERVAL_SECONDS=10` and `DEBUG=True`
**When** the service starts
**Then** a heartbeat log appears every 10 seconds

**Verification:**
```bash
VAULT_WATCHER_DEBUG=true python main.py
# Should print: [timestamp] Poll heartbeat every 10s
```

### AC2: Single Source of Truth
**Given** vault path is changed in config.py
**When** the service runs
**Then** all modules use the new path without code changes

**Verification:**
- Grep codebase for hardcoded paths
- All paths should reference `config.VAULT_PATH`

### AC3: Diff Detection
**Given** a note with `assignee: ""` exists
**When** the assignee changes to `agent-os`
**Then** an entry appears in `events.csv` with old="" and new="agent-os"

**Verification:**
```bash
# Before change
tail -1 data/events.csv

# After change
tail -1 data/events.csv
# Should show: id,file_id,path,assignee,"","agent-os",timestamp
```

### AC4: Rule Firing
**Given** rule "assignee: '' → 'agent-os'" → workflow "new_agent_os_ticket"
**When** assignee changes from "" to "agent-os"
**Then** the workflow runs exactly once per change

**Verification:**
```bash
# Check runs.csv for single entry
grep "new_agent_os_ticket" data/runs.csv | wc -l
# Should be: 1
```

### AC5: Workflow Execution
**Given** the `new_agent_os_ticket` workflow is triggered
**When** execution succeeds
**Then**
- A row appears in `tickets.csv` with ticket details
- A row appears in `runs.csv` with `status='success'`

**When** execution fails
**Then**
- A row appears in `runs.csv` with `status='error'` and error message

**Verification:**
```bash
tail -1 data/tickets.csv  # Should have ticket entry
tail -1 data/runs.csv     # Should have success/error status
```

### AC6: Debug Toggle
**Given** `DEBUG=False` in config
**When** the service runs
**Then** no debug prints appear

**Given** `DEBUG=True` in config
**When** the service runs
**Then** all modules emit progress prints

**Verification:**
```bash
# Silent mode
DEBUG=false python main.py 2>&1 | wc -l
# Should be: 0 (or minimal)

# Verbose mode
DEBUG=true python main.py 2>&1 | head -10
# Should show: heartbeats, file processing, rule evaluation
```

### AC7: Code Constraints
**Given** all source files
**When** analyzed for length
**Then**
- No function exceeds 30 lines (excluding docstrings)
- No file exceeds 200 lines (excluding docstrings)
- Each file has executable `if __name__ == "__main__":` demo

**Verification:**
```bash
# Check function lengths
for f in *.py; do
    python -c "import ast; print(f'$f:', max(len([n for n in ast.walk(ast.parse(open('$f').read())) if isinstance(n, ast.FunctionDef)])))"
done

# Check file lengths
for f in *.py; do
    wc -l $f
done

# Check for demos
grep -l "if __name__ ==" *.py | wc -l
# Should be: 6 (all files)
```

### AC8: Extensibility
**Given** a new rule is needed
**When** the rule is added to `behaviors.py`
**Then** no changes to `main.py` are required

**Given** a new workflow is needed
**When** the workflow is added to `workflows.py`
**Then** no changes to `main.py` are required

**Verification:**
- Add rule to behaviors.py
- Add workflow to workflows.py
- Run service
- Verify rule fires and workflow executes
- Confirm main.py unchanged (git diff)

---

## 7. Security & Privacy

### 7.1 Data Handling

**Sensitive Data:**
- Snapshots store hashes, not raw values
- Events store raw old/new values (could contain sensitive info)
- Tickets store note paths and metadata

**Recommendations:**
- Store CSV files in user home directory with restricted permissions (chmod 600)
- Add CSV directory to .gitignore
- Consider encrypting events.csv if notes contain secrets

### 7.2 File System Security

**Access Control:**
- Service runs with user's file permissions
- No privilege escalation required
- Vault must be readable by service user

**Path Validation:**
- Normalize all paths to absolute
- Prevent directory traversal attacks
- Validate vault path exists and is readable

### 7.3 Workflow Security

**Sandboxing:**
- Workflows run in same process as service
- No shell command injection (use subprocess.run with list args)
- Validate all workflow inputs

**Agent-OS Integration:**
- Store API keys in environment variables, not code
- Use read-only credentials where possible
- Log all external API calls

---

## 8. Performance & Scalability

### 8.1 Performance Targets

**Metrics:**
- **MTTD** (Mean Time To Detect change): ≤ `POLL_INTERVAL_SECONDS`
- **Files per poll**: 1000 files in <5 seconds
- **Memory usage**: <100MB for 1000 files
- **CPU usage**: <5% average (excluding workflow execution)

### 8.2 Optimization Strategies

**Scan Optimization:**
- Cache file modification times
- Skip files unchanged since last scan
- Scan only tracked directories (configurable)

**Memory Optimization:**
- Stream CSV reads for large files
- Don't load entire vault into memory
- LRU cache for recently processed files

**Disk I/O Optimization:**
- Batch CSV writes
- Use append mode (no re-read)
- Optional: SQLite instead of CSV for large deployments

### 8.3 Scalability Limits

**Single Vault:**
- Tested up to 10,000 markdown files
- Recommended max: 5,000 files
- Beyond that: consider selective directory scanning

**Multiple Vaults:**
- Run separate service instance per vault
- Share CSV directory with vault-specific prefixes
- Coordinate with process manager (systemd, supervisor)

**Concurrent Workflows:**
- Current design: sequential execution
- Future: async workflow execution with semaphore

---

## 9. Testing Strategy

### 9.1 Manual Testing

**Each Module:**
- Runnable `__main__` demo
- Junior-dev friendly narration
- No external dependencies for demo

**Integration Testing:**
- Create test vault with sample notes
- Define test rules and workflows
- Run service and verify CSV outputs
- Test all acceptance criteria manually

### 9.2 Future Automated Testing

**Unit Tests:**
- utils.py: parsing, hashing
- csv_store.py: read/write operations
- behaviors.py: rule evaluation
- workflows.py: workflow logic

**Integration Tests:**
- End-to-end: change note → workflow executes
- Idempotency: same change doesn't re-trigger
- Error handling: invalid YAML, missing fields

**Load Tests:**
- 1000 files with 100 changes
- Concurrent CSV writes
- Memory profiling

---

## 10. Deployment

### 10.1 Installation

```bash
# Clone repo
git clone https://github.com/yourorg/vault-watcher.git
cd vault-watcher

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure
export VAULT_WATCHER_VAULT_PATH="/path/to/vault"
export VAULT_WATCHER_INTERVAL="20"
export VAULT_WATCHER_DEBUG="false"

# Run
python main.py
```

### 10.2 Process Management

**systemd (Linux):**
```ini
[Unit]
Description=Obsidian Vault Watcher
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/vault-watcher
Environment="VAULT_WATCHER_VAULT_PATH=/home/youruser/ObsidianVault"
Environment="VAULT_WATCHER_DEBUG=false"
ExecStart=/home/youruser/vault-watcher/venv/bin/python main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .

ENV VAULT_WATCHER_VAULT_PATH=/vault
ENV VAULT_WATCHER_CSV_DIR=/data

VOLUME ["/vault", "/data"]

CMD ["python", "main.py"]
```

### 10.3 Monitoring

**Health Checks:**
- Check if process is running
- Verify CSV files are being updated
- Monitor log for errors

**Metrics to Track:**
- Poll cycle duration
- Events detected per hour
- Workflows executed per hour
- Workflow success rate
- CSV file sizes

**Alerting:**
- Service down
- No polls in last 5 minutes
- Workflow failure rate >10%
- CSV directory disk usage >90%

---

## 11. Future Enhancements

### Phase 2 Features

1. **Real-time Mode**
   - Use `watchdog` for file system events
   - Instant triggering vs polling
   - Configurable: poll vs watch mode

2. **Web Dashboard**
   - View recent events
   - Workflow status
   - Manual workflow triggers
   - Rule management UI

3. **Workflow Marketplace**
   - Community-contributed workflows
   - Easy import/export
   - Workflow templates

4. **Advanced Rules**
   - Multi-field conditions
   - Time-based rules (business hours only)
   - Rate limiting
   - Workflow chaining

5. **SQLite Backend**
   - Optional replacement for CSVs
   - Better querying
   - Concurrent access
   - Full-text search

6. **Bidirectional Sync**
   - Update note frontmatter from workflow results
   - Safe concurrent editing
   - Conflict resolution

### Non-Goals (Out of Scope)

- Real-time collaboration
- Cloud hosting
- Mobile app
- WYSIWYG note editing
- Built-in AI/LLM features
- Multi-user auth/permissions

---

## 12. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Race conditions on CSV files | Medium | Low | Add file locking with `portalocker` |
| Large vaults cause slow scans | High | Medium | Implement file mtime caching, selective scanning |
| Invalid YAML crashes loop | High | Low | Tolerant parsing with try-except |
| Workflow hangs indefinitely | Medium | Low | Add timeout to workflow execution |
| Duplicate workflow triggers | Low | Medium | Implement idempotency hashing |
| CSV corruption from crash | Medium | Low | Write to temp file, then atomic rename |
| Memory leak on long runs | Medium | Low | Clear caches periodically, profile with tracemalloc |

---

## 13. Glossary

- **Frontmatter**: YAML metadata block at top of markdown file, delimited by `---`
- **Vault**: Obsidian workspace directory containing markdown files
- **Snapshot**: Stored state of a file's frontmatter properties (hashed)
- **Event**: Detected change in a frontmatter property
- **Rule**: Condition that triggers a workflow when matched
- **Workflow**: Executable action triggered by a rule
- **Polling**: Periodic scanning of vault for changes
- **Idempotency**: Ensuring same input doesn't trigger workflow multiple times

---

## 14. References

- **Obsidian**: https://obsidian.md
- **Agent-OS**: (your Agent-OS docs)
- **python-frontmatter**: https://pypi.org/project/python-frontmatter/
- **portalocker**: https://pypi.org/project/portalocker/
- **YAML Spec**: https://yaml.org/spec/1.2/spec.html

---

## Appendix A: Example Notes

### Example 1: Agent-OS Ticket Creation

**Before:**
```markdown
---
title: Fix authentication bug
assignee: ""
status: todo
tags: [bug, auth]
---

# Description
Users can't log in with SSO.
```

**After:**
```markdown
---
title: Fix authentication bug
assignee: agent-os
status: in-progress
tags: [bug, auth]
ticket_id: AGNT-123
---

# Description
Users can't log in with SSO.
```

**Events triggered:**
1. `assignee: "" → "agent-os"` → runs `new_agent_os_ticket` workflow
2. Workflow creates Agent-OS ticket AGNT-123
3. Workflow writes to tickets.csv
4. (Optional) Workflow updates note with `ticket_id`

### Example 2: Content Publishing

**Before:**
```markdown
---
title: My Blog Post
stage: draft
publish_date: 2025-10-15
---

# Content here
```

**After:**
```markdown
---
title: My Blog Post
stage: scheduled
publish_date: 2025-10-15
published_url: https://blog.example.com/my-post
---

# Content here
```

**Events triggered:**
1. `stage: "draft" → "scheduled"` + past date → runs `publish_content` workflow
2. Workflow renders markdown, commits to repo, deploys
3. Workflow updates note with `published_url`

---

## Appendix B: Workflow Development Guide

### Creating a New Workflow

1. **Define the workflow function in workflows.py:**

```python
def my_custom_workflow(payload: dict, debug: bool = False) -> dict:
    """
    Description of what this workflow does.

    Args:
        payload: Contains note_path, field, old_value, new_value, frontmatter
        debug: Enable verbose logging

    Returns:
        {"success": bool, "message": str, "data": dict}
    """
    try:
        note_path = payload["note_path"]
        frontmatter = payload["frontmatter"]

        if debug:
            print(f"[my_custom_workflow] Processing {note_path}")

        # Your workflow logic here
        result = do_something(frontmatter)

        return {
            "success": True,
            "message": "Workflow completed successfully",
            "data": {"result": result}
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "data": {}
        }
```

2. **Register workflow in the registry:**

```python
def get_workflows() -> dict[str, callable]:
    """Return all available workflows."""
    return {
        "new_agent_os_ticket": new_agent_os_ticket,
        "my_custom_workflow": my_custom_workflow,  # Add here
        # ... other workflows
    }
```

3. **Create a rule in behaviors.py:**

```python
{
    "name": "my_custom_rule",
    "field": "my_field",
    "predicate": lambda old, new: new == "trigger_value",
    "workflow": "my_custom_workflow",
    "description": "Runs my custom workflow when my_field changes"
}
```

4. **Test your workflow:**

```python
if __name__ == "__main__":
    # Add demo in workflows.py
    print("=== my_custom_workflow Demo ===")
    test_payload = {
        "note_path": "/tmp/test.md",
        "field": "my_field",
        "old_value": "",
        "new_value": "trigger_value",
        "frontmatter": {"title": "Test Note"}
    }
    result = my_custom_workflow(test_payload, debug=True)
    print(f"Result: {result}")
```

---

**End of Specification**

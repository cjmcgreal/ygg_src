# Exercise Tracker Architecture

## Overview

The Exercise Tracker follows a **layered architecture** with strict separation of concerns. The primary design goal is **framework independence** - all business logic is completely decoupled from the Streamlit UI framework, enabling easy migration to other frameworks or platforms in the future.

## Architectural Principles

### 1. Framework Independence

**Critical Requirement**: All business logic MUST be completely independent of the Streamlit framework.

**Why this matters**:
- The entire frontend could be replaced with Flask, FastAPI, Django, or a native mobile app without modifying business logic
- Business logic can be tested in isolation without UI dependencies
- Makes the codebase more maintainable and adaptable to changing requirements
- Enables reuse of business logic across multiple interfaces

**How we achieve it**:
- Business logic modules (db.py, logic.py, analysis.py, workflow.py) contain ZERO Streamlit imports
- All functions accept and return standard Python types (dicts, lists, primitives)
- UI layer (pages/*.py) is the only place Streamlit is used
- UI layer calls workflow functions and displays results

### 2. Separation of Concerns

Each layer has a single, well-defined responsibility:

- **Data Storage Layer**: Persistent storage (CSV files)
- **Data Access Layer**: CRUD operations and queries
- **Business Logic Layer**: Domain logic (progression algorithms, calculations)
- **Workflow Layer**: Orchestration of multi-step operations
- **Presentation Layer**: User interface and interaction

### 3. Clear Layer Boundaries

Communication between layers follows strict rules:

- Each layer only communicates with adjacent layers
- Data flows through function calls, not global state
- No layer skipping (e.g., UI cannot directly call db.py, must go through workflow.py)

## Layer Architecture

```
┌─────────────────────────────────────┐
│  Presentation Layer (Streamlit)     │
│  - pages/*.py files                 │
│  - UI rendering                     │
│  - Session state management         │
│  - User input handling              │
└─────────────────────────────────────┘
              ↓ ↑ (function calls only)
┌─────────────────────────────────────┐
│  Workflow Layer (workflow.py)       │
│  - Aggregates frontend actions      │
│  - Orchestrates business operations │
│  - No Streamlit dependencies        │
└─────────────────────────────────────┘
              ↓ ↑ (function calls only)
┌─────────────────────────────────────┐
│  Business Logic Layer               │
│  - logic.py (progression engine)    │
│  - analysis.py (calculations)       │
│  - No Streamlit dependencies        │
└─────────────────────────────────────┘
              ↓ ↑ (data operations)
┌─────────────────────────────────────┐
│  Data Access Layer (db.py)          │
│  - CSV operations                   │
│  - CRUD functions                   │
│  - Schema management                │
└─────────────────────────────────────┘
              ↓ ↑
┌─────────────────────────────────────┐
│  Data Storage (CSV files)           │
└─────────────────────────────────────┘
```

## Module Responsibilities

### Data Storage Layer

**Files**: CSV files in `data/` directory

**Responsibilities**:
- Persistent storage of all application data
- Four tables: exercises, workouts, workout_logs, set_logs

**Format**:
- CSV files with pandas-compatible schemas
- Datetime fields stored as ISO format strings
- JSON fields stored as escaped JSON strings

### Data Access Layer (db.py)

**Responsibilities**:
- All CSV file operations and data persistence
- CRUD operations for all entities
- Schema definitions for all tables
- Query functions for complex data retrieval
- ID generation (auto-increment pattern)

**Key Functions**:
- `get_schema(table_name)` - Returns column list for table
- `load_table(table_name)` - Loads CSV with datetime conversion
- `save_table(table_name, df)` - Saves CSV with directory creation
- `create_exercise()`, `get_exercise_by_id()`, etc. - CRUD operations
- `get_exercise_history()`, `query_workout_logs()` - Complex queries

**Design Pattern**: Based on procedures-app reference implementation
- Returns DataFrames for list queries
- Returns dicts for single-entity queries
- Auto-creates missing directories
- Handles empty files gracefully

**No Dependencies**: Pure data operations, no business logic

### Business Logic Layer

#### logic.py (Progression Engine)

**Responsibilities**:
- Workout planning and progression logic
- Implements two progression schemes (rep range and linear weight)
- Warmup set generation based on intensity
- Success determination logic

**Core Function**:
```python
def calculate_next_workout_sets(exercise_id: int, workout_log_id: Optional[int] = None) -> List[Dict[str, Any]]
```

This function:
1. Loads exercise configuration
2. Queries exercise history
3. Determines next weight and reps based on progression scheme
4. Generates warmup sets if configured
5. Generates working sets
6. Returns complete set list

**Progression Algorithms**:

**Rep Range Progression**:
- Progress by adding 1 rep per successful workout
- When max reps reached, add weight and reset to min reps
- On failure, repeat same weight and reps

**Linear Weight Progression**:
- Keep reps constant
- Add weight increment each successful workout
- On failure, repeat same weight

**Success Criteria**:
All working sets completed with target reps or more

**No Dependencies**: No Streamlit, pure business logic

#### analysis.py (Calculations)

**Responsibilities**:
- Mathematical operations and metadata calculations
- 1RM estimation (Epley formula)
- Weight estimation for target reps
- Metadata calculation at three levels

**Core Functions**:
- `estimate_one_rep_max(weight, reps)` - Epley formula: 1RM = weight × (1 + reps/30)
- `get_latest_one_rep_max(exercise_id)` - Query most recent 1RM estimate
- `estimate_weight_for_reps(one_rm, target_reps)` - Inverse Epley formula
- `calculate_set_metadata()` - Per-set calculations (volume, calories, 1RM)
- `calculate_exercise_metadata()` - Per-exercise aggregation
- `calculate_workout_metadata()` - Per-workout aggregation

**Three-Level Metadata**:

1. **Set Level**: volume, calories, 1RM estimate (working sets only)
2. **Exercise Level**: total_duration, total_volume, total_calories, set counts
3. **Workout Level**: duration_seconds, total_volume, total_calories, total_sets, muscle_groups_trained

**No Dependencies**: Pure calculations, no Streamlit

### Workflow Layer (workflow.py)

**Responsibilities**:
- Orchestrate multi-step business operations
- Aggregate frontend actions into complete workflows
- Coordinate between business logic and data access layers
- Validation of user inputs

**Key Workflows**:

**handle_create_exercise(exercise_data)**:
- Validates exercise data
- Calls db.create_exercise()
- Returns exercise_id

**handle_create_workout(name, exercise_ids, notes)**:
- Validates workout data
- Verifies exercise_ids exist
- Calls db.create_workout()
- Returns workout_id

**handle_start_workout(workout_id)**:
- Loads workout template
- Creates workout_log entry
- Generates sets for each exercise via logic.calculate_next_workout_sets()
- Returns complete workout plan with history

**handle_complete_workout(workout_log_id, set_data)**:
- Calculates set metadata for each set
- Saves all set_logs
- Calculates workout metadata
- Updates workout_log with metadata and status
- Returns workout summary

**No Dependencies**: No Streamlit, but calls logic, analysis, and db modules

### Presentation Layer (pages/*.py)

**Responsibilities**:
- User interface rendering
- User input handling
- Session state management
- Navigation between pages
- Calling workflow functions

**Key Pages**:

**1_exercise_library.py**:
- Exercise creation form
- Exercise library table view
- Search and filter UI
- Calls: workflow.handle_create_exercise()

**2_create_workout.py**:
- Workout creation form
- Exercise selection UI
- Calls: workflow.handle_create_workout()

**3_workout_overview.py**:
- Workout list display
- Workout selection
- Navigation to execution
- Calls: db.get_all_workouts(), db.get_workout_by_id()

**4_workout_execution.py**:
- Workout execution interface
- Set tracking and completion
- Progress display
- Calls: workflow.handle_start_workout(), workflow.handle_complete_workout()

**5_history.py**:
- Workout log display
- Filtering and search
- Historical data views
- Calls: workflow.get_workout_history()

**Session State Usage**:
- `workout_id` - Selected workout for execution
- `workout_log_id` - Current workout session ID
- `workout_plan` - Generated sets for current workout
- `set_completion` - Dict tracking completed sets
- `start_time` - Workout start timestamp

**Streamlit Dependencies**: This is the ONLY layer that imports Streamlit

## Data Flow Examples

### Complete Workout Flow

```
User clicks "Start Workout" on workout_overview.py
  ↓
Store workout_id in session_state
  ↓
Navigate to workout_execution.py
  ↓
workflow.handle_start_workout(workout_id)
  ↓
  db.get_workout_by_id(workout_id)
  db.create_workout_log(workout_id, start_time, status)
  For each exercise:
    logic.calculate_next_workout_sets(exercise_id)
      ↓
      db.get_exercise_by_id(exercise_id)
      db.get_exercise_history(exercise_id)
      analysis.get_latest_one_rep_max(exercise_id)
      Apply progression algorithm
      logic.generate_warmup_sets() if configured
      Return set list
    db.get_last_exercise_performance(exercise_id)
  Return workout plan
  ↓
Display sets with checkboxes and inputs
  ↓
User completes sets, clicks "Complete Workout"
  ↓
workflow.handle_complete_workout(workout_log_id, set_data)
  ↓
  For each completed set:
    analysis.calculate_set_metadata()
    db.create_set_log()
  db.get_set_logs_for_workout(workout_log_id)
  analysis.calculate_workout_metadata()
  db.update_workout_log()
  Return workout summary
  ↓
Display success message and summary
```

### Progression Logic Flow

```
User starts workout with Barbell Squat exercise
  ↓
logic.calculate_next_workout_sets(exercise_id=1)
  ↓
1. Load exercise config from db:
   - progression_scheme: "rep_range"
   - rep_range_min: 8, rep_range_max: 12
   - weight_increment: 5.0
   - warmup_config: {...}
  ↓
2. Query exercise history:
   - db.get_exercise_history(1)
   - Find last workout: 135 lbs × 11 reps (all 3 sets completed)
   - Success: True
  ↓
3. Get current 1RM:
   - analysis.get_latest_one_rep_max(1)
   - Returns: 176 lbs
  ↓
4. Apply rep range progression:
   - Last: 11 reps (successful)
   - Next: 12 reps (11 + 1, not yet at max)
   - Weight: 135 lbs (same)
  ↓
5. Generate warmup sets:
   - Working weight: 135 lbs
   - Intensity: 135/176 = 76% of 1RM
   - Threshold matched: 70-100% → 3 warmup sets
   - Sets:
     - 54 lbs × 8 reps (40% of 135)
     - 81 lbs × 6 reps (60% of 135)
     - 108 lbs × 4 reps (80% of 135)
  ↓
6. Generate working sets:
   - 3 sets of 135 lbs × 12 reps
   - Rest: 120 seconds
  ↓
7. Return combined list:
   - 3 warmup sets + 3 working sets
```

## Progression Algorithms in Detail

### Rep Range Progression Algorithm

**Purpose**: Gradually increase reps within a range, then increase weight

**Input**:
- exercise: Exercise configuration
- history: Exercise performance history

**Logic**:
```python
if no history:
    next_weight = default_starting_weight (45 lbs)
    next_reps = rep_range_min
    return (next_weight, next_reps)

last_workout = get_most_recent_completed_workout(history)
last_weight = last_workout.weight
last_reps = last_workout.reps
all_completed = all_working_sets_completed(last_workout)

if all_completed:
    # Successful workout
    if last_reps < rep_range_max:
        # Still room to add reps
        next_reps = last_reps + 1
        next_weight = last_weight
    else:
        # Hit top of rep range, add weight and reset
        next_reps = rep_range_min
        next_weight = last_weight + weight_increment
else:
    # Failed workout, repeat
    next_reps = last_reps
    next_weight = last_weight

return (next_weight, next_reps)
```

**Example Progression**:
- W1: 135×8 (success) → W2: 135×9
- W2: 135×9 (success) → W3: 135×10
- W3: 135×10 (success) → W4: 135×11
- W4: 135×11 (failure) → W5: 135×11 (retry)
- W5: 135×11 (success) → W6: 135×12
- W6: 135×12 (success, max) → W7: 140×8 (weight up, reps reset)

### Linear Weight Progression Algorithm

**Purpose**: Add weight each successful workout, keep reps constant

**Input**:
- exercise: Exercise configuration
- history: Exercise performance history

**Logic**:
```python
next_reps = target_reps  # Always constant

if no history:
    next_weight = default_starting_weight (45 lbs)
    return (next_weight, next_reps)

last_workout = get_most_recent_completed_workout(history)
last_weight = last_workout.weight
all_completed = all_working_sets_completed(last_workout)

if all_completed:
    # Successful workout, add weight
    next_weight = last_weight + weight_increment
else:
    # Failed workout, repeat weight
    next_weight = last_weight

return (next_weight, next_reps)
```

**Example Progression**:
- W1: 225×5 (success) → W2: 230×5
- W2: 230×5 (success) → W3: 235×5
- W3: 235×5 (success) → W4: 240×5
- W4: 240×5 (failure) → W5: 240×5 (retry)
- W5: 240×5 (success) → W6: 245×5

### Warmup Set Generation Algorithm

**Purpose**: Generate appropriate warmup sets based on working set intensity

**Input**:
- warmup_config: JSON configuration from exercise
- working_weight: Weight for working sets
- one_rep_max: Estimated 1RM

**Logic**:
```python
if not warmup_config.enabled:
    return []

# Calculate intensity of working set
percent_1rm = (working_weight / one_rep_max) * 100

# Determine number of warmup sets needed
for threshold in warmup_config.intensity_thresholds:
    if threshold.min_percent_1rm <= percent_1rm < threshold.max_percent_1rm:
        warmup_count = threshold.warmup_sets
        break

# Generate warmup sets
warmup_sets = []
for i in range(warmup_count):
    percent = warmup_config.warmup_percentages[i]
    reps = warmup_config.warmup_reps[i]

    warmup_weight = working_weight * (percent / 100)
    # Round to nearest 5 for practicality
    warmup_weight = round(warmup_weight / 5) * 5

    warmup_sets.append({
        "weight": warmup_weight,
        "reps": reps,
        "rest": 60
    })

return warmup_sets
```

**Example**:
- Working: 225 lbs
- 1RM: 285 lbs
- Intensity: 79% of 1RM
- Threshold: 70-100% → 3 warmup sets
- Sets:
  - 90 lbs (40%) × 8 reps
  - 135 lbs (60%) × 6 reps
  - 180 lbs (80%) × 4 reps

## Metadata Calculation Levels

### Level 1: Per-Set Metadata

Calculated when a set is completed.

**Inputs**:
- actual_weight: Weight used
- actual_reps: Reps completed
- duration_seconds: Time to complete set
- set_type: "warmup" or "working"

**Calculations**:
- Volume = weight × reps
- Calories = MET (5.0) × body_weight_kg × (duration_seconds / 3600)
- 1RM estimate (working sets only) = weight × (1 + reps/30)

**Output**: Dict with volume, calories, one_rep_max_estimate

### Level 2: Per-Exercise Metadata

Calculated by aggregating all sets for an exercise.

**Inputs**: List of set log dicts for one exercise

**Calculations**:
- total_duration = sum of all set durations
- total_volume = sum of all set volumes
- total_calories = sum of all set calories
- set_count = count of all completed sets
- working_set_count = count of completed working sets
- warmup_set_count = count of completed warmup sets

**Output**: Dict with aggregated values

### Level 3: Per-Workout Metadata

Calculated by aggregating all sets across all exercises.

**Inputs**:
- start_time: Workout start timestamp
- end_time: Workout end timestamp
- all_set_logs: All set logs for workout
- exercise_ids: List of exercise IDs in workout

**Calculations**:
- duration_seconds = end_time - start_time
- total_volume = sum of all set volumes
- total_calories = sum of all set calories
- total_sets = count of all completed sets
- muscle_groups_trained = unique muscle groups from all exercises (comma-separated, sorted)

**Output**: Dict with workout-level aggregations

## Design Decisions and Rationale

### Why CSV Instead of Database?

**Pros**:
- Simple setup (no database installation)
- Human-readable data
- Easy backup (copy files)
- Sufficient for single-user, local installation
- Pandas provides powerful data manipulation

**Cons**:
- No transactional support
- No referential integrity enforcement
- Performance degrades with large datasets
- No concurrent access support

**Future**: Migrate to SQLite or PostgreSQL for better performance and features

### Why Framework Independence?

**Rationale**:
- UI frameworks change frequently
- Business logic is stable and valuable
- Enables testing without UI
- Enables multiple interfaces (web, mobile, CLI)
- Makes codebase more maintainable

**Cost**: Extra layer (workflow.py) adds indirection

**Benefit**: Can replace Streamlit with Flask, FastAPI, or native app without changing business logic

### Why Three-Level Metadata?

**Rationale**:
- Flexibility for future analytics without recomputation
- Enables queries at different granularities
- Pre-calculated for performance
- Supports different use cases (set analysis, exercise trends, workout summaries)

**Cost**: More storage space, more calculation time

**Benefit**: Fast queries, flexible analytics, detailed history

## Testing Strategy

### Unit Tests

Focus on pure functions in analysis.py and logic.py:
- 1RM calculation correctness
- Weight estimation accuracy
- Progression algorithm logic
- Warmup generation correctness

### Integration Tests

Test workflow.py functions that coordinate multiple modules:
- Complete workout flow (create → execute → complete)
- Multi-workout progression over time
- Failure handling
- Metadata calculation at all levels

### Manual UI Tests

Primary validation for Streamlit pages:
- Form submission and validation
- Navigation between pages
- Session state persistence
- Data display accuracy

## Reference Documentation

**Full specification**: `/home/conrad/git/yggdrasill/domains/software/external_libraries/agent-os/agent-os-sandbox/agent-os/specs/2025-11-01-exercise-app-user-flow/planning/specification.md`

**Reference implementations**:
- Database patterns: procedures-app/src/database.py
- Exercise planning: yggdrasil exercise_planner.py

## Future Architecture Enhancements

### Database Migration

Replace CSV storage with SQLite:
- Better performance for queries
- Transactional support
- Referential integrity
- No code changes to business logic (only db.py)

### API Layer

Add RESTful API between workflow and presentation layers:
- Enable multiple frontend clients
- Better separation for mobile apps
- Enable cloud sync features

### Caching

Add caching layer for frequently accessed data:
- Exercise library
- Workout templates
- Recent 1RM estimates
- Reduce CSV read operations

## Conclusion

The layered architecture with framework independence provides a solid foundation for future growth while keeping the MVP simple. The clear separation of concerns makes the codebase maintainable and testable, while the workflow layer provides a clean interface for any UI framework.

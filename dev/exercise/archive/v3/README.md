# Exercise Tracker

A personal workout tracking and progression system designed to intelligently manage exercise routines, automate progressive overload, and maintain comprehensive workout history.

## Features

- **Intelligent Progression**: Automatically calculates next workout parameters based on performance history
- **Flexible Schemes**: Supports two distinct progression methodologies (rep range and linear weight)
- **1RM-Based Planning**: Uses one-rep max estimation to determine appropriate training loads
- **Warmup Set Generation**: Automatically generates warmup sets based on working set intensity
- **Comprehensive Tracking**: Records all workout data with three-level metadata aggregation
- **Framework Independence**: Clean separation between business logic and UI layer

## Tech Stack

- **Framework**: Streamlit (tab-based navigation)
- **Data Storage**: CSV files with pandas
- **Language**: Python 3.8+
- **Architecture**: Clear separation between UI and business logic for easy framework migration

## Navigation

The app uses **tab-based navigation** (not sidebar pages) making it easy to embed into larger applications. All functionality is accessible through tabs within a single page.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or download this repository** to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd exercise/v3
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to the URL shown in the terminal (usually http://localhost:8501)

## Using as an Embedded Module

The Exercise Tracker can be easily embedded into other Streamlit applications:

### Basic Integration

```python
import streamlit as st
from exercise.v3.src.exercise_app import render_exercise_app

st.set_page_config(page_title="My Fitness App", layout="wide")

# Your other app content here
st.title("My Fitness Application")
st.write("Welcome to my comprehensive fitness tracker!")

# Render the exercise app
render_exercise_app()
```

### Integration with Tabs

```python
import streamlit as st
from exercise.v3.src.exercise_app import render_exercise_app

st.set_page_config(page_title="Multi-App Dashboard", layout="wide")

tab1, tab2, tab3 = st.tabs(["Dashboard", "Exercise Tracker", "Nutrition"])

with tab1:
    st.header("Dashboard")
    # Your dashboard content

with tab2:
    render_exercise_app()

with tab3:
    st.header("Nutrition Tracking")
    # Your nutrition tracking content
```

### Key Features for Embedding

- **No sidebar navigation**: Uses tabs instead, making it clean for embedding
- **Portable function**: Single `render_exercise_app()` function does everything
- **Self-contained**: All data stored in local CSV files
- **No configuration needed**: Works out of the box

## Project Structure

```
exercise/v3/
├── data/                           # CSV data files (created automatically)
│   ├── exercises.csv              # Exercise library
│   ├── workouts.csv               # Workout templates
│   ├── workout_logs.csv           # Completed workout sessions
│   └── set_logs.csv               # Individual set records
├── src/                            # Source code modules
│   └── exercise_app.py            # Main app module with all render functions
├── pages/                          # Legacy page files (can be removed)
│   ├── 1_exercise_library.py      # Exercise management (legacy)
│   ├── 2_create_workout.py        # Workout template creation (legacy)
│   ├── 3_workout_overview.py      # Workout selection (legacy)
│   ├── 4_workout_execution.py     # Active workout tracking (legacy)
│   ├── 5_history.py               # Historical data and analytics (legacy)
│   └── 6_log_old_workout.py       # Manual workout entry (legacy)
├── tests/                          # Unit and integration tests
├── .streamlit/                     # Streamlit configuration
│   └── config.toml                # Theme and server settings
├── app.py                          # Main entry point
├── db.py                           # Data access layer (CSV operations)
├── logic.py                        # Progression engine
├── analysis.py                     # Calculations and metadata
├── workflow.py                     # Workflow orchestration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Usage Guide

### Getting Started

#### 1. Create Your First Exercise

Navigate to **Exercise Library** tab:

1. Enter exercise name (e.g., "Barbell Squat")
2. Add description (optional)
3. Select primary muscle groups (required)
4. Select secondary muscle groups (optional)
5. Choose progression scheme:
   - **Rep Range**: Progress by adding reps (e.g., 8-12 reps), then increase weight
   - **Linear Weight**: Keep reps constant (e.g., 5 reps), increase weight each session
6. Set rep range or target reps based on chosen scheme
7. Set weight increment (e.g., 5 lbs)
8. Enable warmup sets if desired (recommended for compound movements)
9. Click "Create Exercise"

**Example Exercise Configurations:**
- **Barbell Squat**: Rep range 8-12, increment 5 lbs, warmups enabled
- **Bench Press**: Linear weight with 5 reps, increment 5 lbs, warmups enabled
- **Bicep Curls**: Rep range 10-15, increment 2.5 lbs, warmups disabled

#### 2. Create a Workout Template

Navigate to **Create Workout** tab:

1. Enter workout name (e.g., "Push Day A")
2. Select exercises from your library (multiselect)
3. Exercises will be performed in the order selected
4. Add notes (optional)
5. Click "Create Workout"

The workout template is saved and ready to use. The specific weights and reps for each exercise will be determined automatically when you execute the workout.

#### 3. Execute a Workout

Navigate to **Workout Overview** tab:

1. Browse your workout templates
2. Click "Start Workout" on the workout you want to perform
3. The app automatically generates:
   - Warmup sets (if configured) based on working weight intensity
   - Working sets with appropriate weight and rep targets based on progression logic

**During Workout Execution:**
- Check off each set as you complete it
- View "Last Time" data to see your previous performance
- Optionally override target weight/reps if needed (e.g., couldn't complete all reps)
- Add notes to individual sets if desired
- Rest times are displayed between sets

**Complete Workout:**
- Click "Complete Workout" when all working sets are done (warmups optional)
- Metadata is automatically calculated: volume, calories, duration, 1RM estimates
- All data is saved to CSV files

#### 4. View History

Navigate to **History** tab:

- Browse all completed workouts
- Filter by date range, workout type, or exercise
- Expand workout details to see set-by-set breakdown
- View summary statistics:
  - Total workouts completed
  - Total volume lifted
  - Total calories burned
  - Current week summary

## Understanding Progression Logic

### Rep Range Progression

Used for hypertrophy training where you want to work within a target rep range.

**How it works:**
1. Start at minimum reps (e.g., 8 reps with 135 lbs)
2. Each successful workout, add 1 rep (9 reps, then 10, 11, 12...)
3. When you hit maximum reps (e.g., 12), increase weight by increment and reset to minimum reps (140 lbs × 8 reps)
4. Repeat the cycle

**Success criteria**: All working sets completed with target reps or more

**Example progression:**
- Workout 1: 135 lbs × 8 reps (3 sets) → Success
- Workout 2: 135 lbs × 9 reps (3 sets) → Success
- Workout 3: 135 lbs × 10 reps (3 sets) → Success
- Workout 4: 135 lbs × 11 reps (2 complete, 1 failed) → Failure
- Workout 5: 135 lbs × 11 reps (3 sets) → Success (retry)
- Workout 6: 135 lbs × 12 reps (3 sets) → Success (hit max)
- Workout 7: 140 lbs × 8 reps (3 sets) → Success (weight increased)

### Linear Weight Progression

Used for strength training with a fixed rep count.

**How it works:**
1. Perform fixed number of reps (e.g., 5 reps)
2. Each successful workout, increase weight by increment (e.g., +5 lbs)
3. If you fail to complete all sets, repeat the same weight next time
4. Continue adding weight each successful session

**Success criteria**: All working sets completed with target reps or more

**Example progression:**
- Workout 1: 225 lbs × 5 reps (3 sets) → Success
- Workout 2: 230 lbs × 5 reps (3 sets) → Success
- Workout 3: 235 lbs × 5 reps (3 sets) → Success
- Workout 4: 240 lbs × 5 reps (2 complete, 1 failed) → Failure
- Workout 5: 240 lbs × 5 reps (3 sets) → Success (retry)
- Workout 6: 245 lbs × 5 reps (3 sets) → Success

### Understanding Warmup Sets

Warmup sets are automatically generated based on your working set intensity relative to your estimated 1RM.

**Intensity-Based Warmup Generation:**
- **0-50% of 1RM**: 1 warmup set
- **50-70% of 1RM**: 2 warmup sets
- **70-100% of 1RM**: 3 warmup sets

**Default warmup configuration:**
- Warmup 1: 40% of working weight × 8 reps
- Warmup 2: 60% of working weight × 6 reps
- Warmup 3: 80% of working weight × 4 reps

**Example:**
If your working set is 225 lbs (79% of your 285 lbs 1RM):
- 3 warmup sets will be generated:
  - 90 lbs × 8 reps (40%)
  - 135 lbs × 6 reps (60%)
  - 180 lbs × 4 reps (80%)

**Benefits:**
- Prepares muscles and nervous system for heavy loads
- Reduces injury risk
- Improves movement quality and technique
- Scales automatically with strength progression

## One-Rep Max (1RM) Estimation

The app uses the Epley formula to estimate your one-rep max:

**Formula**: 1RM = weight × (1 + reps/30)

**Example**: 225 lbs × 8 reps = 225 × (1 + 8/30) = 285 lbs

**Usage:**
- Calculated automatically after each completed working set
- Used to determine warmup set requirements
- Provides insight into strength progression over time
- Most accurate for 3-10 rep range

## Data Storage

All data is stored in CSV files in the `data/` directory:

- **exercises.csv**: Exercise library with configurations
- **workouts.csv**: Workout templates
- **workout_logs.csv**: Completed workout sessions with metadata
- **set_logs.csv**: Individual set records with calculations

**Backup your data:**
Simply copy the entire `data/` directory to a safe location.

**Reset data:**
Delete all CSV files in the `data/` directory to start fresh.

## Architecture

The application follows a layered architecture with strict separation of concerns:

**Layers (bottom to top):**
1. **Data Storage**: CSV files
2. **Data Access Layer** (db.py): CRUD operations
3. **Business Logic Layer** (logic.py, analysis.py): Progression algorithms and calculations
4. **Workflow Layer** (workflow.py): Orchestration of multi-step operations
5. **Presentation Layer** (pages/*.py): Streamlit UI

**Key Principle**: All business logic is framework-independent. The entire frontend could be replaced with Flask, FastAPI, Django, or a native app without modifying business logic.

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Known Issues

See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for current limitations and bugs.

## Quick Start

See [QUICKSTART.md](library/software/external_libraries/agent-os/agent-os-sandbox/exercise_module/QUICKSTART.md) for a one-page quick start guide.

## Development

### Running Tests

```bash
pytest -v
```

### Project Standards

- **Framework Independence**: Business logic modules (db.py, logic.py, analysis.py, workflow.py) must be completely independent of Streamlit
- **Type Hints**: All functions use type hints for better IDE support
- **Docstrings**: All functions have docstrings with Args, Returns, and Raises sections
- **DRY Principle**: Common patterns are extracted and reused

## Future Enhancements

High-priority enhancements after MVP:
1. Exercise edit/delete functionality
2. Workout template edit/delete functionality
3. Rest timer with countdown
4. Plate calculator for barbell loading
5. Volume and 1RM progression charts
6. Personal records tracking
7. Database migration from CSV to SQLite

## License

This is a personal project for single-user, local installation.

## Support

For issues, questions, or suggestions, please refer to the documentation files or create an issue in the project repository.

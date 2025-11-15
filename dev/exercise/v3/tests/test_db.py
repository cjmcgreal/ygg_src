"""
Focused tests for database layer
Testing critical behaviors only: schemas, load/save, ID generation, datetime conversion, and basic CRUD
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import shutil

# Add parent directory to path to import db module
sys.path.insert(0, str(Path(__file__).parent.parent))

import db


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests"""
    original_data_dir = db.DATA_DIR
    db.DATA_DIR = tmp_path / "data"
    db.DATA_DIR.mkdir(parents=True, exist_ok=True)
    yield db.DATA_DIR
    db.DATA_DIR = original_data_dir


def test_get_schema_returns_correct_columns():
    """Test that schema definitions return correct column lists"""
    exercises_schema = db.get_schema("exercises")
    assert len(exercises_schema) == 12
    assert "id" in exercises_schema
    assert "name" in exercises_schema
    assert "progression_scheme" in exercises_schema
    assert "warmup_config" in exercises_schema

    workouts_schema = db.get_schema("workouts")
    assert len(workouts_schema) == 5
    assert "id" in workouts_schema
    assert "exercise_ids" in workouts_schema

    workout_logs_schema = db.get_schema("workout_logs")
    assert len(workout_logs_schema) == 11

    set_logs_schema = db.get_schema("set_logs")
    assert len(set_logs_schema) == 17


def test_load_table_with_empty_file_returns_empty_dataframe(temp_data_dir):
    """Test that loading non-existent file returns empty DataFrame with correct schema"""
    df = db.load_table("exercises")
    assert df.empty
    assert list(df.columns) == db.get_schema("exercises")


def test_save_table_creates_directory_if_not_exists(tmp_path):
    """Test that save_table creates directory structure"""
    db.DATA_DIR = tmp_path / "new_data"
    assert not db.DATA_DIR.exists()

    df = pd.DataFrame([{"id": 1, "name": "test"}])
    db.save_table("test", df)

    assert db.DATA_DIR.exists()
    assert (db.DATA_DIR / "test.csv").exists()


def test_id_generation_first_is_1_then_increments(temp_data_dir):
    """Test ID generation pattern: first=1, then max+1"""
    # First exercise should get ID 1
    ex1_id = db.create_exercise(name="Exercise 1", progression_scheme="rep_range")
    assert ex1_id == 1

    # Second exercise should get ID 2
    ex2_id = db.create_exercise(name="Exercise 2", progression_scheme="linear_weight")
    assert ex2_id == 2

    # Third exercise should get ID 3
    ex3_id = db.create_exercise(name="Exercise 3", progression_scheme="rep_range")
    assert ex3_id == 3


def test_datetime_conversion_on_load(temp_data_dir):
    """Test that datetime columns are converted correctly when loading"""
    # Create an exercise (has created_at datetime)
    ex_id = db.create_exercise(name="Test Exercise", progression_scheme="rep_range")

    # Load and verify datetime conversion
    df = db.load_table("exercises")
    assert pd.api.types.is_datetime64_any_dtype(df['created_at'])


def test_create_and_get_exercise(temp_data_dir):
    """Test creating and retrieving an exercise"""
    ex_id = db.create_exercise(
        name="Barbell Squat",
        description="Classic leg exercise",
        primary_muscle_groups="quadriceps,glutes",
        secondary_muscle_groups="hamstrings",
        progression_scheme="rep_range",
        rep_range_min=8,
        rep_range_max=12,
        weight_increment=5.0
    )

    exercise = db.get_exercise_by_id(ex_id)
    assert exercise is not None
    assert exercise['name'] == "Barbell Squat"
    assert exercise['progression_scheme'] == "rep_range"
    assert exercise['rep_range_min'] == 8
    assert exercise['rep_range_max'] == 12


def test_create_and_get_workout(temp_data_dir):
    """Test creating and retrieving a workout"""
    # Create exercises first
    ex1_id = db.create_exercise(name="Exercise 1", progression_scheme="rep_range")
    ex2_id = db.create_exercise(name="Exercise 2", progression_scheme="linear_weight")

    # Create workout
    workout_id = db.create_workout(
        name="Push Day",
        exercise_ids=[ex1_id, ex2_id],
        notes="Focus on form"
    )

    # Retrieve and verify
    workout = db.get_workout_by_id(workout_id)
    assert workout is not None
    assert workout['name'] == "Push Day"
    assert workout['exercise_ids'] == [ex1_id, ex2_id]
    assert workout['notes'] == "Focus on form"


def test_create_workout_log_and_update(temp_data_dir):
    """Test creating and updating a workout log"""
    # Create exercise and workout first
    ex_id = db.create_exercise(name="Test Exercise", progression_scheme="rep_range")
    workout_id = db.create_workout(name="Test Workout", exercise_ids=[ex_id])

    # Create workout log
    start_time = datetime.now()
    log_id = db.create_workout_log(workout_id=workout_id, start_time=start_time)

    # Update workout log
    end_time = datetime.now()
    success = db.update_workout_log(
        workout_log_id=log_id,
        end_time=end_time,
        duration_seconds=3600,
        total_volume=1500.0,
        total_calories=250.0,
        total_sets=9,
        muscle_groups_trained="quadriceps,glutes",
        status="completed"
    )

    assert success is True

    # Verify update
    log = db.get_workout_log_by_id(log_id)
    assert log['status'] == "completed"
    assert log['total_volume'] == 1500.0
    assert log['total_sets'] == 9

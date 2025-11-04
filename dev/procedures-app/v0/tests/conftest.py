"""
Pytest configuration and shared fixtures
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src import database


@pytest.fixture
def temp_data_dir(monkeypatch):
    """
    Create a temporary data directory for testing
    Automatically cleans up after test
    """
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    # Monkey patch the DATA_DIR in database module
    monkeypatch.setattr(database, 'DATA_DIR', temp_path)

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_procedure(temp_data_dir):
    """Create a sample procedure for testing"""
    proc_id = database.create_procedure(
        name="Test Procedure",
        description="A test procedure for unit tests"
    )

    # Add steps
    steps = [
        "Step 1: First step",
        "Step 2: Second step",
        "Step 3: Third step"
    ]
    database.update_steps_for_procedure(proc_id, steps)

    return proc_id


@pytest.fixture
def sample_procedure_with_run(temp_data_dir, sample_procedure):
    """Create a sample procedure with a completed run"""
    # Create a run
    run_id = database.create_run(sample_procedure)

    # Get steps and initialize run steps
    steps = database.get_steps_for_procedure(sample_procedure)

    for step in steps:
        database.create_run_step(run_id, step['id'])

    # Get run steps and mark them complete
    run_steps = database.get_run_steps(run_id)

    for run_step in run_steps:
        database.update_run_step(run_step['id'], completed=True)

    # Complete the run
    database.update_run(run_id, status="completed", end_now=True)

    return {
        'procedure_id': sample_procedure,
        'run_id': run_id
    }


@pytest.fixture
def multiple_procedures(temp_data_dir):
    """Create multiple procedures for testing"""
    procedures = []

    for i in range(3):
        proc_id = database.create_procedure(
            name=f"Procedure {i+1}",
            description=f"Description for procedure {i+1}"
        )

        steps = [f"Step {j+1}" for j in range(3 + i)]
        database.update_steps_for_procedure(proc_id, steps)

        procedures.append(proc_id)

    return procedures


@pytest.fixture
def procedure_with_multiple_runs(temp_data_dir, sample_procedure):
    """Create a procedure with multiple runs"""
    runs = []

    for i in range(5):
        run_id = database.create_run(sample_procedure)

        # Initialize run steps
        steps = database.get_steps_for_procedure(sample_procedure)
        for step in steps:
            database.create_run_step(run_id, step['id'])

        # Complete 4 out of 5 runs
        if i < 4:
            run_steps = database.get_run_steps(run_id)

            for run_step in run_steps:
                database.update_run_step(run_step['id'], completed=True)

            database.update_run(run_id, status="completed", end_now=True)
        else:
            # Leave one run cancelled
            database.update_run(run_id, status="cancelled", end_now=True)

        runs.append(run_id)

    return {
        'procedure_id': sample_procedure,
        'run_ids': runs
    }

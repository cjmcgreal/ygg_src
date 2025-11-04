"""
Unit tests for database module
"""

import pytest
from src import database


class TestProcedures:
    def test_create_procedure(self, temp_data_dir):
        """Test creating a procedure"""
        proc_id = database.create_procedure("Test Procedure", "Test description")

        assert proc_id == 1

        # Verify it was created
        proc = database.get_procedure_by_id(proc_id)
        assert proc is not None
        assert proc['name'] == "Test Procedure"
        assert proc['description'] == "Test description"
        assert proc['version'] == 1

    def test_get_procedure_by_id_not_found(self, temp_data_dir):
        """Test getting non-existent procedure"""
        proc = database.get_procedure_by_id(999)
        assert proc is None

    def test_get_all_procedures(self, temp_data_dir):
        """Test getting all procedures"""
        database.create_procedure("Proc 1", "Desc 1")
        database.create_procedure("Proc 2", "Desc 2")

        all_procs = database.get_all_procedures()
        assert len(all_procs) == 2

    def test_update_procedure(self, temp_data_dir, sample_procedure):
        """Test updating a procedure"""
        success = database.update_procedure(
            sample_procedure,
            name="Updated Name",
            description="Updated Description"
        )

        assert success is True

        proc = database.get_procedure_by_id(sample_procedure)
        assert proc['name'] == "Updated Name"
        assert proc['description'] == "Updated Description"
        assert proc['version'] == 2  # Version incremented

    def test_update_procedure_not_found(self, temp_data_dir):
        """Test updating non-existent procedure"""
        success = database.update_procedure(999, name="Test")
        assert success is False

    def test_delete_procedure(self, temp_data_dir, sample_procedure):
        """Test deleting a procedure"""
        success = database.delete_procedure(sample_procedure)
        assert success is True

        # Verify deletion
        proc = database.get_procedure_by_id(sample_procedure)
        assert proc is None

        # Verify steps were deleted
        steps = database.get_steps_for_procedure(sample_procedure)
        assert len(steps) == 0


class TestSteps:
    def test_create_step(self, temp_data_dir, sample_procedure):
        """Test creating a step"""
        step_id = database.create_step(
            sample_procedure,
            order=1,
            description="Test Step"
        )

        assert step_id is not None

    def test_get_steps_for_procedure(self, temp_data_dir, sample_procedure):
        """Test getting steps for a procedure"""
        steps = database.get_steps_for_procedure(sample_procedure)

        assert len(steps) == 3
        assert steps[0]['description'] == "Step 1: First step"
        assert steps[1]['description'] == "Step 2: Second step"
        assert steps[2]['description'] == "Step 3: Third step"

    def test_get_steps_ordered(self, temp_data_dir, sample_procedure):
        """Test steps are returned in correct order"""
        steps = database.get_steps_for_procedure(sample_procedure)

        for i, step in enumerate(steps):
            assert step['order'] == i + 1

    def test_update_steps_for_procedure(self, temp_data_dir, sample_procedure):
        """Test replacing all steps for a procedure"""
        new_steps = ["New Step 1", "New Step 2"]
        database.update_steps_for_procedure(sample_procedure, new_steps)

        steps = database.get_steps_for_procedure(sample_procedure)
        assert len(steps) == 2
        assert steps[0]['description'] == "New Step 1"
        assert steps[1]['description'] == "New Step 2"


class TestRuns:
    def test_create_run(self, temp_data_dir, sample_procedure):
        """Test creating a run"""
        run_id = database.create_run(sample_procedure)

        assert run_id == 1

        run = database.get_run_by_id(run_id)
        assert run is not None
        assert run['procedure_id'] == sample_procedure
        assert run['status'] == 'in_progress'

    def test_get_run_by_id_not_found(self, temp_data_dir):
        """Test getting non-existent run"""
        run = database.get_run_by_id(999)
        assert run is None

    def test_get_all_runs(self, temp_data_dir, sample_procedure):
        """Test getting all runs"""
        database.create_run(sample_procedure)
        database.create_run(sample_procedure)

        all_runs = database.get_all_runs()
        assert len(all_runs) == 2

    def test_update_run_status(self, temp_data_dir, sample_procedure):
        """Test updating run status"""
        run_id = database.create_run(sample_procedure)

        success = database.update_run(run_id, status="completed", end_now=True)
        assert success is True

        run = database.get_run_by_id(run_id)
        assert run['status'] == "completed"
        assert run['end_time'] is not None

    def test_update_run_notes(self, temp_data_dir, sample_procedure):
        """Test updating run notes"""
        run_id = database.create_run(sample_procedure)

        success = database.update_run(run_id, notes="Test notes")
        assert success is True

        run = database.get_run_by_id(run_id)
        assert run['notes'] == "Test notes"


class TestRunSteps:
    def test_create_run_step(self, temp_data_dir, sample_procedure):
        """Test creating a run step"""
        run_id = database.create_run(sample_procedure)
        steps = database.get_steps_for_procedure(sample_procedure)

        run_step_id = database.create_run_step(run_id, steps[0]['id'])

        assert run_step_id is not None

    def test_get_run_steps(self, temp_data_dir, sample_procedure):
        """Test getting run steps"""
        run_id = database.create_run(sample_procedure)
        steps = database.get_steps_for_procedure(sample_procedure)

        # Create run steps
        for step in steps:
            database.create_run_step(run_id, step['id'])

        run_steps = database.get_run_steps(run_id)
        assert len(run_steps) == 3

    def test_update_run_step(self, temp_data_dir, sample_procedure):
        """Test updating a run step"""
        run_id = database.create_run(sample_procedure)
        steps = database.get_steps_for_procedure(sample_procedure)

        run_step_id = database.create_run_step(run_id, steps[0]['id'])

        success = database.update_run_step(
            run_step_id,
            completed=True,
            notes="Step completed"
        )

        assert success is True

        run_steps = database.get_run_steps(run_id)
        run_step = next(rs for rs in run_steps if rs['id'] == run_step_id)

        assert run_step['completed'] is True
        assert run_step['notes'] == "Step completed"
        assert run_step['completed_at'] is not None


class TestLabels:
    def test_create_label(self, temp_data_dir):
        """Test creating a label"""
        label_id = database.create_label("weekly", "#FF5733")

        assert label_id == 1

        labels = database.get_all_labels()
        assert len(labels) == 1
        assert labels[0]['name'] == "weekly"
        assert labels[0]['color'] == "#FF5733"

    def test_get_all_labels_empty(self, temp_data_dir):
        """Test getting labels when none exist"""
        labels = database.get_all_labels()
        assert len(labels) == 0

    def test_assign_label_to_procedure(self, temp_data_dir, sample_procedure):
        """Test assigning a label to a procedure"""
        label_id = database.create_label("test-label")

        database.assign_label_to_procedure(sample_procedure, label_id)

        labels = database.get_labels_for_procedure(sample_procedure)
        assert len(labels) == 1
        assert labels[0]['name'] == "test-label"

    def test_assign_duplicate_label(self, temp_data_dir, sample_procedure):
        """Test assigning same label twice (should not create duplicate)"""
        label_id = database.create_label("test-label")

        database.assign_label_to_procedure(sample_procedure, label_id)
        database.assign_label_to_procedure(sample_procedure, label_id)

        labels = database.get_labels_for_procedure(sample_procedure)
        assert len(labels) == 1

    def test_remove_label_from_procedure(self, temp_data_dir, sample_procedure):
        """Test removing a label from a procedure"""
        label_id = database.create_label("test-label")
        database.assign_label_to_procedure(sample_procedure, label_id)

        database.remove_label_from_procedure(sample_procedure, label_id)

        labels = database.get_labels_for_procedure(sample_procedure)
        assert len(labels) == 0

    def test_get_labels_for_procedure_none(self, temp_data_dir, sample_procedure):
        """Test getting labels when procedure has none"""
        labels = database.get_labels_for_procedure(sample_procedure)
        assert len(labels) == 0


class TestDataPersistence:
    def test_procedures_persist_after_save(self, temp_data_dir):
        """Test that procedures persist to CSV"""
        proc_id = database.create_procedure("Test", "Desc")

        # Load directly from CSV
        df = database.load_table("procedures")
        assert len(df) == 1
        assert df.iloc[0]['name'] == "Test"

    def test_multiple_operations_persist(self, temp_data_dir):
        """Test multiple operations persist correctly"""
        # Create procedure
        proc_id = database.create_procedure("Test", "Desc")

        # Add steps
        database.update_steps_for_procedure(proc_id, ["Step 1", "Step 2"])

        # Create run
        run_id = database.create_run(proc_id)

        # Verify all persisted
        procedures_df = database.load_table("procedures")
        steps_df = database.load_table("steps")
        runs_df = database.load_table("runs")

        assert len(procedures_df) == 1
        assert len(steps_df) == 2
        assert len(runs_df) == 1

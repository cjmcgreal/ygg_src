"""
Unit tests for logic module
"""

import pytest
from src import logic, database


class TestCreateProcedureWithSteps:
    def test_create_valid_procedure(self, temp_data_dir):
        """Test creating a valid procedure with steps"""
        success, proc_id, error = logic.create_procedure_with_steps(
            "Test Procedure",
            "Test description",
            ["Step 1", "Step 2", "Step 3"]
        )

        assert success is True
        assert proc_id is not None
        assert error is None

        # Verify procedure was created
        proc = database.get_procedure_by_id(proc_id)
        assert proc is not None
        assert proc['name'] == "Test Procedure"

        # Verify steps were created
        steps = database.get_steps_for_procedure(proc_id)
        assert len(steps) == 3

    def test_create_procedure_invalid_name(self, temp_data_dir):
        """Test creating procedure with invalid name"""
        success, proc_id, error = logic.create_procedure_with_steps(
            "",  # Empty name
            "Description",
            ["Step 1"]
        )

        assert success is False
        assert proc_id is None
        assert error is not None
        assert "name cannot be empty" in error

    def test_create_procedure_no_steps(self, temp_data_dir):
        """Test creating procedure without steps"""
        success, proc_id, error = logic.create_procedure_with_steps(
            "Test",
            "Description",
            []  # No steps
        )

        assert success is False
        assert proc_id is None
        assert error is not None


class TestUpdateProcedureWithSteps:
    def test_update_procedure_name(self, temp_data_dir, sample_procedure):
        """Test updating procedure name"""
        success, error = logic.update_procedure_with_steps(
            sample_procedure,
            name="Updated Name"
        )

        assert success is True
        assert error is None

        proc = database.get_procedure_by_id(sample_procedure)
        assert proc['name'] == "Updated Name"

    def test_update_procedure_steps(self, temp_data_dir, sample_procedure):
        """Test updating procedure steps"""
        new_steps = ["New Step 1", "New Step 2"]

        success, error = logic.update_procedure_with_steps(
            sample_procedure,
            steps=new_steps,
            change_description="Updated steps"
        )

        assert success is True
        assert error is None

        steps = database.get_steps_for_procedure(sample_procedure)
        assert len(steps) == 2
        assert steps[0]['description'] == "New Step 1"

    def test_update_nonexistent_procedure(self, temp_data_dir):
        """Test updating non-existent procedure"""
        success, error = logic.update_procedure_with_steps(
            999,  # Non-existent ID
            name="Test"
        )

        assert success is False
        assert error is not None
        assert "not found" in error

    def test_update_procedure_invalid_steps(self, temp_data_dir, sample_procedure):
        """Test updating with invalid steps"""
        success, error = logic.update_procedure_with_steps(
            sample_procedure,
            steps=[]  # Empty steps list
        )

        assert success is False
        assert error is not None


class TestStartProcedureRun:
    def test_start_valid_run(self, temp_data_dir, sample_procedure):
        """Test starting a valid procedure run"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        assert success is True
        assert run_id is not None
        assert error is None

        # Verify run was created
        run = database.get_run_by_id(run_id)
        assert run is not None
        assert run['status'] == 'in_progress'

        # Verify run steps were initialized
        run_steps = database.get_run_steps(run_id)
        assert len(run_steps) == 3  # Sample procedure has 3 steps

    def test_start_run_nonexistent_procedure(self, temp_data_dir):
        """Test starting run for non-existent procedure"""
        success, run_id, error = logic.start_procedure_run(999)

        assert success is False
        assert run_id is None
        assert error is not None
        assert "not found" in error


class TestCompleteStepInRun:
    def test_complete_step_success(self, temp_data_dir, sample_procedure):
        """Test completing a step in a run"""
        # Start run
        success, run_id, error = logic.start_procedure_run(sample_procedure)
        assert success is True

        # Get first step
        steps = database.get_steps_for_procedure(sample_procedure)
        first_step_id = steps[0]['id']

        # Complete the step
        success, error = logic.complete_step_in_run(
            run_id,
            first_step_id,
            notes="Test notes"
        )

        assert success is True
        assert error is None

        # Verify step was marked complete
        run_steps = database.get_run_steps(run_id)
        completed_step = next(rs for rs in run_steps if rs['step_id'] == first_step_id)
        assert completed_step['completed'] is True
        assert completed_step['notes'] == "Test notes"

    def test_complete_invalid_step(self, temp_data_dir, sample_procedure):
        """Test completing a step that doesn't exist in run"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        success, error = logic.complete_step_in_run(run_id, 999)

        assert success is False
        assert error is not None


class TestFinishRun:
    def test_finish_run_completed(self, temp_data_dir, sample_procedure):
        """Test finishing a run as completed"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        success, error = logic.finish_run(
            run_id,
            status="completed",
            notes="All done"
        )

        assert success is True
        assert error is None

        run = database.get_run_by_id(run_id)
        assert run['status'] == "completed"
        assert run['notes'] == "All done"
        assert run['end_time'] is not None

    def test_finish_run_cancelled(self, temp_data_dir, sample_procedure):
        """Test cancelling a run"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        success, error = logic.finish_run(run_id, status="cancelled")

        assert success is True

        run = database.get_run_by_id(run_id)
        assert run['status'] == "cancelled"

    def test_finish_run_invalid_status(self, temp_data_dir, sample_procedure):
        """Test finishing with invalid status"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        success, error = logic.finish_run(run_id, status="invalid_status")

        assert success is False
        assert error is not None

    def test_finish_nonexistent_run(self, temp_data_dir):
        """Test finishing non-existent run"""
        success, error = logic.finish_run(999)

        assert success is False
        assert error is not None


class TestGetProcedureWithMetadata:
    def test_get_procedure_with_metadata(self, temp_data_dir, sample_procedure_with_run):
        """Test getting procedure with metadata"""
        proc_id = sample_procedure_with_run['procedure_id']

        proc = logic.get_procedure_with_metadata(proc_id)

        assert proc is not None
        assert 'step_count' in proc
        assert 'steps' in proc
        assert 'labels' in proc
        assert 'total_runs' in proc
        assert 'completed_runs' in proc
        assert 'avg_duration_seconds' in proc
        assert 'completion_rate' in proc

        assert proc['step_count'] == 3
        assert proc['total_runs'] >= 1
        assert proc['completed_runs'] >= 1

    def test_get_nonexistent_procedure_with_metadata(self, temp_data_dir):
        """Test getting metadata for non-existent procedure"""
        proc = logic.get_procedure_with_metadata(999)
        assert proc is None


class TestGetAllProceduresWithMetadata:
    def test_get_all_procedures_with_metadata(self, temp_data_dir, multiple_procedures):
        """Test getting all procedures with metadata"""
        procedures = logic.get_all_procedures_with_metadata()

        assert len(procedures) == 3
        for proc in procedures:
            assert 'step_count' in proc
            assert 'total_runs' in proc

    def test_get_all_procedures_empty(self, temp_data_dir):
        """Test getting all procedures when none exist"""
        procedures = logic.get_all_procedures_with_metadata()
        assert len(procedures) == 0


class TestFilterProcedures:
    def test_filter_by_search(self, temp_data_dir, multiple_procedures):
        """Test filtering procedures by search term"""
        all_procs = logic.get_all_procedures_with_metadata()

        filtered = logic.filter_procedures(all_procs, search="Procedure 1")

        assert len(filtered) == 1
        assert "Procedure 1" in filtered[0]['name']

    def test_filter_case_insensitive(self, temp_data_dir, multiple_procedures):
        """Test search is case insensitive"""
        all_procs = logic.get_all_procedures_with_metadata()

        filtered = logic.filter_procedures(all_procs, search="procedure")

        assert len(filtered) == 3  # All match

    def test_filter_by_description(self, temp_data_dir, multiple_procedures):
        """Test filtering by description text"""
        all_procs = logic.get_all_procedures_with_metadata()

        filtered = logic.filter_procedures(all_procs, search="Description for")

        assert len(filtered) == 3

    def test_filter_no_results(self, temp_data_dir, multiple_procedures):
        """Test filtering with no matches"""
        all_procs = logic.get_all_procedures_with_metadata()

        filtered = logic.filter_procedures(all_procs, search="NonexistentTerm")

        assert len(filtered) == 0


class TestGetRunWithDetails:
    def test_get_run_with_details(self, temp_data_dir, sample_procedure_with_run):
        """Test getting run with full details"""
        run_id = sample_procedure_with_run['run_id']

        run = logic.get_run_with_details(run_id)

        assert run is not None
        assert 'procedure' in run
        assert 'steps' in run
        assert 'duration_seconds' in run
        assert 'duration_formatted' in run

        assert len(run['steps']) == 3

    def test_get_nonexistent_run_with_details(self, temp_data_dir):
        """Test getting details for non-existent run"""
        run = logic.get_run_with_details(999)
        assert run is None


class TestGetActiveRun:
    def test_get_active_run_exists(self, temp_data_dir, sample_procedure):
        """Test getting active run when one exists"""
        # Start a run
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        active = logic.get_active_run()

        assert active is not None
        assert active['id'] == run_id
        assert active['status'] == 'in_progress'

    def test_get_active_run_none(self, temp_data_dir):
        """Test getting active run when none exists"""
        active = logic.get_active_run()
        assert active is None

    def test_get_active_run_after_completion(self, temp_data_dir, sample_procedure):
        """Test no active run after completion"""
        # Start and finish run
        success, run_id, error = logic.start_procedure_run(sample_procedure)
        logic.finish_run(run_id, status="completed")

        active = logic.get_active_run()
        assert active is None


class TestGetRunProgress:
    def test_get_run_progress_no_steps_complete(self, temp_data_dir, sample_procedure):
        """Test progress with no steps completed"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        progress = logic.get_run_progress(run_id)

        assert progress['total_steps'] == 3
        assert progress['completed_steps'] == 0
        assert progress['remaining_steps'] == 3
        assert progress['progress_percent'] == 0

    def test_get_run_progress_partial_complete(self, temp_data_dir, sample_procedure):
        """Test progress with some steps completed"""
        success, run_id, error = logic.start_procedure_run(sample_procedure)

        # Complete first step
        steps = database.get_steps_for_procedure(sample_procedure)
        logic.complete_step_in_run(run_id, steps[0]['id'])

        progress = logic.get_run_progress(run_id)

        assert progress['total_steps'] == 3
        assert progress['completed_steps'] == 1
        assert progress['remaining_steps'] == 2
        assert progress['progress_percent'] == pytest.approx(33.33, rel=0.1)

    def test_get_run_progress_all_complete(self, temp_data_dir, sample_procedure_with_run):
        """Test progress with all steps completed"""
        run_id = sample_procedure_with_run['run_id']

        progress = logic.get_run_progress(run_id)

        assert progress['total_steps'] == 3
        assert progress['completed_steps'] == 3
        assert progress['remaining_steps'] == 0
        assert progress['progress_percent'] == 100

"""
Unit tests for utils module
"""

import pytest
from datetime import datetime, timedelta
from src import utils


class TestGenerateId:
    def test_generate_id_empty_list(self):
        """Test ID generation with empty list"""
        result = utils.generate_id([])
        assert result == 1

    def test_generate_id_with_existing_ids(self):
        """Test ID generation with existing IDs"""
        result = utils.generate_id([1, 2, 3])
        assert result == 4

    def test_generate_id_non_sequential(self):
        """Test ID generation with non-sequential IDs"""
        result = utils.generate_id([1, 5, 10, 3])
        assert result == 11


class TestFormatDuration:
    def test_format_duration_none(self):
        """Test formatting None duration"""
        assert utils.format_duration(None) == "N/A"

    def test_format_duration_seconds(self):
        """Test formatting seconds only"""
        assert utils.format_duration(45) == "45s"

    def test_format_duration_minutes(self):
        """Test formatting minutes"""
        assert utils.format_duration(90) == "1m 30s"
        assert utils.format_duration(120) == "2m"

    def test_format_duration_hours(self):
        """Test formatting hours"""
        assert utils.format_duration(3600) == "1h"
        assert utils.format_duration(3660) == "1h 1m"
        assert utils.format_duration(7200) == "2h"


class TestSafeDivide:
    def test_safe_divide_normal(self):
        """Test normal division"""
        assert utils.safe_divide(10, 2) == 5.0

    def test_safe_divide_by_zero(self):
        """Test division by zero returns default"""
        assert utils.safe_divide(10, 0) == 0.0
        assert utils.safe_divide(10, 0, default=99) == 99

    def test_safe_divide_floats(self):
        """Test float division"""
        assert utils.safe_divide(7.5, 2.5) == 3.0


class TestValidateProcedureData:
    def test_validate_valid_data(self):
        """Test validation with valid data"""
        is_valid, error = utils.validate_procedure_data(
            "Test Procedure",
            ["Step 1", "Step 2"]
        )
        assert is_valid is True
        assert error is None

    def test_validate_empty_name(self):
        """Test validation with empty name"""
        is_valid, error = utils.validate_procedure_data("", ["Step 1"])
        assert is_valid is False
        assert "name cannot be empty" in error

    def test_validate_whitespace_name(self):
        """Test validation with whitespace-only name"""
        is_valid, error = utils.validate_procedure_data("   ", ["Step 1"])
        assert is_valid is False
        assert "name cannot be empty" in error

    def test_validate_long_name(self):
        """Test validation with name too long"""
        long_name = "a" * 201
        is_valid, error = utils.validate_procedure_data(long_name, ["Step 1"])
        assert is_valid is False
        assert "200 characters" in error

    def test_validate_no_steps(self):
        """Test validation with no steps"""
        is_valid, error = utils.validate_procedure_data("Test", [])
        assert is_valid is False
        assert "at least one step" in error

    def test_validate_empty_step(self):
        """Test validation with empty step"""
        is_valid, error = utils.validate_procedure_data(
            "Test",
            ["Step 1", ""]
        )
        assert is_valid is False
        assert "Step 2 cannot be empty" in error

    def test_validate_too_many_steps(self):
        """Test validation with too many steps"""
        steps = [f"Step {i}" for i in range(101)]
        is_valid, error = utils.validate_procedure_data("Test", steps)
        assert is_valid is False
        assert "cannot have more than 100 steps" in error

    def test_validate_step_too_long(self):
        """Test validation with step description too long"""
        long_step = "a" * 501
        is_valid, error = utils.validate_procedure_data(
            "Test",
            ["Step 1", long_step]
        )
        assert is_valid is False
        assert "Step 2 must be 500 characters" in error


class TestFormatDatetime:
    def test_format_datetime_none(self):
        """Test formatting None datetime"""
        assert utils.format_datetime(None) == "N/A"

    def test_format_datetime_object(self):
        """Test formatting datetime object"""
        dt = datetime(2025, 10, 12, 14, 30, 0)
        result = utils.format_datetime(dt)
        assert "2025-10-12" in result
        assert "14:30:00" in result

    def test_format_datetime_string(self):
        """Test formatting datetime string"""
        dt_str = "2025-10-12T14:30:00"
        result = utils.format_datetime(dt_str)
        assert "2025-10-12" in result

    def test_format_datetime_custom_format(self):
        """Test custom format string"""
        dt = datetime(2025, 10, 12, 14, 30, 0)
        result = utils.format_datetime(dt, "%Y-%m-%d")
        assert result == "2025-10-12"


class TestCalculateDurationSeconds:
    def test_calculate_duration_with_end_time(self):
        """Test duration calculation with both times"""
        start = datetime(2025, 10, 12, 10, 0, 0)
        end = datetime(2025, 10, 12, 10, 5, 0)
        duration = utils.calculate_duration_seconds(start, end)
        assert duration == 300  # 5 minutes

    def test_calculate_duration_no_end_time(self):
        """Test duration calculation without end time (uses now)"""
        start = datetime.now() - timedelta(seconds=10)
        duration = utils.calculate_duration_seconds(start)
        assert 9 <= duration <= 11  # Allow small time delta

    def test_calculate_duration_none_start(self):
        """Test duration calculation with None start"""
        duration = utils.calculate_duration_seconds(None)
        assert duration is None

    def test_calculate_duration_string_inputs(self):
        """Test duration calculation with string inputs"""
        start = "2025-10-12T10:00:00"
        end = "2025-10-12T10:05:00"
        duration = utils.calculate_duration_seconds(start, end)
        assert duration == 300


class TestTruncateText:
    def test_truncate_short_text(self):
        """Test truncating text shorter than max length"""
        text = "Short text"
        result = utils.truncate_text(text, 50)
        assert result == "Short text"

    def test_truncate_long_text(self):
        """Test truncating long text"""
        text = "This is a very long text that should be truncated"
        result = utils.truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_exact_length(self):
        """Test text exactly at max length"""
        text = "a" * 50
        result = utils.truncate_text(text, 50)
        assert result == text
        assert not result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test custom suffix"""
        text = "This is a long text"
        result = utils.truncate_text(text, 10, suffix=">>")
        assert result.endswith(">>")
        assert len(result) == 10

"""
Unit tests for analysis module
"""

import pytest
from src import analysis, database


class TestGetCompletionRate:
    def test_completion_rate_no_runs(self, temp_data_dir, sample_procedure):
        """Test completion rate with no runs"""
        rate = analysis.get_completion_rate(sample_procedure)
        assert rate == 0.0

    def test_completion_rate_all_completed(self, temp_data_dir, procedure_with_multiple_runs):
        """Test completion rate with mixed results"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        rate = analysis.get_completion_rate(proc_id)

        # 4 completed out of 5 total (1 cancelled)
        assert rate == 80.0

    def test_completion_rate_partial(self, temp_data_dir, sample_procedure):
        """Test completion rate with partial completions"""
        # Create 2 completed runs
        for _ in range(2):
            run_id = database.create_run(sample_procedure)
            database.update_run(run_id, status="completed", end_now=True)

        # Create 1 cancelled run
        run_id = database.create_run(sample_procedure)
        database.update_run(run_id, status="cancelled", end_now=True)

        rate = analysis.get_completion_rate(sample_procedure)

        # 2 out of 3 = 66.67%
        assert rate == pytest.approx(66.67, rel=0.1)


class TestGetAverageDuration:
    def test_average_duration_no_completed_runs(self, temp_data_dir, sample_procedure):
        """Test average duration with no completed runs"""
        avg = analysis.get_average_duration(sample_procedure)
        assert avg is None

    def test_average_duration_single_run(self, temp_data_dir, sample_procedure_with_run):
        """Test average duration with one completed run"""
        proc_id = sample_procedure_with_run['procedure_id']

        avg = analysis.get_average_duration(proc_id)

        assert avg is not None
        assert avg > 0

    def test_average_duration_multiple_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test average duration with multiple runs"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        avg = analysis.get_average_duration(proc_id)

        assert avg is not None
        assert avg > 0


class TestGetDurationVariance:
    def test_duration_variance_insufficient_data(self, temp_data_dir, sample_procedure):
        """Test variance with insufficient data"""
        variance = analysis.get_duration_variance(sample_procedure)
        assert variance is None

    def test_duration_variance_single_run(self, temp_data_dir, sample_procedure_with_run):
        """Test variance with single run"""
        proc_id = sample_procedure_with_run['procedure_id']

        variance = analysis.get_duration_variance(proc_id)

        # Need at least 2 runs for variance
        assert variance is None

    def test_duration_variance_multiple_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test variance with multiple runs"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        variance = analysis.get_duration_variance(proc_id)

        # Should have variance with 4 completed runs
        assert variance is not None
        assert variance >= 0


class TestGetRunFrequency:
    def test_run_frequency_no_runs(self, temp_data_dir, sample_procedure):
        """Test frequency with no runs"""
        freq = analysis.get_run_frequency(sample_procedure, days=30)
        assert freq == 0.0

    def test_run_frequency_with_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test frequency with runs"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        freq = analysis.get_run_frequency(proc_id, days=30)

        # 5 runs in 30 days = 5 / (30/7) = ~1.17 per week
        assert freq > 0


class TestGetMostFrequentProcedures:
    def test_most_frequent_no_runs(self, temp_data_dir, multiple_procedures):
        """Test most frequent with no runs"""
        frequent = analysis.get_most_frequent_procedures(limit=5)
        assert len(frequent) == 0

    def test_most_frequent_with_runs(self, temp_data_dir, multiple_procedures):
        """Test most frequent with various run counts"""
        # Create different numbers of runs for each procedure
        for i, proc_id in enumerate(multiple_procedures):
            for _ in range(i + 1):  # 1, 2, 3 runs respectively
                run_id = database.create_run(proc_id)
                database.update_run(run_id, status="completed", end_now=True)

        frequent = analysis.get_most_frequent_procedures(limit=2)

        assert len(frequent) == 2
        # Most frequent should be Procedure 3 with 3 runs
        assert frequent[0]['run_count'] == 3
        assert frequent[1]['run_count'] == 2

    def test_most_frequent_limit(self, temp_data_dir, multiple_procedures):
        """Test limit parameter"""
        # Create runs
        for proc_id in multiple_procedures:
            run_id = database.create_run(proc_id)
            database.update_run(run_id, status="completed", end_now=True)

        frequent = analysis.get_most_frequent_procedures(limit=1)

        assert len(frequent) == 1


class TestGetOverallStats:
    def test_overall_stats_no_data(self, temp_data_dir):
        """Test overall stats with no data"""
        stats = analysis.get_overall_stats()

        assert stats['total_procedures'] == 0
        assert stats['total_runs'] == 0
        assert stats['completed_runs'] == 0
        assert stats['overall_completion_rate'] == 0

    def test_overall_stats_with_data(self, temp_data_dir, procedure_with_multiple_runs):
        """Test overall stats with data"""
        stats = analysis.get_overall_stats()

        assert stats['total_procedures'] == 1
        assert stats['total_runs'] == 5
        assert stats['completed_runs'] == 4
        assert stats['cancelled_runs'] == 1
        assert stats['overall_completion_rate'] == 80.0

    def test_overall_stats_multiple_procedures(self, temp_data_dir, multiple_procedures):
        """Test overall stats with multiple procedures"""
        # Create runs for each procedure
        for proc_id in multiple_procedures:
            for _ in range(2):
                run_id = database.create_run(proc_id)
                database.update_run(run_id, status="completed", end_now=True)

        stats = analysis.get_overall_stats()

        assert stats['total_procedures'] == 3
        assert stats['total_runs'] == 6
        assert stats['completed_runs'] == 6
        assert stats['overall_completion_rate'] == 100.0


class TestGetProcedureTrends:
    def test_trends_no_runs(self, temp_data_dir, sample_procedure):
        """Test trends with no runs"""
        trends = analysis.get_procedure_trends(sample_procedure, days=30)
        assert len(trends) == 0

    def test_trends_with_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test trends with runs"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        trends = analysis.get_procedure_trends(proc_id, days=30)

        # Should have at least one day with data
        assert len(trends) >= 1

        # Each trend should have required fields
        for trend in trends:
            assert 'date' in trend
            assert 'total_runs' in trend
            assert 'completed_runs' in trend


class TestGetCompletionRateByProcedure:
    def test_completion_rate_by_procedure_no_runs(self, temp_data_dir, multiple_procedures):
        """Test completion rates with no runs"""
        rates = analysis.get_completion_rate_by_procedure()
        assert len(rates) == 0

    def test_completion_rate_by_procedure_with_runs(self, temp_data_dir, multiple_procedures):
        """Test completion rates with runs"""
        # Create runs with different completion rates
        # Procedure 1: 100% completion (2/2)
        for _ in range(2):
            run_id = database.create_run(multiple_procedures[0])
            database.update_run(run_id, status="completed", end_now=True)

        # Procedure 2: 50% completion (1/2)
        run_id = database.create_run(multiple_procedures[1])
        database.update_run(run_id, status="completed", end_now=True)
        run_id = database.create_run(multiple_procedures[1])
        database.update_run(run_id, status="cancelled", end_now=True)

        rates = analysis.get_completion_rate_by_procedure()

        assert len(rates) == 2

        # Should be sorted by completion rate descending
        assert rates[0]['completion_rate'] >= rates[1]['completion_rate']

    def test_completion_rate_by_procedure_structure(self, temp_data_dir, sample_procedure):
        """Test structure of completion rate results"""
        run_id = database.create_run(sample_procedure)
        database.update_run(run_id, status="completed", end_now=True)

        rates = analysis.get_completion_rate_by_procedure()

        assert len(rates) == 1
        rate = rates[0]

        assert 'procedure_id' in rate
        assert 'name' in rate
        assert 'total_runs' in rate
        assert 'completed_runs' in rate
        assert 'completion_rate' in rate


class TestGetRecentActivity:
    def test_recent_activity_no_runs(self, temp_data_dir):
        """Test recent activity with no runs"""
        activity = analysis.get_recent_activity(days=7, limit=10)
        assert len(activity) == 0

    def test_recent_activity_with_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test recent activity with runs"""
        activity = analysis.get_recent_activity(days=7, limit=10)

        # Should have runs
        assert len(activity) > 0

        # Check structure
        for item in activity:
            assert 'run_id' in item
            assert 'procedure_name' in item
            assert 'start_time' in item
            assert 'status' in item
            assert 'duration_formatted' in item

    def test_recent_activity_limit(self, temp_data_dir, procedure_with_multiple_runs):
        """Test recent activity respects limit"""
        activity = analysis.get_recent_activity(days=7, limit=2)

        assert len(activity) <= 2

    def test_recent_activity_sorted_by_time(self, temp_data_dir, sample_procedure):
        """Test recent activity is sorted by most recent first"""
        # Create multiple runs
        for _ in range(3):
            run_id = database.create_run(sample_procedure)
            database.update_run(run_id, status="completed", end_now=True)

        activity = analysis.get_recent_activity(days=7, limit=10)

        # Should be sorted with most recent first
        for i in range(len(activity) - 1):
            assert activity[i]['start_time'] >= activity[i + 1]['start_time']


class TestGetBottleneckSteps:
    def test_bottleneck_steps_no_runs(self, temp_data_dir, sample_procedure):
        """Test bottleneck identification with no runs"""
        bottlenecks = analysis.get_bottleneck_steps(sample_procedure)

        # Returns steps in order even without run data
        assert len(bottlenecks) == 3

    def test_bottleneck_steps_with_runs(self, temp_data_dir, sample_procedure_with_run):
        """Test bottleneck identification with runs"""
        proc_id = sample_procedure_with_run['procedure_id']

        bottlenecks = analysis.get_bottleneck_steps(proc_id)

        # Should return steps
        assert len(bottlenecks) == 3
        assert 'description' in bottlenecks[0]


class TestGetTimeDistribution:
    def test_time_distribution_no_runs(self, temp_data_dir, sample_procedure):
        """Test time distribution with no runs"""
        distribution = analysis.get_time_distribution(sample_procedure, bins=5)
        assert len(distribution) == 0

    def test_time_distribution_with_runs(self, temp_data_dir, procedure_with_multiple_runs):
        """Test time distribution with runs"""
        proc_id = procedure_with_multiple_runs['procedure_id']

        distribution = analysis.get_time_distribution(proc_id, bins=3)

        # Should have distribution data
        assert len(distribution) > 0

        # Check structure
        for item in distribution:
            assert 'min_seconds' in item
            assert 'max_seconds' in item
            assert 'count' in item
            assert 'label' in item

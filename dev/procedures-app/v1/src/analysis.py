"""
Analytics and metrics calculations for procedures
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from . import database
from . import utils


def get_completion_rate(procedure_id: int) -> float:
    """
    Calculate completion rate for a procedure

    Args:
        procedure_id: Procedure ID

    Returns:
        Completion rate as percentage (0-100)
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[runs_df['procedure_id'] == procedure_id]

    if len(proc_runs) == 0:
        return 0.0

    completed = len(proc_runs[proc_runs['status'] == 'completed'])
    total = len(proc_runs)

    return (completed / total) * 100


def get_average_duration(procedure_id: int) -> Optional[float]:
    """
    Calculate average execution time for a procedure

    Args:
        procedure_id: Procedure ID

    Returns:
        Average duration in seconds, or None if no completed runs
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[
        (runs_df['procedure_id'] == procedure_id) &
        (runs_df['status'] == 'completed') &
        (runs_df['end_time'].notna())
    ]

    if proc_runs.empty:
        return None

    durations = (proc_runs['end_time'] - proc_runs['start_time']).dt.total_seconds()
    return durations.mean()


def get_duration_variance(procedure_id: int) -> Optional[float]:
    """
    Calculate standard deviation of execution times

    Args:
        procedure_id: Procedure ID

    Returns:
        Standard deviation in seconds, or None if insufficient data
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[
        (runs_df['procedure_id'] == procedure_id) &
        (runs_df['status'] == 'completed') &
        (runs_df['end_time'].notna())
    ]

    if len(proc_runs) < 2:
        return None

    durations = (proc_runs['end_time'] - proc_runs['start_time']).dt.total_seconds()
    return durations.std()


def get_run_frequency(procedure_id: int, days: int = 30) -> float:
    """
    Calculate how often a procedure is run

    Args:
        procedure_id: Procedure ID
        days: Time period to analyze

    Returns:
        Average runs per week
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[runs_df['procedure_id'] == procedure_id]

    if proc_runs.empty:
        return 0.0

    # Filter to recent runs
    cutoff = datetime.now() - timedelta(days=days)
    recent_runs = proc_runs[proc_runs['start_time'] >= cutoff]

    runs_count = len(recent_runs)
    weeks = days / 7

    return runs_count / weeks if weeks > 0 else 0.0


def get_most_frequent_procedures(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most frequently run procedures

    Args:
        limit: Number of results to return

    Returns:
        List of procedure dicts with run counts
    """
    runs_df = database.get_all_runs()
    procedures_df = database.get_all_procedures()

    if runs_df.empty:
        return []

    # Count runs per procedure
    run_counts = runs_df.groupby('procedure_id').size().reset_index(name='run_count')

    # Merge with procedure names
    result = run_counts.merge(procedures_df[['id', 'name']], left_on='procedure_id', right_on='id')

    # Sort and limit
    result = result.sort_values('run_count', ascending=False).head(limit)

    return result[['procedure_id', 'name', 'run_count']].to_dict('records')


def get_overall_stats() -> Dict[str, Any]:
    """
    Get overall statistics across all procedures

    Returns:
        Dict with overall metrics
    """
    procedures_df = database.get_all_procedures()
    runs_df = database.get_all_runs()

    total_procedures = len(procedures_df)
    total_runs = len(runs_df)
    completed_runs = len(runs_df[runs_df['status'] == 'completed'])
    cancelled_runs = len(runs_df[runs_df['status'] == 'cancelled'])
    in_progress_runs = len(runs_df[runs_df['status'] == 'in_progress'])

    # Calculate average completion rate
    overall_completion_rate = utils.safe_divide(completed_runs, total_runs, 0) * 100

    # Get runs this week
    week_ago = datetime.now() - timedelta(days=7)
    runs_this_week = len(runs_df[runs_df['start_time'] >= week_ago])

    # Get most run procedure
    most_frequent = get_most_frequent_procedures(limit=1)
    most_frequent_name = most_frequent[0]['name'] if most_frequent else "N/A"

    return {
        'total_procedures': total_procedures,
        'total_runs': total_runs,
        'completed_runs': completed_runs,
        'cancelled_runs': cancelled_runs,
        'in_progress_runs': in_progress_runs,
        'overall_completion_rate': overall_completion_rate,
        'runs_this_week': runs_this_week,
        'most_frequent_procedure': most_frequent_name
    }


def get_procedure_trends(procedure_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get time series data for a procedure

    Args:
        procedure_id: Procedure ID
        days: Number of days to analyze

    Returns:
        List of dicts with date and metrics
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[
        (runs_df['procedure_id'] == procedure_id) &
        (runs_df['start_time'] >= datetime.now() - timedelta(days=days))
    ]

    if proc_runs.empty:
        return []

    # Group by date
    proc_runs['date'] = proc_runs['start_time'].dt.date
    daily_stats = proc_runs.groupby('date').agg({
        'id': 'count',  # Number of runs
        'status': lambda x: (x == 'completed').sum()  # Completed runs
    }).reset_index()

    daily_stats.columns = ['date', 'total_runs', 'completed_runs']

    return daily_stats.to_dict('records')


def get_bottleneck_steps(procedure_id: int) -> List[Dict[str, Any]]:
    """
    Identify steps that take the longest time

    Args:
        procedure_id: Procedure ID

    Returns:
        List of steps with average completion times
    """
    # Note: To properly calculate step duration, we would need to track
    # when each step started, not just when it completed
    # For now, return steps ordered by their position
    # This is a placeholder for future enhancement

    steps_df = database.load_table("steps")
    procedure_steps = steps_df[steps_df['procedure_id'] == procedure_id]

    if procedure_steps.empty:
        return []

    return procedure_steps.sort_values('order').to_dict('records')


def get_completion_rate_by_procedure() -> List[Dict[str, Any]]:
    """
    Get completion rates for all procedures

    Returns:
        List of procedures with completion rates
    """
    procedures_df = database.get_all_procedures()
    runs_df = database.get_all_runs()

    if runs_df.empty:
        return []

    result = []
    for _, proc in procedures_df.iterrows():
        proc_runs = runs_df[runs_df['procedure_id'] == proc['id']]

        if not proc_runs.empty:
            completed = len(proc_runs[proc_runs['status'] == 'completed'])
            total = len(proc_runs)
            completion_rate = (completed / total) * 100

            result.append({
                'procedure_id': proc['id'],
                'name': proc['name'],
                'total_runs': total,
                'completed_runs': completed,
                'completion_rate': completion_rate
            })

    # Sort by completion rate descending
    result.sort(key=lambda x: x['completion_rate'], reverse=True)

    return result


def get_time_distribution(procedure_id: int, bins: int = 5) -> List[Dict[str, Any]]:
    """
    Get distribution of execution times

    Args:
        procedure_id: Procedure ID
        bins: Number of bins for histogram

    Returns:
        List of bin ranges with counts
    """
    runs_df = database.get_all_runs()
    proc_runs = runs_df[
        (runs_df['procedure_id'] == procedure_id) &
        (runs_df['status'] == 'completed') &
        (runs_df['end_time'].notna())
    ]

    if proc_runs.empty:
        return []

    durations = (proc_runs['end_time'] - proc_runs['start_time']).dt.total_seconds()

    # Create histogram
    counts, bin_edges = pd.cut(durations, bins=bins, retbins=True)
    distribution = counts.value_counts().sort_index()

    result = []
    for interval, count in distribution.items():
        result.append({
            'min_seconds': interval.left,
            'max_seconds': interval.right,
            'count': count,
            'label': f"{utils.format_duration(interval.left)} - {utils.format_duration(interval.right)}"
        })

    return result


def get_recent_activity(days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent procedure activity

    Args:
        days: Number of days to look back
        limit: Maximum number of results

    Returns:
        List of recent runs with details
    """
    runs_df = database.get_all_runs()
    procedures_df = database.get_all_procedures()

    cutoff = datetime.now() - timedelta(days=days)
    recent_runs = runs_df[runs_df['start_time'] >= cutoff]

    if recent_runs.empty:
        return []

    # Merge with procedure names
    result = recent_runs.merge(
        procedures_df[['id', 'name']],
        left_on='procedure_id',
        right_on='id',
        suffixes=('', '_proc')
    )

    # Calculate durations
    result['duration'] = (result['end_time'] - result['start_time']).dt.total_seconds()

    # Sort by start time descending
    result = result.sort_values('start_time', ascending=False).head(limit)

    # Format output
    output = []
    for _, row in result.iterrows():
        output.append({
            'run_id': row['id'],
            'procedure_name': row['name'],
            'start_time': row['start_time'],
            'status': row['status'],
            'duration_formatted': utils.format_duration(row['duration']) if pd.notna(row['duration']) else "In progress"
        })

    return output

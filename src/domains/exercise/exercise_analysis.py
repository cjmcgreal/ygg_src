"""
Exercise data analysis.
Contains data processing and computational functions.
"""
import pandas as pd


def get_exercise_summary(exercise_df):
    """
    Calculate summary statistics for exercise data.

    Args:
        exercise_df (pd.DataFrame): Exercise data with numeric columns

    Returns:
        dict: Summary statistics (total, average, max)
    """
    if exercise_df.empty:
        return {'total': 0, 'average': 0, 'max': 0}

    # Get first numeric column for analysis
    numeric_cols = exercise_df.select_dtypes(include=['number']).columns

    if len(numeric_cols) == 0:
        return {'total': 0, 'average': 0, 'max': 0}

    col = numeric_cols[0]

    return {
        'total': len(exercise_df),
        'average': exercise_df[col].mean(),
        'max': exercise_df[col].max()
    }


def aggregate_by_category(exercise_df, category_col, value_col):
    """
    Aggregate exercise data by category.

    Args:
        exercise_df (pd.DataFrame): Exercise data
        category_col (str): Column name to group by
        value_col (str): Column name to sum

    Returns:
        pd.DataFrame: Aggregated data
    """
    if exercise_df.empty:
        return pd.DataFrame()

    aggregated = exercise_df.groupby(category_col)[value_col].sum().reset_index()
    aggregated = aggregated.sort_values(value_col, ascending=False)

    return aggregated


if __name__ == "__main__":
    # Standalone test
    print("Exercise Analysis - Standalone Test")
    print("=" * 50)

    # Create sample data
    sample_data = pd.DataFrame({
        'exercise': ['Push-ups', 'Squats', 'Lunges'],
        'reps': [20, 30, 25],
        'category': ['Upper', 'Lower', 'Lower']
    })

    print("\nSample data:")
    print(sample_data)

    # Test summary
    print("\n1. Testing get_exercise_summary:")
    summary = get_exercise_summary(sample_data)
    print(f"   Summary: {summary}")

    # Test aggregation
    print("\n2. Testing aggregate_by_category:")
    aggregated = aggregate_by_category(sample_data, 'category', 'reps')
    print(f"   Aggregated by category:")
    print(aggregated)

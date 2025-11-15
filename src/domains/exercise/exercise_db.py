"""
Exercise database interface.
Handles CSV file reading and writing for exercise data.
"""
import pandas as pd
import os


def get_csv_path():
    """Get the path to the exercises CSV file."""
    return "domains/exercise/exercise_data/exercises.csv"


def load_exercise_data():
    """
    Load exercise data from CSV file.

    Returns:
        pd.DataFrame: Exercise data, or empty DataFrame if file doesn't exist
    """
    csv_path = get_csv_path()

    if not os.path.exists(csv_path):
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['exercise', 'reps', 'date'])

    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading exercise data: {e}")
        return pd.DataFrame(columns=['exercise', 'reps', 'date'])


def save_exercise_data(exercise_df):
    """
    Save exercise data to CSV file.

    Args:
        exercise_df (pd.DataFrame): Exercise data to save

    Returns:
        bool: True if successful, False otherwise
    """
    csv_path = get_csv_path()

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Save to CSV
        exercise_df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving exercise data: {e}")
        return False


if __name__ == "__main__":
    # Standalone test
    print("Exercise DB - Standalone Test")
    print("=" * 50)

    print(f"\n1. CSV Path: {get_csv_path()}")

    # Test load
    print("\n2. Testing load_exercise_data:")
    df = load_exercise_data()
    print(f"   Loaded {len(df)} rows")
    print(f"   Columns: {df.columns.tolist()}")

    # Test save with sample data
    print("\n3. Testing save_exercise_data:")
    sample_df = pd.DataFrame({
        'exercise': ['Push-ups', 'Squats'],
        'reps': [20, 30],
        'date': ['2025-11-15', '2025-11-15']
    })
    success = save_exercise_data(sample_df)
    print(f"   Save successful: {success}")

    if success:
        # Verify by loading again
        loaded = load_exercise_data()
        print(f"   Verification - loaded {len(loaded)} rows after save")

"""
Database layer for the music arrangement generator.

Handles CSV file I/O for:
- generation_history.csv (log of generations)
"""

from pathlib import Path
from datetime import datetime
import pandas as pd

DATA_DIR = Path(__file__).parent / "arrangement_data"


def ensure_data_files_exist() -> None:
    """
    Create data directory and CSV files if they don't exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    history_file = DATA_DIR / "generation_history.csv"
    if not history_file.exists():
        df = pd.DataFrame(columns=[
            'id', 'input_filename', 'num_chords', 'octave', 'generated_date'
        ])
        df.to_csv(history_file, index=False)


def load_generation_history() -> pd.DataFrame:
    """
    Load generation history from CSV.

    Returns:
        pd.DataFrame: Columns: id, input_filename, num_chords, octave, generated_date
    """
    ensure_data_files_exist()
    history_file = DATA_DIR / "generation_history.csv"
    return pd.read_csv(history_file)


def log_generation(
    input_filename: str,
    num_chords: int,
    octave: int = 4
) -> tuple[bool, int]:
    """
    Log a new generation to history.

    Args:
        input_filename: Name of the uploaded MusicXML file
        num_chords: Number of chords processed
        octave: Octave used for generation

    Returns:
        tuple: (success: bool, new_id: int)
    """
    try:
        ensure_data_files_exist()
        history_file = DATA_DIR / "generation_history.csv"

        df = pd.read_csv(history_file)

        # Generate new ID
        new_id = df['id'].max() + 1 if len(df) > 0 else 1

        # Create new row
        new_row = pd.DataFrame([{
            'id': new_id,
            'input_filename': input_filename,
            'num_chords': num_chords,
            'octave': octave,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }])

        # Append and save
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(history_file, index=False)

        return True, new_id

    except Exception as e:
        print(f"Error logging generation: {e}")
        return False, -1


def get_recent_generations(n: int = 50) -> pd.DataFrame:
    """
    Get n most recent generations.

    Args:
        n: Maximum number of records to return

    Returns:
        pd.DataFrame: Recent generation history, sorted by date descending
    """
    df = load_generation_history()

    if len(df) == 0:
        return df

    # Sort by date descending and take top n
    df = df.sort_values('generated_date', ascending=False).head(n)
    return df


if __name__ == "__main__":
    # Example usage for manual testing
    print("Testing arrangement_db.py")
    print("=" * 40)

    # Ensure data files exist
    print("\nEnsuring data files exist...")
    ensure_data_files_exist()
    print(f"Data directory: {DATA_DIR}")
    print(f"Directory exists: {DATA_DIR.exists()}")

    # Log a test generation
    print("\nLogging a test generation...")
    success, new_id = log_generation(
        input_filename="test_song.xml",
        num_chords=16,
        octave=4
    )
    print(f"Success: {success}, New ID: {new_id}")

    # Log another one
    success, new_id = log_generation(
        input_filename="autumn_leaves.xml",
        num_chords=32,
        octave=5
    )
    print(f"Success: {success}, New ID: {new_id}")

    # Load and display history
    print("\nGeneration history:")
    history = get_recent_generations(10)
    print(history.to_string(index=False))

    print("\n" + "=" * 40)
    print("All tests completed successfully!")

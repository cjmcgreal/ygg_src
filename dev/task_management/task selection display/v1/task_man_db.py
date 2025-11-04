import pandas as pd

def load_task_data(csv_path: str) -> pd.DataFrame:
    """Load task data from a CSV file."""
    return pd.read_csv(csv_path)

def save_task_data(df: pd.DataFrame, csv_path: str) -> None:
    """Save updated task data back to CSV."""
    df.to_csv(csv_path, index=False)

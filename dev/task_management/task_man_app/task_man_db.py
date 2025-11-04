import pandas as pd

def load_task_data(csv_path: str) -> pd.DataFrame:
    """Load task data from a CSV file."""
    
    # read csv
    df = pd.read_csv(csv_path)

    # replace nans in column "is_recurring"
    column_name = 'is_recurring'
    replacement_value = 'False'
    df[column_name] = df[column_name].fillna(replacement_value)
    
    return df

def save_task_data(df: pd.DataFrame, csv_path: str) -> None:
    """Save updated task data back to CSV."""
    df.to_csv(csv_path, index=False)

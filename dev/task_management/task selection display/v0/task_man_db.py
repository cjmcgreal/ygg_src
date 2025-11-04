"""Handles reading and writing the CSV task database."""
import pandas as pd

def read_task_db(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)

def write_task_db(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path, index=False)

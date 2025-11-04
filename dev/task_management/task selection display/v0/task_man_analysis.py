"""Analysis module: provides helpers for extracting insights from the task dataset."""
import pandas as pd

def get_unique_values(df: pd.DataFrame) -> dict:
    return {col: sorted(df[col].dropna().unique().tolist()) for col in df.columns if df[col].dtype == "object"}

def get_visible_columns(all_columns, hidden_columns):
    return [col for col in all_columns if col not in hidden_columns]

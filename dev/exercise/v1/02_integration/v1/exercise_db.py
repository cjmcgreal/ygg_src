import pandas as pd

def load_db(path):
    """Load workout database from CSV."""
    return pd.read_csv(path)

def save_db(path, df):
    """Save workout database to CSV."""
    df.to_csv(path, index=False)

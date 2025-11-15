import pandas as pd
from exercise_db import load_db, save_db

DB_PATH = "exercise_db.csv"

def get_next_workout():
    """Return last saved workout from CSV."""
    try:
        df = load_db(DB_PATH)
        return df if not df.empty else None
    except FileNotFoundError:
        return None

def save_workout(df):
    """Save the given workout to CSV."""
    save_db(DB_PATH, df)

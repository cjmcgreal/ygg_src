"""Core logic module for processing and editing tasks."""
import streamlit as st
import pandas as pd

def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    for col, values in filters.items():
        df = df[df[col].isin(values)]
    return df

def edit_table_ui(df: pd.DataFrame) -> pd.DataFrame:
    edited_df = df.copy()
    for i, row in df.iterrows():
        with st.expander(f"Edit Task: {row['short_name']}"):
            for col in df.columns:
                new_val = st.text_input(f"{col} (row {i})", value=str(row[col]), key=f"{col}_{i}")
                edited_df.at[i, col] = new_val
    return edited_df

def add_new_task_row(df: pd.DataFrame) -> pd.DataFrame:
    with st.expander("New Task"):
        new_row = {}
        for col in df.columns:
            new_row[col] = st.text_input(f"New {col}", key=f"new_{col}")
        if st.button("Add Task"):
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.success("New task added!")
    return df

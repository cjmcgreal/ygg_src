"""Streamlit frontend for the task viewer app."""
import streamlit as st
import pandas as pd
from task_man_db import read_task_db, write_task_db
from task_man_logic import apply_filters, edit_table_ui, add_new_task_row
from task_man_analysis import get_unique_values, get_visible_columns
from task_man_workflow import process_task_data

st.set_page_config(page_title="Task Viewer", layout="wide")

st.title("📋 Task Viewer Dashboard")

file_path = "sample_tasks.csv"
df = read_task_db(file_path)

with st.sidebar:
    st.header("🔍 Filters")
    unique_values = get_unique_values(df)
    filters = {}
    for col, values in unique_values.items():
        filters[col] = st.multiselect(f"Filter {col}", values, default=values)

all_columns = df.columns.tolist()
hidden_columns = st.sidebar.multiselect("Hide Columns", all_columns, default=[])

visible_columns = get_visible_columns(all_columns, hidden_columns)
filtered_df = apply_filters(df, filters)
visible_df = filtered_df[visible_columns]

st.subheader("🧾 Task Table")
st.dataframe(visible_df, use_container_width=True)

st.subheader("✏️ Edit Tasks")
df = edit_table_ui(df)

st.subheader("➕ Add New Task")
df = add_new_task_row(df)

if st.button("💾 Save Changes"):
    write_task_db(df, file_path)
    st.success("Database updated successfully!")

import streamlit as st
import pandas as pd
from task_man_logic import get_column_filters, apply_filters
from task_man_workflow import load_task_data, save_task_data

def render_task_man_tab(csv_path):

    tab1, tab2 = st.tabs(["Task Display","Other"])

    with tab1:
        # csv_path = "sample_tasks.csv"
        df = load_task_data(csv_path)

        # UI: Filters inside expander
        with st.expander("🔍 Filters and Display Options", expanded=False):
            all_columns = df.columns.tolist()

            selected_columns = st.multiselect("Columns to display:", options=all_columns, default=all_columns)
            column_filters = get_column_filters(df)
            selected_filters = {}

            for col, values in column_filters.items():
                selected = st.multiselect(f"Filter by {col}:", options=values, default=values)
                selected_filters[col] = selected

        # Apply filters
        filtered_df = apply_filters(df, selected_filters)

        # Show editable table
        st.subheader("📋 Task Editor")
        edited_df = st.dataframe(df)
        # edited_df = st.data_editor(df, num_rows="dynamic")
        # edited_df = st.data_editor(filtered_df[selected_columns], num_rows="dynamic")

        # Save Button
        if st.button("💾 Save Changes"):
            save_task_data(edited_df, csv_path)
            st.success("Changes saved.")


if __name__ == "__main__":
    csv_path = 'obsidian_vault_man_edits.csv'

    st.set_page_config(layout="wide")
    render_task_man_tab(csv_path)


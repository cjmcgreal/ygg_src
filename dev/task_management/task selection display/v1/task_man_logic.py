def get_column_filters(df):
    """Return a dictionary of unique values per column for filtering."""
    filters = {}
    for col in df.columns:
        unique_vals = df[col].dropna().unique().tolist()
        if len(unique_vals) < 100:  # Skip filtering for high-cardinality columns
            filters[col] = unique_vals
    return filters

def apply_filters(df, selected_filters):
    """Apply selected filters to the dataframe."""
    filtered_df = df.copy()
    for col, selected_values in selected_filters.items():
        if col in df.columns:
            filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
    return filtered_df

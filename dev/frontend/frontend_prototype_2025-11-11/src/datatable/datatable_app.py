"""
Data Table Focus - Style 2
Interactive table-centric view with filtering, sorting, and detailed data exploration.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime


def render_datatable():
    """
    Render the data table focused style.
    Features: Interactive tables, filtering, sorting, detailed views.
    """
    # Import data functions
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from shared.shared_db import load_transactions
    from shared.shared_analysis import calculate_statistics

    # Load data
    transactions_df = load_transactions()
    stats = calculate_statistics(transactions_df)

    # Header
    st.title("Transaction Data Explorer")
    st.markdown("*Interactive table-focused analysis of all transactions*")
    st.divider()

    # Quick stats bar
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Transactions", stats['total_transactions'])
    col2.metric("Total Income", f"${stats['total_income']:,.0f}")
    col3.metric("Total Expenses", f"${stats['total_expenses']:,.0f}")
    col4.metric("Net Balance", f"${stats['net_balance']:,.0f}")
    col5.metric("Categories", stats['unique_categories'])

    st.divider()

    # Tabs for different table views
    tab1, tab2, tab3, tab4 = st.tabs([
        "All Transactions",
        "Income Only",
        "Expenses Only",
        "Category Summary"
    ])

    with tab1:
        st.subheader("All Transactions")

        # Filters in expandable section
        with st.expander("Filters & Options", expanded=True):
            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:
                # Date range filter
                min_date = transactions_df['date'].min().date()
                max_date = transactions_df['date'].max().date()
                date_range = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )

            with filter_col2:
                # Category filter
                all_categories = sorted(transactions_df['category'].unique().tolist())
                selected_categories = st.multiselect(
                    "Categories",
                    options=all_categories,
                    default=all_categories
                )

            with filter_col3:
                # Transaction type filter
                transaction_types = st.multiselect(
                    "Transaction Type",
                    options=['income', 'expense'],
                    default=['income', 'expense']
                )

            # Amount range filter
            amount_col1, amount_col2 = st.columns(2)
            with amount_col1:
                min_amount = float(transactions_df['amount'].min())
                max_amount = float(transactions_df['amount'].max())
                amount_range = st.slider(
                    "Amount Range",
                    min_value=min_amount,
                    max_value=max_amount,
                    value=(min_amount, max_amount),
                    format="$%.2f"
                )

        # Apply filters
        filtered_df = transactions_df.copy()

        # Date filter
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= date_range[0]) &
                (filtered_df['date'].dt.date <= date_range[1])
            ]

        # Category filter
        if selected_categories:
            filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

        # Type filter
        if transaction_types:
            filtered_df = filtered_df[filtered_df['type'].isin(transaction_types)]

        # Amount filter
        filtered_df = filtered_df[
            (filtered_df['amount'] >= amount_range[0]) &
            (filtered_df['amount'] <= amount_range[1])
        ]

        # Display filtered results count
        st.info(f"Showing {len(filtered_df)} of {len(transactions_df)} transactions")

        # Format dataframe for display
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
        display_df = display_df.sort_values('date', ascending=False)

        # Display table with column configuration
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "transaction_id": st.column_config.TextColumn("ID", width="small"),
                "date": st.column_config.TextColumn("Date", width="medium"),
                "amount": st.column_config.TextColumn("Amount", width="medium"),
                "category": st.column_config.TextColumn("Category", width="medium"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "type": st.column_config.TextColumn("Type", width="small")
            },
            height=400
        )

        # Export option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with tab2:
        st.subheader("Income Transactions")

        income_df = transactions_df[transactions_df['type'] == 'income'].copy()
        income_df = income_df.sort_values('date', ascending=False)

        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Income", f"${income_df['amount'].sum():,.2f}")
        col2.metric("Transactions", len(income_df))
        col3.metric("Average", f"${income_df['amount'].mean():,.2f}")
        col4.metric("Largest", f"${income_df['amount'].max():,.2f}")

        st.markdown("---")

        # Format and display
        display_income = income_df.copy()
        display_income['date'] = display_income['date'].dt.strftime('%Y-%m-%d')
        display_income['amount'] = display_income['amount'].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_income,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Income by category chart
        st.subheader("Income by Category")
        income_by_cat = income_df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        income_by_cat.columns = ['Category', 'Total', 'Count', 'Average']
        income_by_cat = income_by_cat.sort_values('Total', ascending=False)

        fig = px.bar(
            income_by_cat,
            x='Category',
            y='Total',
            title='Total Income by Category',
            color='Count',
            text='Total',
            color_continuous_scale='Greens'
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Expense Transactions")

        expense_df = transactions_df[transactions_df['type'] == 'expense'].copy()
        expense_df = expense_df.sort_values('date', ascending=False)

        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Expenses", f"${abs(expense_df['amount'].sum()):,.2f}")
        col2.metric("Transactions", len(expense_df))
        col3.metric("Average", f"${abs(expense_df['amount'].mean()):,.2f}")
        col4.metric("Largest", f"${abs(expense_df['amount'].min()):,.2f}")

        st.markdown("---")

        # Format and display
        display_expense = expense_df.copy()
        display_expense['date'] = display_expense['date'].dt.strftime('%Y-%m-%d')
        display_expense['amount'] = display_expense['amount'].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_expense,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Expense by category chart
        st.subheader("Expenses by Category")
        expense_by_cat = expense_df.groupby('category')['amount'].agg(['sum', 'count', 'mean']).reset_index()
        expense_by_cat['sum'] = expense_by_cat['sum'].abs()
        expense_by_cat['mean'] = expense_by_cat['mean'].abs()
        expense_by_cat.columns = ['Category', 'Total', 'Count', 'Average']
        expense_by_cat = expense_by_cat.sort_values('Total', ascending=False)

        fig = px.bar(
            expense_by_cat,
            x='Category',
            y='Total',
            title='Total Expenses by Category',
            color='Count',
            text='Total',
            color_continuous_scale='Reds'
        )
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.subheader("Category Summary")

        # Aggregate by category
        category_summary = transactions_df.groupby(['category', 'type']).agg({
            'amount': ['sum', 'count', 'mean', 'min', 'max']
        }).reset_index()

        category_summary.columns = ['Category', 'Type', 'Total', 'Count', 'Average', 'Min', 'Max']
        category_summary['Total'] = category_summary['Total'].apply(lambda x: abs(x))
        category_summary['Average'] = category_summary['Average'].apply(lambda x: abs(x))
        category_summary['Min'] = category_summary['Min'].apply(lambda x: abs(x))
        category_summary['Max'] = category_summary['Max'].apply(lambda x: abs(x))

        # Format for display
        display_cat = category_summary.copy()
        for col in ['Total', 'Average', 'Min', 'Max']:
            display_cat[col] = display_cat[col].apply(lambda x: f"${x:,.2f}")

        st.dataframe(
            display_cat,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        # Category comparison chart
        st.subheader("Category Comparison")
        pivot_data = category_summary.pivot(index='Category', columns='Type', values='Total').fillna(0)

        fig = go.Figure()
        if 'income' in pivot_data.columns:
            fig.add_trace(go.Bar(name='Income', x=pivot_data.index, y=pivot_data['income'], marker_color='green'))
        if 'expense' in pivot_data.columns:
            fig.add_trace(go.Bar(name='Expense', x=pivot_data.index, y=pivot_data['expense'], marker_color='red'))

        fig.update_layout(
            barmode='group',
            title='Income vs Expenses by Category',
            xaxis_title='Category',
            yaxis_title='Amount ($)',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    # Standalone testing
    st.set_page_config(page_title="Data Table Explorer", layout="wide")
    render_datatable()

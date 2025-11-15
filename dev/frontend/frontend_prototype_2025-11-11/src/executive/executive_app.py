"""
Executive Dashboard - Style 1
High-level overview with KPI cards and executive summary charts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


def render_executive():
    """
    Render the executive dashboard style.
    Features: KPI cards, clean charts, high-level overview.
    """
    # Import data functions
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from shared.shared_db import load_transactions
    from shared.shared_analysis import (
        calculate_statistics,
        calculate_monthly_summary,
        calculate_category_totals
    )

    # Load data
    transactions_df = load_transactions()
    stats = calculate_statistics(transactions_df)
    monthly_df = calculate_monthly_summary(transactions_df)
    category_df = calculate_category_totals(transactions_df)

    # Header
    st.title("Executive Financial Dashboard")
    st.markdown("*High-level overview of your financial performance*")
    st.divider()

    # KPI Cards Section
    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Net Balance",
            value=f"${stats['net_balance']:,.2f}",
            delta=f"${stats['net_balance']:,.2f}"
        )

    with col2:
        st.metric(
            label="Total Income",
            value=f"${stats['total_income']:,.2f}",
            delta=f"{stats['income_count']} transactions"
        )

    with col3:
        st.metric(
            label="Total Expenses",
            value=f"${stats['total_expenses']:,.2f}",
            delta=f"-{stats['expense_count']} transactions",
            delta_color="inverse"
        )

    with col4:
        savings_rate = (stats['net_balance'] / stats['total_income'] * 100) if stats['total_income'] > 0 else 0
        st.metric(
            label="Savings Rate",
            value=f"{savings_rate:.1f}%",
            delta=f"{savings_rate:.1f}%"
        )

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Monthly Trends", "Category Breakdown", "Performance Metrics"])

    with tab1:
        st.subheader("Monthly Income vs Expenses")

        # Create monthly trend chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=monthly_df['month'],
            y=monthly_df['income'],
            name='Income',
            marker_color='#2ecc71'
        ))

        fig.add_trace(go.Bar(
            x=monthly_df['month'],
            y=monthly_df['expenses'],
            name='Expenses',
            marker_color='#e74c3c'
        ))

        fig.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['net'],
            name='Net',
            mode='lines+markers',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            barmode='group',
            xaxis_title="Month",
            yaxis_title="Amount ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

        # Monthly summary table
        st.subheader("Monthly Summary Table")
        monthly_display = monthly_df.copy()
        monthly_display['month'] = monthly_display['month'].dt.strftime('%B %Y')
        monthly_display['income'] = monthly_display['income'].apply(lambda x: f"${x:,.2f}")
        monthly_display['expenses'] = monthly_display['expenses'].apply(lambda x: f"${x:,.2f}")
        monthly_display['net'] = monthly_display['net'].apply(lambda x: f"${x:,.2f}")
        monthly_display.columns = ['Month', 'Income', 'Expenses', 'Net', 'Transactions']
        st.dataframe(monthly_display, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Spending by Category")

        # Separate income and expenses
        expense_categories = category_df[category_df['total'] < 0].copy()
        expense_categories['total'] = expense_categories['total'].abs()

        income_categories = category_df[category_df['total'] > 0].copy()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Expense Categories**")
            # Pie chart for expenses
            if len(expense_categories) > 0:
                fig_expense = px.pie(
                    expense_categories,
                    values='total',
                    names='category',
                    title='Expense Distribution',
                    color_discrete_sequence=px.colors.sequential.Reds_r
                )
                fig_expense.update_traces(textposition='inside', textinfo='percent+label')
                fig_expense.update_layout(height=400)
                st.plotly_chart(fig_expense, use_container_width=True)

        with col2:
            st.markdown("**Income Categories**")
            # Pie chart for income
            if len(income_categories) > 0:
                fig_income = px.pie(
                    income_categories,
                    values='total',
                    names='category',
                    title='Income Distribution',
                    color_discrete_sequence=px.colors.sequential.Greens_r
                )
                fig_income.update_traces(textposition='inside', textinfo='percent+label')
                fig_income.update_layout(height=400)
                st.plotly_chart(fig_income, use_container_width=True)

        # Category details table
        st.subheader("Category Details")
        category_display = category_df.copy()
        category_display['total'] = category_display['total'].apply(lambda x: f"${x:,.2f}")
        category_display['average'] = category_display['average'].apply(lambda x: f"${x:,.2f}")
        category_display.columns = ['Category', 'Total', 'Transactions', 'Average']
        st.dataframe(category_display, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Performance Metrics")

        # Performance metrics grid
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.markdown("**Average Metrics**")
            st.write(f"Avg Income per Transaction: **${stats['avg_income']:,.2f}**")
            st.write(f"Avg Expense per Transaction: **${stats['avg_expense']:,.2f}**")
            st.write(f"Total Transactions: **{stats['total_transactions']}**")

        with metric_col2:
            st.markdown("**Transaction Breakdown**")
            st.write(f"Income Transactions: **{stats['income_count']}**")
            st.write(f"Expense Transactions: **{stats['expense_count']}**")
            st.write(f"Unique Categories: **{stats['unique_categories']}**")

        with metric_col3:
            st.markdown("**Extremes**")
            st.write(f"Largest Income: **${stats['largest_income']:,.2f}**")
            st.write(f"Largest Expense: **${stats['largest_expense']:,.2f}**")
            income_expense_ratio = stats['total_income'] / stats['total_expenses'] if stats['total_expenses'] > 0 else 0
            st.write(f"Income/Expense Ratio: **{income_expense_ratio:.2f}**")

        # Monthly transaction count chart
        st.subheader("Monthly Transaction Volume")
        fig_volume = px.bar(
            monthly_df,
            x='month',
            y='transaction_count',
            title='Transactions per Month',
            labels={'transaction_count': 'Number of Transactions', 'month': 'Month'},
            color='transaction_count',
            color_continuous_scale='Blues'
        )
        fig_volume.update_layout(height=350)
        st.plotly_chart(fig_volume, use_container_width=True)


if __name__ == "__main__":
    # Standalone testing
    st.set_page_config(page_title="Executive Dashboard", layout="wide")
    render_executive()

"""
Analytics Lab - Style 3
Advanced visualizations and deep-dive analysis with multiple chart types.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def render_analytics():
    """
    Render the analytics lab style.
    Features: Multiple chart types, statistical analysis, advanced visualizations.
    """
    # Import data functions
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from shared.shared_db import load_transactions
    from shared.shared_analysis import (
        calculate_statistics,
        calculate_monthly_summary,
        calculate_category_totals,
        calculate_daily_balance,
        get_top_transactions
    )

    # Load data
    transactions_df = load_transactions()
    stats = calculate_statistics(transactions_df)
    monthly_df = calculate_monthly_summary(transactions_df)
    category_df = calculate_category_totals(transactions_df)
    daily_balance_df = calculate_daily_balance(transactions_df)

    # Header
    st.title("Financial Analytics Laboratory")
    st.markdown("*Advanced visualizations and statistical analysis*")
    st.divider()

    # Tabs for different analysis types
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Time Series Analysis",
        "Distribution Analysis",
        "Correlation & Patterns",
        "Comparative Analysis",
        "Statistical Deep Dive"
    ])

    with tab1:
        st.subheader("Time Series Analysis")

        # Cumulative balance over time
        st.markdown("**Cumulative Balance Trend**")
        fig_balance = go.Figure()

        fig_balance.add_trace(go.Scatter(
            x=daily_balance_df['date'],
            y=daily_balance_df['cumulative_balance'],
            mode='lines',
            name='Cumulative Balance',
            fill='tozeroy',
            line=dict(color='#3498db', width=2)
        ))

        fig_balance.update_layout(
            xaxis_title="Date",
            yaxis_title="Balance ($)",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig_balance, use_container_width=True)

        # Daily transaction activity
        st.markdown("**Daily Transaction Activity**")
        fig_daily = go.Figure()

        fig_daily.add_trace(go.Bar(
            x=daily_balance_df['date'],
            y=daily_balance_df['daily_total'],
            name='Daily Total',
            marker_color=daily_balance_df['daily_total'].apply(
                lambda x: '#2ecc71' if x > 0 else '#e74c3c'
            )
        ))

        fig_daily.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig_daily, use_container_width=True)

        # Moving average analysis
        st.markdown("**7-Day Moving Average**")
        daily_balance_df['ma_7'] = daily_balance_df['daily_total'].rolling(window=7, min_periods=1).mean()

        fig_ma = go.Figure()

        fig_ma.add_trace(go.Scatter(
            x=daily_balance_df['date'],
            y=daily_balance_df['daily_total'],
            mode='markers',
            name='Daily Total',
            marker=dict(size=4, opacity=0.5)
        ))

        fig_ma.add_trace(go.Scatter(
            x=daily_balance_df['date'],
            y=daily_balance_df['ma_7'],
            mode='lines',
            name='7-Day MA',
            line=dict(color='red', width=3)
        ))

        fig_ma.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            hovermode='x unified',
            height=350
        )

        st.plotly_chart(fig_ma, use_container_width=True)

    with tab2:
        st.subheader("Distribution Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Income distribution histogram
            st.markdown("**Income Distribution**")
            income_data = transactions_df[transactions_df['type'] == 'income']['amount']

            fig_income_hist = px.histogram(
                income_data,
                nbins=20,
                title='Income Amount Distribution',
                labels={'value': 'Amount ($)', 'count': 'Frequency'},
                color_discrete_sequence=['#2ecc71']
            )
            fig_income_hist.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_income_hist, use_container_width=True)

        with col2:
            # Expense distribution histogram
            st.markdown("**Expense Distribution**")
            expense_data = transactions_df[transactions_df['type'] == 'expense']['amount'].abs()

            fig_expense_hist = px.histogram(
                expense_data,
                nbins=20,
                title='Expense Amount Distribution',
                labels={'value': 'Amount ($)', 'count': 'Frequency'},
                color_discrete_sequence=['#e74c3c']
            )
            fig_expense_hist.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_expense_hist, use_container_width=True)

        # Box plot comparison
        st.markdown("**Amount Distribution by Category**")

        # Prepare data for box plot
        expense_categories = transactions_df[transactions_df['type'] == 'expense'].copy()
        expense_categories['amount'] = expense_categories['amount'].abs()

        fig_box = px.box(
            expense_categories,
            x='category',
            y='amount',
            title='Expense Amount Distribution by Category',
            color='category',
            points='all'
        )
        fig_box.update_layout(height=400, showlegend=False)
        fig_box.update_xaxes(tickangle=45)
        st.plotly_chart(fig_box, use_container_width=True)

        # Violin plot
        st.markdown("**Transaction Density by Type**")
        plot_data = transactions_df.copy()
        plot_data['amount'] = plot_data['amount'].abs()

        fig_violin = px.violin(
            plot_data,
            x='type',
            y='amount',
            title='Transaction Amount Density',
            box=True,
            points='all',
            color='type',
            color_discrete_map={'income': '#2ecc71', 'expense': '#e74c3c'}
        )
        fig_violin.update_layout(height=400)
        st.plotly_chart(fig_violin, use_container_width=True)

    with tab3:
        st.subheader("Correlation & Patterns")

        # Day of week analysis
        st.markdown("**Transaction Patterns by Day of Week**")
        transactions_df['day_of_week'] = transactions_df['date'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        dow_analysis = transactions_df.groupby(['day_of_week', 'type']).agg({
            'amount': ['count', 'sum']
        }).reset_index()
        dow_analysis.columns = ['day_of_week', 'type', 'count', 'sum']
        dow_analysis['sum'] = dow_analysis['sum'].abs()

        # Create subplots
        fig_dow = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Transaction Count by Day', 'Transaction Amount by Day')
        )

        for trans_type in ['income', 'expense']:
            data = dow_analysis[dow_analysis['type'] == trans_type]
            # Reorder by day of week
            data['day_order'] = data['day_of_week'].map({day: i for i, day in enumerate(day_order)})
            data = data.sort_values('day_order')

            color = '#2ecc71' if trans_type == 'income' else '#e74c3c'

            fig_dow.add_trace(
                go.Bar(name=trans_type.capitalize(), x=data['day_of_week'], y=data['count'], marker_color=color),
                row=1, col=1
            )

            fig_dow.add_trace(
                go.Bar(name=trans_type.capitalize(), x=data['day_of_week'], y=data['sum'], marker_color=color, showlegend=False),
                row=1, col=2
            )

        fig_dow.update_layout(height=400, barmode='group')
        st.plotly_chart(fig_dow, use_container_width=True)

        # Heatmap of transactions by day and category
        st.markdown("**Transaction Heatmap: Day of Week vs Category**")

        # Create pivot table
        heatmap_data = transactions_df.groupby(['day_of_week', 'category']).size().reset_index(name='count')
        pivot_heatmap = heatmap_data.pivot(index='day_of_week', columns='category', values='count').fillna(0)

        # Reorder by day of week
        pivot_heatmap = pivot_heatmap.reindex(day_order)

        fig_heatmap = px.imshow(
            pivot_heatmap,
            labels=dict(x="Category", y="Day of Week", color="Count"),
            aspect="auto",
            color_continuous_scale='YlOrRd',
            title='Transaction Frequency Heatmap'
        )
        fig_heatmap.update_layout(height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    with tab4:
        st.subheader("Comparative Analysis")

        # Month-over-month comparison
        st.markdown("**Month-over-Month Growth**")

        monthly_df['income_growth'] = monthly_df['income'].pct_change() * 100
        monthly_df['expense_growth'] = monthly_df['expenses'].pct_change() * 100

        fig_growth = go.Figure()

        fig_growth.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['income_growth'],
            mode='lines+markers',
            name='Income Growth %',
            line=dict(color='#2ecc71', width=2),
            marker=dict(size=8)
        ))

        fig_growth.add_trace(go.Scatter(
            x=monthly_df['month'],
            y=monthly_df['expense_growth'],
            mode='lines+markers',
            name='Expense Growth %',
            line=dict(color='#e74c3c', width=2),
            marker=dict(size=8)
        ))

        fig_growth.add_hline(y=0, line_dash="dash", line_color="gray")

        fig_growth.update_layout(
            xaxis_title="Month",
            yaxis_title="Growth Rate (%)",
            hovermode='x unified',
            height=400
        )

        st.plotly_chart(fig_growth, use_container_width=True)

        # Category comparison - Top 5 expenses
        st.markdown("**Top 5 Expense Categories - Monthly Trend**")

        expense_df = transactions_df[transactions_df['type'] == 'expense'].copy()
        top_5_categories = expense_df.groupby('category')['amount'].sum().abs().nlargest(5).index

        expense_df['month'] = expense_df['date'].dt.to_period('M').dt.to_timestamp()
        expense_df['amount'] = expense_df['amount'].abs()

        monthly_by_cat = expense_df[expense_df['category'].isin(top_5_categories)].groupby(
            ['month', 'category']
        )['amount'].sum().reset_index()

        fig_cat_trend = px.line(
            monthly_by_cat,
            x='month',
            y='amount',
            color='category',
            markers=True,
            title='Top 5 Expense Categories Over Time'
        )
        fig_cat_trend.update_layout(height=400)
        st.plotly_chart(fig_cat_trend, use_container_width=True)

        # Sunburst chart
        st.markdown("**Hierarchical View: Type → Category**")

        sunburst_data = transactions_df.copy()
        sunburst_data['amount'] = sunburst_data['amount'].abs()

        fig_sunburst = px.sunburst(
            sunburst_data,
            path=['type', 'category'],
            values='amount',
            title='Transaction Hierarchy',
            color='type',
            color_discrete_map={'income': '#2ecc71', 'expense': '#e74c3c'}
        )
        fig_sunburst.update_layout(height=500)
        st.plotly_chart(fig_sunburst, use_container_width=True)

    with tab5:
        st.subheader("Statistical Deep Dive")

        # Statistical summary
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Income Statistics**")
            income_stats = transactions_df[transactions_df['type'] == 'income']['amount'].describe()
            st.dataframe(income_stats.apply(lambda x: f"${x:,.2f}"), use_container_width=True)

        with col2:
            st.markdown("**Expense Statistics**")
            expense_stats = transactions_df[transactions_df['type'] == 'expense']['amount'].abs().describe()
            st.dataframe(expense_stats.apply(lambda x: f"${x:,.2f}"), use_container_width=True)

        # Percentile analysis
        st.markdown("**Transaction Amount Percentiles**")

        percentiles = [10, 25, 50, 75, 90, 95, 99]
        income_percentiles = np.percentile(
            transactions_df[transactions_df['type'] == 'income']['amount'],
            percentiles
        )
        expense_percentiles = np.percentile(
            transactions_df[transactions_df['type'] == 'expense']['amount'].abs(),
            percentiles
        )

        percentile_df = pd.DataFrame({
            'Percentile': [f"{p}th" for p in percentiles],
            'Income': [f"${v:,.2f}" for v in income_percentiles],
            'Expense': [f"${v:,.2f}" for v in expense_percentiles]
        })

        st.dataframe(percentile_df, use_container_width=True, hide_index=True)

        # Top transactions tables
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Top 10 Income Transactions**")
            top_income = get_top_transactions(transactions_df, n=10, transaction_type='income')
            display_income = top_income[['date', 'category', 'amount']].copy()
            display_income['date'] = display_income['date'].dt.strftime('%Y-%m-%d')
            display_income['amount'] = display_income['amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_income, use_container_width=True, hide_index=True, height=300)

        with col2:
            st.markdown("**Top 10 Expense Transactions**")
            top_expenses = get_top_transactions(transactions_df, n=10, transaction_type='expense')
            display_expense = top_expenses[['date', 'category', 'amount']].copy()
            display_expense['date'] = display_expense['date'].dt.strftime('%Y-%m-%d')
            display_expense['amount'] = display_expense['amount'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(display_expense, use_container_width=True, hide_index=True, height=300)


if __name__ == "__main__":
    # Standalone testing
    st.set_page_config(page_title="Analytics Lab", layout="wide")
    render_analytics()

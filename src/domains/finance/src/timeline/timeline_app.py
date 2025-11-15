"""
Timeline Explorer - Style 5
Chronological focus with timeline visualizations and date-centric navigation.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render_timeline():
    """
    Render the timeline explorer style.
    Features: Timeline views, chronological navigation, date-focused analysis.
    """
    # Import data functions
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from shared.shared_db import load_transactions
    from shared.shared_analysis import (
        calculate_statistics,
        calculate_daily_balance,
        get_top_transactions
    )

    # Load data
    transactions_df = load_transactions()
    stats = calculate_statistics(transactions_df)
    daily_balance_df = calculate_daily_balance(transactions_df)

    # Header
    st.title("Financial Timeline Explorer")
    st.markdown("*Navigate your finances through time*")
    st.divider()

    # Quick stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Period Start", transactions_df['date'].min().strftime('%b %d, %Y'))
    col2.metric("Period End", transactions_df['date'].max().strftime('%b %d, %Y'))
    col3.metric("Days Active", (transactions_df['date'].max() - transactions_df['date'].min()).days)

    st.divider()

    # Tabs for different timeline views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Interactive Timeline",
        "Calendar View",
        "Weekly Breakdown",
        "Event Stream"
    ])

    with tab1:
        st.subheader("Interactive Transaction Timeline")

        # Timeline scatter plot
        timeline_df = transactions_df.copy()
        timeline_df['amount_abs'] = timeline_df['amount'].abs()
        timeline_df['color'] = timeline_df['type'].map({'income': '#27ae60', 'expense': '#e74c3c'})

        fig_timeline = go.Figure()

        # Add income transactions
        income_data = timeline_df[timeline_df['type'] == 'income']
        fig_timeline.add_trace(go.Scatter(
            x=income_data['date'],
            y=income_data['amount'],
            mode='markers',
            name='Income',
            marker=dict(
                size=income_data['amount_abs'] / 50,
                color='#27ae60',
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            text=income_data.apply(lambda row: f"{row['category']}<br>${row['amount']:,.2f}", axis=1),
            hovertemplate='%{text}<extra></extra>'
        ))

        # Add expense transactions
        expense_data = timeline_df[timeline_df['type'] == 'expense']
        fig_timeline.add_trace(go.Scatter(
            x=expense_data['date'],
            y=expense_data['amount'],
            mode='markers',
            name='Expense',
            marker=dict(
                size=expense_data['amount_abs'] / 50,
                color='#e74c3c',
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            text=expense_data.apply(lambda row: f"{row['category']}<br>${row['amount']:,.2f}", axis=1),
            hovertemplate='%{text}<extra></extra>'
        ))

        fig_timeline.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Amount ($)",
            height=450,
            hovermode='closest',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig_timeline, use_container_width=True)

        # Balance timeline
        st.subheader("Cumulative Balance Timeline")

        fig_balance = go.Figure()

        fig_balance.add_trace(go.Scatter(
            x=daily_balance_df['date'],
            y=daily_balance_df['cumulative_balance'],
            mode='lines',
            fill='tozeroy',
            line=dict(color='#3498db', width=2),
            fillcolor='rgba(52, 152, 219, 0.2)',
            hovertemplate='%{x|%b %d, %Y}<br>$%{y:,.2f}<extra></extra>'
        ))

        # Mark significant events (large transactions)
        top_income = get_top_transactions(transactions_df, n=3, transaction_type='income')
        top_expense = get_top_transactions(transactions_df, n=3, transaction_type='expense')

        for _, row in top_income.iterrows():
            balance_at_date = daily_balance_df[daily_balance_df['date'] <= row['date']]['cumulative_balance'].iloc[-1]
            fig_balance.add_annotation(
                x=row['date'],
                y=balance_at_date,
                text=f"Income: ${row['amount']:,.0f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='#27ae60',
                bgcolor='#27ae60',
                font=dict(color='white', size=10),
                opacity=0.8
            )

        for _, row in top_expense.iterrows():
            balance_at_date = daily_balance_df[daily_balance_df['date'] <= row['date']]['cumulative_balance'].iloc[-1]
            fig_balance.add_annotation(
                x=row['date'],
                y=balance_at_date,
                text=f"Expense: ${row['amount']:,.0f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='#e74c3c',
                bgcolor='#e74c3c',
                font=dict(color='white', size=10),
                opacity=0.8
            )

        fig_balance.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Balance ($)",
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig_balance, use_container_width=True)

    with tab2:
        st.subheader("Calendar Heatmap View")

        # Prepare calendar data
        calendar_df = transactions_df.copy()
        calendar_df['date_only'] = calendar_df['date'].dt.date
        daily_summary = calendar_df.groupby('date_only').agg({
            'amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        daily_summary.columns = ['date', 'net_amount', 'count']

        # Add week and day of week info
        daily_summary['date'] = pd.to_datetime(daily_summary['date'])
        daily_summary['week'] = daily_summary['date'].dt.isocalendar().week
        daily_summary['day_of_week'] = daily_summary['date'].dt.dayofweek
        daily_summary['day_name'] = daily_summary['date'].dt.day_name()

        # Create heatmap
        st.markdown("**Daily Net Amount Heatmap**")

        # Get unique weeks
        unique_weeks = sorted(daily_summary['week'].unique())
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Create matrix for heatmap
        heatmap_matrix = []
        hover_text = []

        for week in unique_weeks:
            week_data = daily_summary[daily_summary['week'] == week]
            week_row = []
            hover_row = []

            for day in range(7):
                day_data = week_data[week_data['day_of_week'] == day]
                if len(day_data) > 0:
                    week_row.append(day_data['net_amount'].iloc[0])
                    hover_row.append(
                        f"{day_data['date'].iloc[0].strftime('%b %d')}<br>"
                        f"Net: ${day_data['net_amount'].iloc[0]:,.2f}<br>"
                        f"Transactions: {day_data['count'].iloc[0]}"
                    )
                else:
                    week_row.append(None)
                    hover_row.append("")

            heatmap_matrix.append(week_row)
            hover_text.append(hover_row)

        fig_calendar = go.Figure(data=go.Heatmap(
            z=heatmap_matrix,
            x=day_names,
            y=[f"Week {w}" for w in unique_weeks],
            hovertext=hover_text,
            hovertemplate='%{hovertext}<extra></extra>',
            colorscale=[
                [0, '#e74c3c'],
                [0.5, '#f8f9fa'],
                [1, '#27ae60']
            ],
            zmid=0,
            colorbar=dict(title="Net Amount ($)")
        ))

        fig_calendar.update_layout(
            title="Daily Net Amount by Week",
            xaxis_title="Day of Week",
            yaxis_title="Week",
            height=400
        )

        st.plotly_chart(fig_calendar, use_container_width=True)

        # Monthly calendar view
        st.markdown("**Transaction Activity by Month**")

        monthly_activity = transactions_df.copy()
        monthly_activity['month'] = monthly_activity['date'].dt.to_period('M')
        monthly_activity['day'] = monthly_activity['date'].dt.day

        activity_summary = monthly_activity.groupby(['month', 'day']).size().reset_index(name='count')
        activity_summary['month'] = activity_summary['month'].astype(str)

        fig_month_activity = px.density_heatmap(
            activity_summary,
            x='day',
            y='month',
            z='count',
            title='Transaction Frequency by Day of Month',
            labels={'day': 'Day of Month', 'month': 'Month', 'count': 'Transactions'},
            color_continuous_scale='Blues'
        )
        fig_month_activity.update_layout(height=400)
        st.plotly_chart(fig_month_activity, use_container_width=True)

    with tab3:
        st.subheader("Weekly Breakdown")

        # Weekly aggregation
        weekly_df = transactions_df.copy()
        weekly_df['week'] = weekly_df['date'].dt.to_period('W').apply(lambda r: r.start_time)

        weekly_summary = weekly_df.groupby('week').agg({
            'amount': 'sum',
            'transaction_id': 'count'
        }).reset_index()
        weekly_summary.columns = ['week', 'net', 'count']

        # Separate income and expenses by week
        weekly_income = weekly_df[weekly_df['type'] == 'income'].groupby('week')['amount'].sum().reset_index()
        weekly_income.columns = ['week', 'income']

        weekly_expense = weekly_df[weekly_df['type'] == 'expense'].groupby('week')['amount'].sum().abs().reset_index()
        weekly_expense.columns = ['week', 'expense']

        # Merge
        weekly_full = weekly_summary.merge(weekly_income, on='week', how='left')
        weekly_full = weekly_full.merge(weekly_expense, on='week', how='left')
        weekly_full = weekly_full.fillna(0)

        # Chart
        fig_weekly = go.Figure()

        fig_weekly.add_trace(go.Bar(
            x=weekly_full['week'],
            y=weekly_full['income'],
            name='Income',
            marker_color='#27ae60'
        ))

        fig_weekly.add_trace(go.Bar(
            x=weekly_full['week'],
            y=weekly_full['expense'],
            name='Expense',
            marker_color='#e74c3c'
        ))

        fig_weekly.add_trace(go.Scatter(
            x=weekly_full['week'],
            y=weekly_full['net'],
            name='Net',
            mode='lines+markers',
            line=dict(color='#3498db', width=3),
            marker=dict(size=10)
        ))

        fig_weekly.update_layout(
            barmode='group',
            xaxis_title="Week Starting",
            yaxis_title="Amount ($)",
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig_weekly, use_container_width=True)

        # Weekly summary table
        st.markdown("**Weekly Summary Table**")
        weekly_display = weekly_full.copy()
        weekly_display['week'] = weekly_display['week'].dt.strftime('%b %d, %Y')
        weekly_display['income'] = weekly_display['income'].apply(lambda x: f"${x:,.2f}")
        weekly_display['expense'] = weekly_display['expense'].apply(lambda x: f"${x:,.2f}")
        weekly_display['net'] = weekly_display['net'].apply(lambda x: f"${x:,.2f}")
        weekly_display.columns = ['Week Starting', 'Net', 'Transactions', 'Income', 'Expense']

        st.dataframe(
            weekly_display[['Week Starting', 'Income', 'Expense', 'Net', 'Transactions']],
            use_container_width=True,
            hide_index=True,
            height=300
        )

    with tab4:
        st.subheader("Event Stream")

        # Chronological list of all transactions
        st.markdown("**All Transactions in Chronological Order**")

        # Date range selector
        min_date = transactions_df['date'].min().date()
        max_date = transactions_df['date'].max().date()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

        # Filter transactions
        stream_df = transactions_df[
            (transactions_df['date'].dt.date >= start_date) &
            (transactions_df['date'].dt.date <= end_date)
        ].copy()

        stream_df = stream_df.sort_values('date', ascending=False)

        st.info(f"Showing {len(stream_df)} transactions from {start_date} to {end_date}")

        # Display as event stream with custom formatting
        for _, row in stream_df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 3, 2, 2])

            with col1:
                st.text(row['date'].strftime('%b %d, %Y'))

            with col2:
                st.text(f"{row['category']} - {row['description']}")

            with col3:
                if row['type'] == 'income':
                    st.markdown(f"<span style='color: #27ae60; font-weight: bold;'>${row['amount']:,.2f}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #e74c3c; font-weight: bold;'>${row['amount']:,.2f}</span>", unsafe_allow_html=True)

            with col4:
                badge_color = '#27ae60' if row['type'] == 'income' else '#e74c3c'
                st.markdown(f"<span style='background-color: {badge_color}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px;'>{row['type'].upper()}</span>", unsafe_allow_html=True)

            st.markdown("---")


if __name__ == "__main__":
    # Standalone testing
    st.set_page_config(page_title="Timeline Explorer", layout="wide")
    render_timeline()

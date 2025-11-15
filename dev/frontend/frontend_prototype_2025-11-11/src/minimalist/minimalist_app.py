"""
Minimalist View - Style 4
Clean, simple interface with focus on essential information only.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render_minimalist():
    """
    Render the minimalist style.
    Features: Clean design, essential information, minimal clutter.
    """
    # Import data functions
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

    from shared.shared_db import load_transactions
    from shared.shared_analysis import (
        calculate_statistics,
        calculate_monthly_summary,
        calculate_daily_balance
    )

    # Load data
    transactions_df = load_transactions()
    stats = calculate_statistics(transactions_df)
    monthly_df = calculate_monthly_summary(transactions_df)
    daily_balance_df = calculate_daily_balance(transactions_df)

    # Minimalist header
    st.title("Financial Overview")
    st.caption("Simple. Clear. Essential.")

    st.markdown("")
    st.markdown("")

    # Key number - Balance
    st.markdown(f"<h1 style='text-align: center; color: #2c3e50;'>${stats['net_balance']:,.2f}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #7f8c8d; font-size: 18px;'>Current Balance</p>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("---")
    st.markdown("")

    # Tabs - minimal design
    tab1, tab2, tab3 = st.tabs(["Summary", "Trends", "Details"])

    with tab1:
        st.markdown("")

        # Simple two-column layout
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Income")
            st.markdown(f"<h2 style='color: #27ae60;'>${stats['total_income']:,.2f}</h2>", unsafe_allow_html=True)
            st.caption(f"{stats['income_count']} transactions")
            st.caption(f"Average: ${stats['avg_income']:,.2f}")

            st.markdown("")
            st.markdown("")

            # Top income categories
            income_cats = transactions_df[transactions_df['type'] == 'income'].groupby('category')['amount'].sum().sort_values(ascending=False).head(3)
            st.markdown("**Top Sources**")
            for cat, amount in income_cats.items():
                st.text(f"{cat}: ${amount:,.2f}")

        with col2:
            st.markdown("### Expenses")
            st.markdown(f"<h2 style='color: #e74c3c;'>${stats['total_expenses']:,.2f}</h2>", unsafe_allow_html=True)
            st.caption(f"{stats['expense_count']} transactions")
            st.caption(f"Average: ${stats['avg_expense']:,.2f}")

            st.markdown("")
            st.markdown("")

            # Top expense categories
            expense_cats = transactions_df[transactions_df['type'] == 'expense'].groupby('category')['amount'].sum().abs().sort_values(ascending=False).head(3)
            st.markdown("**Top Categories**")
            for cat, amount in expense_cats.items():
                st.text(f"{cat}: ${amount:,.2f}")

        st.markdown("")
        st.markdown("---")
        st.markdown("")

        # Simple savings rate indicator
        savings_rate = (stats['net_balance'] / stats['total_income'] * 100) if stats['total_income'] > 0 else 0

        st.markdown("### Savings Rate")
        st.progress(min(savings_rate / 100, 1.0))
        st.caption(f"{savings_rate:.1f}% of income saved")

    with tab2:
        st.markdown("")

        # Clean line chart for balance
        st.markdown("### Balance Over Time")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=daily_balance_df['date'],
            y=daily_balance_df['cumulative_balance'],
            mode='lines',
            line=dict(color='#3498db', width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)',
            hovertemplate='%{y:$,.2f}<extra></extra>'
        ))

        fig.update_layout(
            xaxis_title="",
            yaxis_title="Balance",
            showlegend=False,
            height=350,
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#2c3e50')
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#ecf0f1')

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("")
        st.markdown("")

        # Simple monthly bars
        st.markdown("### Monthly Net Income")

        fig_monthly = go.Figure()

        colors = ['#27ae60' if x > 0 else '#e74c3c' for x in monthly_df['net']]

        fig_monthly.add_trace(go.Bar(
            x=monthly_df['month'],
            y=monthly_df['net'],
            marker_color=colors,
            hovertemplate='%{y:$,.2f}<extra></extra>'
        ))

        fig_monthly.update_layout(
            xaxis_title="",
            yaxis_title="Net",
            showlegend=False,
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color='#2c3e50')
        )

        fig_monthly.update_xaxes(showgrid=False)
        fig_monthly.update_yaxes(showgrid=True, gridcolor='#ecf0f1')

        st.plotly_chart(fig_monthly, use_container_width=True)

    with tab3:
        st.markdown("")

        # Recent transactions - clean table
        st.markdown("### Recent Transactions")

        recent = transactions_df.sort_values('date', ascending=False).head(15).copy()
        recent['Date'] = recent['date'].dt.strftime('%b %d')
        recent['Amount'] = recent['amount'].apply(lambda x: f"${x:,.2f}")

        # Simple display
        display_recent = recent[['Date', 'Category', 'Amount', 'Type']].copy()
        display_recent['Type'] = display_recent['Type'].str.capitalize()

        st.dataframe(
            display_recent,
            use_container_width=True,
            hide_index=True,
            height=400
        )

        st.markdown("")
        st.markdown("")

        # Monthly breakdown - simple table
        st.markdown("### Monthly Breakdown")

        monthly_display = monthly_df.copy()
        monthly_display['Month'] = monthly_display['month'].dt.strftime('%B')
        monthly_display['Income'] = monthly_display['income'].apply(lambda x: f"${x:,.0f}")
        monthly_display['Expenses'] = monthly_display['expenses'].apply(lambda x: f"${x:,.0f}")
        monthly_display['Net'] = monthly_display['net'].apply(lambda x: f"${x:,.0f}")

        st.dataframe(
            monthly_display[['Month', 'Income', 'Expenses', 'Net']],
            use_container_width=True,
            hide_index=True,
            height=300
        )


if __name__ == "__main__":
    # Standalone testing
    st.set_page_config(page_title="Minimalist View", layout="wide")
    render_minimalist()

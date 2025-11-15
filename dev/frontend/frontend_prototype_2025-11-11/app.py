"""
Main Application Entry Point
Provides a sidebar to select between different frontend styles.
"""

import streamlit as st

# Import all style renderers
from src.executive.executive_app import render_executive
from src.datatable.datatable_app import render_datatable
from src.analytics.analytics_app import render_analytics
from src.minimalist.minimalist_app import render_minimalist
from src.timeline.timeline_app import render_timeline


def main():
    """
    Main application function with tab-based style selector.
    """
    # Page configuration
    st.set_page_config(
        page_title="Financial Dashboard Prototype",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Header
    st.title("Financial Dashboard Prototype")
    st.caption("All styles use the same underlying dataset of 100 financial transactions.")
    st.markdown("")

    # Main tabs for different dashboard styles
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Dashboard",
        "📋 Data Table Focus",
        "📈 Analytics Lab",
        "✨ Minimalist View",
        "📅 Timeline Explorer"
    ])

    with tab1:
        st.markdown("")
        st.caption("High-level overview with KPI cards and executive summary charts. Perfect for quick insights and management reporting.")
        render_executive()

    with tab2:
        st.markdown("")
        st.caption("Interactive table-centric view with advanced filtering and sorting. Ideal for detailed data exploration and export.")
        render_datatable()

    with tab3:
        st.markdown("")
        st.caption("Advanced visualizations and statistical analysis. For deep-dive analysis with multiple chart types and patterns.")
        render_analytics()

    with tab4:
        st.markdown("")
        st.caption("Clean, simple interface with essential information only. Focus on clarity and ease of understanding.")
        render_minimalist()

    with tab5:
        st.markdown("")
        st.caption("Chronological focus with timeline visualizations. Navigate your finances through time with calendar and event views.")
        render_timeline()


if __name__ == "__main__":
    main()

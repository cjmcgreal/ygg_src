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
    Main application function with sidebar style selector.
    """
    # Page configuration
    st.set_page_config(
        page_title="Financial Dashboard Prototype",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar for style selection
    with st.sidebar:
        st.title("Dashboard Styles")
        st.markdown("Choose a frontend style to explore:")
        st.markdown("---")

        # Style selector
        selected_style = st.radio(
            "Select Style:",
            options=[
                "Executive Dashboard",
                "Data Table Focus",
                "Analytics Lab",
                "Minimalist View",
                "Timeline Explorer"
            ],
            index=0
        )

        st.markdown("---")

        # Style descriptions
        st.markdown("### Style Descriptions")

        if selected_style == "Executive Dashboard":
            st.info(
                "**Executive Dashboard**\n\n"
                "High-level overview with KPI cards and executive summary charts. "
                "Perfect for quick insights and management reporting."
            )
        elif selected_style == "Data Table Focus":
            st.info(
                "**Data Table Focus**\n\n"
                "Interactive table-centric view with advanced filtering and sorting. "
                "Ideal for detailed data exploration and export."
            )
        elif selected_style == "Analytics Lab":
            st.info(
                "**Analytics Lab**\n\n"
                "Advanced visualizations and statistical analysis. "
                "For deep-dive analysis with multiple chart types and patterns."
            )
        elif selected_style == "Minimalist View":
            st.info(
                "**Minimalist View**\n\n"
                "Clean, simple interface with essential information only. "
                "Focus on clarity and ease of understanding."
            )
        elif selected_style == "Timeline Explorer":
            st.info(
                "**Timeline Explorer**\n\n"
                "Chronological focus with timeline visualizations. "
                "Navigate your finances through time with calendar and event views."
            )

        st.markdown("---")
        st.caption("All styles use the same underlying dataset of 100 financial transactions.")

    # Render selected style
    if selected_style == "Executive Dashboard":
        render_executive()
    elif selected_style == "Data Table Focus":
        render_datatable()
    elif selected_style == "Analytics Lab":
        render_analytics()
    elif selected_style == "Minimalist View":
        render_minimalist()
    elif selected_style == "Timeline Explorer":
        render_timeline()


if __name__ == "__main__":
    main()

"""
Finance App - Integration wrapper for prod environment

This file acts as the integration point between the prod app structure
and the existing finance module.
"""
import sys
import os

# Add the domains/finance directory to Python path so modules can import each other
finance_dir = os.path.dirname(os.path.abspath(__file__))
if finance_dir not in sys.path:
    sys.path.insert(0, finance_dir)

# Import the main function from app.py and create a render function
from app import main as finance_main


def render_finance_app():
    """
    Render the finance domain app.

    This wrapper calls the main() function from app.py which handles
    all the tab-based navigation and rendering.
    """
    # Call the main finance app function
    # Note: We skip the set_page_config since that's handled by the page file

    # Import all style renderers directly
    from src.executive.executive_app import render_executive
    from src.datatable.datatable_app import render_datatable
    from src.analytics.analytics_app import render_analytics
    from src.minimalist.minimalist_app import render_minimalist
    from src.timeline.timeline_app import render_timeline

    import streamlit as st

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


# Export the render function for use by the main app.py
__all__ = ['render_finance_app']


if __name__ == "__main__":
    # Standalone test
    print("Finance App - Integration Wrapper")
    print("=" * 50)
    print("This wrapper integrates the finance module into the prod environment")
    print("Run the main app.py to see the full integrated UI")
    print("\nTo test: streamlit run ../../app.py")

"""
Streamlit UI for timeseries visualization tool.
Provides interactive interface for exploring and plotting timeseries data.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import List, Dict

# Import workflow layer
from . import timeseries_workflow as workflow
from . import timeseries_logic as logic


def initialize_session_state():
    """
    Initialize Streamlit session state with default values.
    This ensures state persists across reruns.
    """
    if 'app_initialized' not in st.session_state:
        # Load initial app state from workflow
        app_state = workflow.initialize_app()

        # Store in session state
        st.session_state.hierarchy = app_state['hierarchy']
        st.session_state.all_channels = app_state['all_channels']
        st.session_state.min_date = app_state['min_date']
        st.session_state.max_date = app_state['max_date']
        st.session_state.bucket_options = app_state['bucket_options']
        st.session_state.plot_types = app_state['plot_types']
        st.session_state.bar_modes = app_state['bar_modes']
        st.session_state.agg_methods = app_state['agg_methods']

        # Initialize user selections
        st.session_state.selected_channels = []
        st.session_state.app_initialized = True


def flatten_hierarchy(hierarchy: dict, path: str = "", result: list = None) -> list:
    """
    Flatten the hierarchical structure into a list of (path, channel_info) tuples.

    Args:
        hierarchy (dict): Nested hierarchy dictionary
        path (str): Current path in hierarchy
        result (list): Accumulated results

    Returns:
        list: List of (full_path, channel_info) tuples
    """
    if result is None:
        result = []

    for key, value in hierarchy.items():
        current_path = f"{path}/{key}" if path else key

        # Check if this is a leaf node (contains 'channel' key)
        if isinstance(value, dict) and 'channel' in value:
            # Add leaf node to results
            result.append((current_path, value))
        else:
            # Recurse into branch
            flatten_hierarchy(value, current_path, result)

    return result


def render_channel_tree(hierarchy: dict):
    """
    Render hierarchical channel navigation tree with add buttons.
    Uses a flat list with path display to avoid nested expanders.

    Args:
        hierarchy (dict): Nested hierarchy dictionary
    """
    # Flatten the hierarchy
    flat_channels = flatten_hierarchy(hierarchy)

    # Group by top-level category for better organization
    categories = {}
    for path, info in flat_channels:
        top_level = path.split('/')[0]
        if top_level not in categories:
            categories[top_level] = []
        categories[top_level].append((path, info))

    # Render each category in its own expander
    for category, channels in categories.items():
        with st.expander(f"📁 {category}", expanded=True):
            for path, info in channels:
                # Remove top-level from display path
                display_path = '/'.join(path.split('/')[1:])

                col1, col2 = st.columns([3, 1])

                with col1:
                    # Show the full path and unit
                    st.markdown(f"**{display_path}** `{info['unit']}`")

                with col2:
                    # Check if already added
                    if info['channel'] in st.session_state.selected_channels:
                        st.caption("✓")
                    else:
                        # Add button
                        button_key = f"add_{info['channel']}"
                        if st.button("➕", key=button_key, help=f"Add {display_path}"):
                            success, updated, msg = workflow.add_channel_to_plot(
                                st.session_state.selected_channels,
                                info['channel']
                            )
                            if success:
                                st.session_state.selected_channels = updated
                                st.rerun()
                            else:
                                st.error(msg)


def render_selected_channels():
    """
    Render the list of currently selected channels with remove buttons.
    """
    if not st.session_state.selected_channels:
        st.info("No channels selected. Add channels from the tree on the left.")
        return

    st.markdown("### Selected Channels")

    for channel in st.session_state.selected_channels:
        col1, col2 = st.columns([4, 1])

        with col1:
            # Get metadata for display
            metadata = workflow.get_channel_metadata(channel)
            if metadata:
                label = logic.format_channel_label(channel, metadata)
                st.markdown(f"• {label}")
            else:
                st.markdown(f"• {channel}")

        with col2:
            # Remove button
            if st.button("✖", key=f"remove_{channel}", help=f"Remove {channel}"):
                success, updated, msg = workflow.remove_channel_from_plot(
                    st.session_state.selected_channels,
                    channel
                )
                if success:
                    st.session_state.selected_channels = updated
                    st.rerun()

    # Clear all button
    if st.button("🗑️ Clear All", type="secondary"):
        success, updated, msg = workflow.clear_all_channels(
            st.session_state.selected_channels
        )
        if success:
            st.session_state.selected_channels = updated
            st.rerun()


def create_plot(plot_data, channels, plot_type, bar_mode):
    """
    Create Plotly chart based on data and settings.

    Args:
        plot_data: DataFrame with plot data
        channels: List of channel names
        plot_type: Type of plot
        bar_mode: Bar chart mode (for bar charts)

    Returns:
        plotly.graph_objects.Figure: The plot figure
    """
    fig = go.Figure()

    # Get colors for channels
    colors = logic.get_color_palette(len(channels))

    # Get plot configuration
    config = logic.get_plot_config(plot_type, bar_mode)

    # Create traces based on plot type
    for i, channel in enumerate(channels):
        if channel not in plot_data.columns:
            continue

        # Get metadata for label
        metadata = workflow.get_channel_metadata(channel)
        label = logic.format_channel_label(channel, metadata)

        if plot_type == 'line':
            fig.add_trace(go.Scatter(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                mode='lines',
                name=label,
                line=dict(color=colors[i], width=2),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

        elif plot_type == 'bar':
            fig.add_trace(go.Bar(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                name=label,
                marker_color=colors[i],
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

        elif plot_type == 'area':
            fig.add_trace(go.Scatter(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                mode='lines',
                name=label,
                fill='tonexty' if i > 0 else 'tozeroy',
                line=dict(color=colors[i], width=0),
                fillcolor=colors[i],
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

        elif plot_type == 'scatter':
            fig.add_trace(go.Scatter(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                mode='markers',
                name=label,
                marker=dict(color=colors[i], size=6, opacity=0.7),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

    # Update layout for slick appearance
    fig.update_layout(
        template='plotly_white',
        title={
            'text': 'Timeseries Visualization',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#1f77b4'}
        },
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600,
        margin=dict(l=60, r=40, t=100, b=60)
    )

    # Apply bar mode if bar chart
    if plot_type == 'bar':
        fig.update_layout(barmode=bar_mode)

    # Update grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig


def render_timeseries():
    """
    Main render function for the timeseries visualization app.
    This is called by the root app.py.
    """
    # Initialize session state
    initialize_session_state()

    # Set page configuration
    st.title("⚡ Epic Timeseries Visualization Tool")
    st.markdown("---")

    # Create two-column layout
    col_left, col_right = st.columns([1, 3])

    # LEFT COLUMN: Channel Navigation Tree
    with col_left:
        st.markdown("### 📁 Available Channels")
        st.markdown("Browse and add channels to your plot:")

        # Render the hierarchical tree
        with st.container():
            render_channel_tree(st.session_state.hierarchy)

    # RIGHT COLUMN: Plot Area and Controls
    with col_right:
        # Show selected channels
        render_selected_channels()

        # Only show controls and plot if channels are selected
        if st.session_state.selected_channels:
            st.markdown("---")

            # Plot controls in expander
            with st.expander("⚙️ Plot Settings", expanded=True):
                # Create control columns
                ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)

                with ctrl_col1:
                    # Date range
                    st.markdown("**Date Range**")
                    start_date = st.date_input(
                        "Start Date",
                        value=st.session_state.min_date.date(),
                        min_value=st.session_state.min_date.date(),
                        max_value=st.session_state.max_date.date(),
                        key="start_date"
                    )
                    end_date = st.date_input(
                        "End Date",
                        value=st.session_state.max_date.date(),
                        min_value=st.session_state.min_date.date(),
                        max_value=st.session_state.max_date.date(),
                        key="end_date"
                    )

                with ctrl_col2:
                    # Bucket size and aggregation
                    st.markdown("**Aggregation**")

                    # Get recommendation
                    if start_date and end_date:
                        recommendations = workflow.recommend_settings(
                            datetime.combine(start_date, datetime.min.time()),
                            datetime.combine(end_date, datetime.min.time())
                        )
                        recommended_idx = st.session_state.bucket_options.index(
                            recommendations['bucket_size']
                        )
                    else:
                        recommended_idx = 0

                    bucket_size = st.selectbox(
                        "Time Bucket",
                        st.session_state.bucket_options,
                        index=recommended_idx,
                        help="Aggregate data into time buckets"
                    )

                    agg_method = st.selectbox(
                        "Aggregation Method",
                        st.session_state.agg_methods,
                        index=0
                    )

                with ctrl_col3:
                    # Plot type
                    st.markdown("**Visualization**")
                    plot_type_name = st.selectbox(
                        "Plot Type",
                        st.session_state.plot_types,
                        index=0
                    )

                    # Show bar mode only for bar charts
                    plot_type = logic.PLOT_TYPES[plot_type_name]
                    if plot_type == 'bar':
                        bar_mode_name = st.selectbox(
                            "Bar Mode",
                            st.session_state.bar_modes,
                            index=0
                        )
                        bar_mode = logic.BAR_MODES[bar_mode_name]
                    else:
                        bar_mode = 'group'

            # Generate plot button
            if st.button("📈 Generate Plot", type="primary", use_container_width=True):
                # Convert dates to datetime
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = datetime.combine(end_date, datetime.max.time())

                # Generate plot data
                with st.spinner("Generating plot data..."):
                    success, plot_data, msg = workflow.generate_plot_data(
                        selected_channels=st.session_state.selected_channels,
                        start_date=start_dt,
                        end_date=end_dt,
                        bucket_size_name=bucket_size,
                        agg_method_name=agg_method
                    )

                if success:
                    st.success(msg)

                    # Create and display plot
                    fig = create_plot(
                        plot_data,
                        st.session_state.selected_channels,
                        plot_type,
                        bar_mode
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show summary stats
                    with st.expander("📊 Summary Statistics"):
                        stats = workflow.calculate_summary_stats(
                            st.session_state.selected_channels,
                            start_dt,
                            end_dt
                        )

                        # Display stats in columns
                        for channel in st.session_state.selected_channels:
                            if channel in stats:
                                metadata = workflow.get_channel_metadata(channel)
                                label = logic.format_channel_label(channel, metadata)

                                st.markdown(f"**{label}**")
                                col1, col2, col3, col4 = st.columns(4)
                                col1.metric("Mean", f"{stats[channel]['mean']:.2f}")
                                col2.metric("Min", f"{stats[channel]['min']:.2f}")
                                col3.metric("Max", f"{stats[channel]['max']:.2f}")
                                col4.metric("Std Dev", f"{stats[channel]['std']:.2f}")
                                st.markdown("---")

                else:
                    st.error(f"Error: {msg}")

        else:
            # Friendly empty state
            st.info("👈 Select channels from the left panel to get started!")


if __name__ == "__main__":
    """Standalone test - run the app directly."""
    render_timeseries()

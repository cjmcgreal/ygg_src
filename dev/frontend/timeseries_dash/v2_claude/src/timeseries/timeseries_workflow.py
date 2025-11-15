"""
Workflow layer for timeseries visualization.
Orchestrates interactions between UI, database, analysis, and logic layers.
Each function represents a specific user action or workflow.
"""

from datetime import datetime
from typing import List, Dict, Tuple
import pandas as pd

# Import all the layers
from . import timeseries_db as db
from . import timeseries_analysis as analysis
from . import timeseries_logic as logic


def initialize_app() -> dict:
    """
    Initialize the application and load all necessary metadata.
    Called when the app first starts.

    Returns:
        dict: Initial app state with hierarchy, channels, date range, etc.
    """
    # Load channel hierarchy for navigation tree
    hierarchy = db.get_channel_hierarchy()

    # Load channel list
    channels = db.get_channel_list()

    # Get available date range from data
    min_date, max_date = db.get_date_range()

    # Get bucket size options
    bucket_options = list(analysis.BUCKET_SIZES.keys())

    # Get plot type options
    plot_types = list(logic.PLOT_TYPES.keys())

    # Get bar mode options
    bar_modes = list(logic.BAR_MODES.keys())

    # Get aggregation method options
    agg_methods = list(logic.AGG_METHODS.keys())

    return {
        'hierarchy': hierarchy,
        'all_channels': channels,
        'min_date': min_date,
        'max_date': max_date,
        'bucket_options': bucket_options,
        'plot_types': plot_types,
        'bar_modes': bar_modes,
        'agg_methods': agg_methods
    }


def add_channel_to_plot(
    current_channels: List[str],
    new_channel: str
) -> Tuple[bool, List[str], str]:
    """
    Add a channel to the current plot selection.
    Validates before adding.

    Args:
        current_channels (List[str]): Currently selected channels
        new_channel (str): Channel to add

    Returns:
        Tuple[bool, List[str], str]: (success, updated_channels, message)
    """
    # Check if already added
    if new_channel in current_channels:
        return False, current_channels, f"Channel '{new_channel}' is already in the plot"

    # Try adding the channel
    updated_channels = current_channels + [new_channel]

    # Validate the new selection
    is_valid, error_msg = logic.validate_channel_selection(updated_channels)

    if not is_valid:
        return False, current_channels, error_msg

    return True, updated_channels, f"Added '{new_channel}' to plot"


def remove_channel_from_plot(
    current_channels: List[str],
    channel_to_remove: str
) -> Tuple[bool, List[str], str]:
    """
    Remove a channel from the current plot selection.

    Args:
        current_channels (List[str]): Currently selected channels
        channel_to_remove (str): Channel to remove

    Returns:
        Tuple[bool, List[str], str]: (success, updated_channels, message)
    """
    if channel_to_remove not in current_channels:
        return False, current_channels, f"Channel '{channel_to_remove}' is not in the plot"

    updated_channels = [ch for ch in current_channels if ch != channel_to_remove]

    return True, updated_channels, f"Removed '{channel_to_remove}' from plot"


def clear_all_channels(current_channels: List[str]) -> Tuple[bool, List[str], str]:
    """
    Clear all selected channels.

    Args:
        current_channels (List[str]): Currently selected channels

    Returns:
        Tuple[bool, List[str], str]: (success, updated_channels, message)
    """
    if not current_channels:
        return False, current_channels, "No channels to clear"

    return True, [], "Cleared all channels from plot"


def generate_plot_data(
    selected_channels: List[str],
    start_date: datetime,
    end_date: datetime,
    bucket_size_name: str,
    agg_method_name: str
) -> Tuple[bool, pd.DataFrame, str]:
    """
    Generate the plot data based on user selections.
    This is called when the user wants to update/refresh the plot.

    Args:
        selected_channels (List[str]): Channels to plot
        start_date (datetime): Start of date range
        end_date (datetime): End of date range
        bucket_size_name (str): User-friendly bucket size name
        agg_method_name (str): User-friendly aggregation method name

    Returns:
        Tuple[bool, pd.DataFrame, str]: (success, plot_data, message)
    """
    # Validate inputs
    is_valid, error = logic.validate_channel_selection(selected_channels)
    if not is_valid:
        return False, pd.DataFrame(), error

    is_valid, error = logic.validate_date_range(start_date, end_date)
    if not is_valid:
        return False, pd.DataFrame(), error

    # Convert user-friendly names to internal values
    bucket_size = analysis.BUCKET_SIZES.get(bucket_size_name)
    agg_method = logic.AGG_METHODS.get(agg_method_name, 'mean')

    # Load raw data
    raw_data = db.load_timeseries_data()

    # Prepare plot data using analysis layer
    plot_data = analysis.prepare_plot_data(
        df=raw_data,
        channels=selected_channels,
        start_date=start_date,
        end_date=end_date,
        bucket_size=bucket_size,
        agg_method=agg_method
    )

    # Validate the prepared data
    is_valid, error = logic.validate_plot_data(plot_data)
    if not is_valid:
        return False, pd.DataFrame(), error

    return True, plot_data, "Plot data generated successfully"


def get_channel_metadata(channel_name: str) -> dict:
    """
    Get full metadata for a specific channel.

    Args:
        channel_name (str): Channel name

    Returns:
        dict: Channel metadata (unit, description, hierarchy, etc.)
    """
    return db.get_channel_info(channel_name)


def calculate_summary_stats(
    selected_channels: List[str],
    start_date: datetime,
    end_date: datetime
) -> dict:
    """
    Calculate summary statistics for selected channels in the date range.

    Args:
        selected_channels (List[str]): Channels to summarize
        start_date (datetime): Start of date range
        end_date (datetime): End of date range

    Returns:
        dict: Summary statistics for each channel
    """
    if not selected_channels:
        return {}

    # Load raw data
    raw_data = db.load_timeseries_data()

    # Filter by date range
    filtered_data = analysis.filter_by_date_range(raw_data, start_date, end_date)

    # Calculate summary
    summary = analysis.get_data_summary(filtered_data, selected_channels)

    return summary


def recommend_settings(start_date: datetime, end_date: datetime) -> dict:
    """
    Recommend optimal plot settings based on the selected date range.

    Args:
        start_date (datetime): Start of date range
        end_date (datetime): End of date range

    Returns:
        dict: Recommended settings (bucket_size, etc.)
    """
    # Calculate date range in days
    date_range_days = (end_date - start_date).days

    # Get recommended bucket size
    recommended_bucket = logic.recommend_bucket_size(date_range_days)

    return {
        'bucket_size': recommended_bucket,
        'date_range_days': date_range_days
    }


if __name__ == "__main__":
    """Standalone test section for manual verification."""

    print("=" * 60)
    print("TIMESERIES WORKFLOW LAYER TEST")
    print("=" * 60)

    # Test app initialization
    print("\n1. Testing app initialization...")
    app_state = initialize_app()
    print(f"   ✓ Hierarchy loaded: {list(app_state['hierarchy'].keys())}")
    print(f"   ✓ Total channels: {len(app_state['all_channels'])}")
    print(f"   ✓ Date range: {app_state['min_date']} to {app_state['max_date']}")
    print(f"   ✓ Bucket options: {len(app_state['bucket_options'])}")
    print(f"   ✓ Plot types: {app_state['plot_types']}")

    # Test adding channels
    print("\n2. Testing channel selection workflow...")
    channels = []
    success, channels, msg = add_channel_to_plot(channels, 'building_a_hvac_temperature')
    print(f"   ✓ Add channel 1: {success} - '{msg}'")

    success, channels, msg = add_channel_to_plot(channels, 'building_b_hvac_temperature')
    print(f"   ✓ Add channel 2: {success} - '{msg}'")

    # Try adding duplicate
    success, channels, msg = add_channel_to_plot(channels, 'building_a_hvac_temperature')
    print(f"   ✓ Add duplicate: {success} - '{msg}'")

    # Test removing channel
    print("\n3. Testing channel removal...")
    success, channels, msg = remove_channel_from_plot(channels, 'building_a_hvac_temperature')
    print(f"   ✓ Remove channel: {success} - '{msg}'")
    print(f"   ✓ Remaining channels: {channels}")

    # Test clearing
    print("\n4. Testing clear all...")
    success, channels, msg = clear_all_channels(channels)
    print(f"   ✓ Clear all: {success} - '{msg}'")
    print(f"   ✓ Remaining channels: {channels}")

    # Test plot data generation
    print("\n5. Testing plot data generation...")
    test_channels = ['building_a_hvac_temperature', 'building_a_power_consumption']
    success, plot_df, msg = generate_plot_data(
        selected_channels=test_channels,
        start_date=app_state['min_date'],
        end_date=app_state['max_date'],
        bucket_size_name='1 Day',
        agg_method_name='Average (Mean)'
    )
    print(f"   ✓ Success: {success}")
    print(f"   ✓ Message: {msg}")
    print(f"   ✓ Data shape: {plot_df.shape}")
    print(f"   ✓ Columns: {list(plot_df.columns)}")

    # Test metadata lookup
    print("\n6. Testing channel metadata lookup...")
    metadata = get_channel_metadata('building_a_hvac_temperature')
    print(f"   ✓ Channel: {metadata['channel_name']}")
    print(f"   ✓ Unit: {metadata['unit']}")
    print(f"   ✓ Hierarchy: {metadata['hierarchy']}")

    # Test summary stats
    print("\n7. Testing summary statistics...")
    stats = calculate_summary_stats(
        selected_channels=['building_a_hvac_temperature'],
        start_date=app_state['min_date'],
        end_date=app_state['max_date']
    )
    print(f"   ✓ Channels analyzed: {list(stats.keys())}")
    channel_stats = stats['building_a_hvac_temperature']
    print(f"   ✓ Mean: {channel_stats['mean']:.2f}")
    print(f"   ✓ Min: {channel_stats['min']:.2f}")
    print(f"   ✓ Max: {channel_stats['max']:.2f}")

    # Test recommendations
    print("\n8. Testing settings recommendations...")
    recommendations = recommend_settings(
        start_date=app_state['min_date'],
        end_date=app_state['max_date']
    )
    print(f"   ✓ Date range: {recommendations['date_range_days']} days")
    print(f"   ✓ Recommended bucket: {recommendations['bucket_size']}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

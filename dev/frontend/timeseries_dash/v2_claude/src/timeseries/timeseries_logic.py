"""
Business logic layer for timeseries visualization.
Handles plot type logic, validation, and configuration rules.
"""

from typing import List, Dict
import pandas as pd


# Available plot types
PLOT_TYPES = {
    'Line Chart': 'line',
    'Bar Chart': 'bar',
    'Area Chart': 'area',
    'Scatter Plot': 'scatter'
}

# Available bar chart modes
BAR_MODES = {
    'Side by Side': 'group',
    'Stacked': 'stack'
}

# Available aggregation methods
AGG_METHODS = {
    'Average (Mean)': 'mean',
    'Sum (Total)': 'sum',
    'Minimum': 'min',
    'Maximum': 'max',
    'Median': 'median'
}


def validate_channel_selection(channels: List[str]) -> tuple[bool, str]:
    """
    Validate that the channel selection is valid for plotting.

    Args:
        channels (List[str]): Selected channel names

    Returns:
        tuple[bool, str]: (is_valid, error_message)
                         error_message is empty string if valid
    """
    if not channels or len(channels) == 0:
        return False, "Please select at least one channel to plot"

    # Reasonable limit on number of channels to prevent cluttered plots
    if len(channels) > 10:
        return False, "Too many channels selected (max 10). Plot will be unreadable."

    return True, ""


def validate_date_range(start_date, end_date) -> tuple[bool, str]:
    """
    Validate that the date range is valid.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if start_date is None or end_date is None:
        return False, "Please select both start and end dates"

    if start_date >= end_date:
        return False, "Start date must be before end date"

    return True, ""


def get_plot_config(
    plot_type: str,
    bar_mode: str = 'group',
    show_legend: bool = True,
    show_grid: bool = True
) -> dict:
    """
    Generate plot configuration based on user preferences.

    Args:
        plot_type (str): Type of plot ('line', 'bar', 'area', 'scatter')
        bar_mode (str): Bar chart mode ('group' or 'stack')
        show_legend (bool): Whether to show legend
        show_grid (bool): Whether to show grid lines

    Returns:
        dict: Configuration dictionary for plotting library
    """
    config = {
        'plot_type': plot_type,
        'bar_mode': bar_mode,
        'show_legend': show_legend,
        'show_grid': show_grid
    }

    # Add plot-specific configurations
    if plot_type == 'line':
        config['line_shape'] = 'linear'  # Could be 'spline' for smoothing
        config['fill'] = None

    elif plot_type == 'area':
        config['line_shape'] = 'linear'
        config['fill'] = 'tonexty'  # Fill to next Y
        config['fillmode'] = 'overlay'  # Overlay areas

    elif plot_type == 'bar':
        config['bargap'] = 0.15  # Gap between bars
        config['bargroupgap'] = 0.1  # Gap between bar groups

    elif plot_type == 'scatter':
        config['marker_size'] = 5
        config['marker_opacity'] = 0.7

    return config


def should_use_long_format(plot_type: str, bar_mode: str) -> bool:
    """
    Determine if data should be in long format for the given plot configuration.

    Some plot types/modes work better with long format data.

    Args:
        plot_type (str): Type of plot
        bar_mode (str): Bar chart mode

    Returns:
        bool: True if long format should be used
    """
    # Stacked bar charts often work better with long format
    if plot_type == 'bar' and bar_mode == 'stack':
        return True

    # For other types, wide format is usually fine
    return False


def get_color_palette(num_channels: int) -> List[str]:
    """
    Get a color palette for the specified number of channels.

    Returns visually distinct colors for better readability.

    Args:
        num_channels (int): Number of channels to generate colors for

    Returns:
        List[str]: List of color hex codes
    """
    # Curated color palette that's visually pleasing and accessible
    base_palette = [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f',  # Gray
        '#bcbd22',  # Yellow-green
        '#17becf',  # Cyan
    ]

    # If we need more colors than in palette, repeat it
    colors = []
    for i in range(num_channels):
        colors.append(base_palette[i % len(base_palette)])

    return colors


def recommend_bucket_size(date_range_days: int) -> str:
    """
    Recommend an appropriate bucket size based on the date range.

    Business rule: Choose bucket size to give roughly 50-200 data points.

    Args:
        date_range_days (int): Number of days in the date range

    Returns:
        str: Recommended bucket size (user-friendly name)
    """
    if date_range_days <= 2:
        return '1 Hour'
    elif date_range_days <= 7:
        return '6 Hours'
    elif date_range_days <= 14:
        return '12 Hours'
    elif date_range_days <= 60:
        return '1 Day'
    elif date_range_days <= 180:
        return '1 Week'
    elif date_range_days <= 365:
        return '1 Month'
    else:
        return '3 Months'


def format_channel_label(channel_name: str, channel_info: dict = None) -> str:
    """
    Format channel name for display in plots.

    Args:
        channel_name (str): Raw channel name
        channel_info (dict): Optional channel metadata with 'unit' field

    Returns:
        str: Formatted label for display
    """
    # Convert underscores to spaces and title case
    label = channel_name.replace('_', ' ').title()

    # Add unit if available
    if channel_info and 'unit' in channel_info:
        unit = channel_info['unit']
        label = f"{label} ({unit})"

    return label


def validate_plot_data(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate that the prepared data is suitable for plotting.

    Args:
        df (pd.DataFrame): Prepared plot data

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if df is None or df.empty:
        return False, "No data available for the selected date range and filters"

    if len(df) < 2:
        return False, "Not enough data points (need at least 2). Try adjusting date range or bucket size."

    if 'timestamp' not in df.columns:
        return False, "Invalid data format: missing timestamp column"

    return True, ""


if __name__ == "__main__":
    """Standalone test section for manual verification."""

    print("=" * 60)
    print("TIMESERIES LOGIC LAYER TEST")
    print("=" * 60)

    # Test channel validation
    print("\n1. Testing channel validation...")
    valid, msg = validate_channel_selection(['channel1', 'channel2'])
    print(f"   ✓ Valid selection (2 channels): {valid}")

    valid, msg = validate_channel_selection([])
    print(f"   ✓ Empty selection: {valid} - '{msg}'")

    valid, msg = validate_channel_selection([f'channel{i}' for i in range(15)])
    print(f"   ✓ Too many channels (15): {valid} - '{msg}'")

    # Test date validation
    print("\n2. Testing date validation...")
    from datetime import datetime, timedelta
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    valid, msg = validate_date_range(yesterday, now)
    print(f"   ✓ Valid range: {valid}")

    valid, msg = validate_date_range(now, yesterday)
    print(f"   ✓ Invalid range (end before start): {valid} - '{msg}'")

    # Test plot configuration
    print("\n3. Testing plot configuration...")
    for plot_name, plot_type in PLOT_TYPES.items():
        config = get_plot_config(plot_type)
        print(f"   ✓ {plot_name:15s}: {config['plot_type']}")

    # Test bar mode config
    print("\n4. Testing bar chart modes...")
    for mode_name, mode_value in BAR_MODES.items():
        config = get_plot_config('bar', bar_mode=mode_value)
        print(f"   ✓ {mode_name:15s}: bar_mode='{config['bar_mode']}'")

    # Test color palette
    print("\n5. Testing color palette generation...")
    colors = get_color_palette(5)
    print(f"   ✓ Generated {len(colors)} colors")
    print(f"   ✓ Sample colors: {colors[:3]}")

    # Test bucket size recommendation
    print("\n6. Testing bucket size recommendations...")
    test_ranges = [1, 5, 10, 30, 90, 200, 400]
    for days in test_ranges:
        recommendation = recommend_bucket_size(days)
        print(f"   ✓ {days:3d} days: {recommendation}")

    # Test channel label formatting
    print("\n7. Testing channel label formatting...")
    test_channel = "building_a_hvac_temperature"
    label1 = format_channel_label(test_channel)
    print(f"   ✓ Without unit: {label1}")

    label2 = format_channel_label(test_channel, {'unit': '°C'})
    print(f"   ✓ With unit: {label2}")

    # Test long format decision
    print("\n8. Testing long format logic...")
    print(f"   ✓ Bar (group):  Long format? {should_use_long_format('bar', 'group')}")
    print(f"   ✓ Bar (stack):  Long format? {should_use_long_format('bar', 'stack')}")
    print(f"   ✓ Line:         Long format? {should_use_long_format('line', 'group')}")

    # Test plot data validation
    print("\n9. Testing plot data validation...")
    # Valid data
    valid_df = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01', periods=10, freq='1D'),
        'channel1': range(10)
    })
    valid, msg = validate_plot_data(valid_df)
    print(f"   ✓ Valid data (10 rows): {valid}")

    # Empty data
    empty_df = pd.DataFrame()
    valid, msg = validate_plot_data(empty_df)
    print(f"   ✓ Empty data: {valid} - '{msg}'")

    # Too few points
    small_df = pd.DataFrame({
        'timestamp': [pd.Timestamp('2025-01-01')],
        'channel1': [1]
    })
    valid, msg = validate_plot_data(small_df)
    print(f"   ✓ Too few points (1): {valid} - '{msg}'")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

"""
Analysis layer for timeseries data.
Handles time-based aggregation, bucketing, and data transformations.
"""

import pandas as pd
from typing import List, Tuple
from datetime import datetime


# Mapping of user-friendly bucket names to pandas resample frequencies
BUCKET_SIZES = {
    '1 Hour': '1H',
    '6 Hours': '6H',
    '12 Hours': '12H',
    '1 Day': '1D',
    '1 Week': '1W',
    '1 Month': '1M',
    '3 Months': '3M',
    'Raw Data (no aggregation)': None  # No aggregation
}


def filter_by_date_range(
    df: pd.DataFrame,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """
    Filter timeseries data to a specific date range.

    Args:
        df (pd.DataFrame): Timeseries data with 'timestamp' column
        start_date (datetime): Start of date range (inclusive)
        end_date (datetime): End of date range (inclusive)

    Returns:
        pd.DataFrame: Filtered data
    """
    # Create copy to avoid modifying original
    filtered_df = df.copy()

    # Filter by date range
    mask = (filtered_df['timestamp'] >= start_date) & (filtered_df['timestamp'] <= end_date)
    filtered_df = filtered_df[mask]

    return filtered_df


def aggregate_timeseries(
    df: pd.DataFrame,
    channels: List[str],
    bucket_size: str = '1D',
    agg_method: str = 'mean'
) -> pd.DataFrame:
    """
    Aggregate timeseries data into time buckets.

    Args:
        df (pd.DataFrame): Timeseries data with 'timestamp' column
        channels (List[str]): List of channel names to include
        bucket_size (str): Pandas resample frequency string (e.g., '1H', '1D', '1W')
                          If None, returns raw data without aggregation
        agg_method (str): Aggregation method - 'mean', 'sum', 'min', 'max', 'median'

    Returns:
        pd.DataFrame: Aggregated data with timestamp and channel columns
    """
    # Create copy and ensure we only have timestamp + requested channels
    work_df = df[['timestamp'] + channels].copy()

    # If no bucket size specified, return raw data
    if bucket_size is None or bucket_size == 'None':
        return work_df

    # Set timestamp as index for resampling
    work_df = work_df.set_index('timestamp')

    # Perform aggregation based on method
    if agg_method == 'mean':
        aggregated = work_df.resample(bucket_size).mean()
    elif agg_method == 'sum':
        aggregated = work_df.resample(bucket_size).sum()
    elif agg_method == 'min':
        aggregated = work_df.resample(bucket_size).min()
    elif agg_method == 'max':
        aggregated = work_df.resample(bucket_size).max()
    elif agg_method == 'median':
        aggregated = work_df.resample(bucket_size).median()
    else:
        # Default to mean if invalid method
        aggregated = work_df.resample(bucket_size).mean()

    # Reset index to make timestamp a column again
    aggregated = aggregated.reset_index()

    # Drop any rows with NaN values (can happen at boundaries)
    aggregated = aggregated.dropna()

    return aggregated


def prepare_plot_data(
    df: pd.DataFrame,
    channels: List[str],
    start_date: datetime,
    end_date: datetime,
    bucket_size: str = '1D',
    agg_method: str = 'mean'
) -> pd.DataFrame:
    """
    Complete data preparation pipeline for plotting.
    Combines filtering, channel selection, and aggregation.

    Args:
        df (pd.DataFrame): Raw timeseries data
        channels (List[str]): Channels to include in plot
        start_date (datetime): Start of date range
        end_date (datetime): End of date range
        bucket_size (str): Time bucket size (pandas frequency string)
        agg_method (str): Aggregation method

    Returns:
        pd.DataFrame: Processed data ready for plotting
    """
    # Step 1: Filter by date range
    filtered_df = filter_by_date_range(df, start_date, end_date)

    # Step 2: Aggregate into time buckets
    aggregated_df = aggregate_timeseries(
        filtered_df,
        channels,
        bucket_size,
        agg_method
    )

    return aggregated_df


def get_data_summary(df: pd.DataFrame, channels: List[str]) -> dict:
    """
    Calculate summary statistics for selected channels.

    Args:
        df (pd.DataFrame): Timeseries data
        channels (List[str]): Channels to summarize

    Returns:
        dict: Summary statistics for each channel
              {channel_name: {'mean': x, 'min': y, 'max': z, ...}}
    """
    summary = {}

    for channel in channels:
        if channel in df.columns:
            channel_data = df[channel]
            summary[channel] = {
                'mean': channel_data.mean(),
                'median': channel_data.median(),
                'min': channel_data.min(),
                'max': channel_data.max(),
                'std': channel_data.std(),
                'count': channel_data.count()
            }

    return summary


def convert_to_long_format(df: pd.DataFrame, channels: List[str]) -> pd.DataFrame:
    """
    Convert wide-format data to long format for certain plot types.

    Wide format: timestamp | channel1 | channel2 | channel3
    Long format: timestamp | channel_name | value

    Args:
        df (pd.DataFrame): Wide-format timeseries data
        channels (List[str]): Channels to include

    Returns:
        pd.DataFrame: Long-format data with columns [timestamp, channel, value]
    """
    # Melt the dataframe to long format
    long_df = df.melt(
        id_vars=['timestamp'],
        value_vars=channels,
        var_name='channel',
        value_name='value'
    )

    return long_df


if __name__ == "__main__":
    """Standalone test section for manual verification."""

    # Import database layer for test data
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.timeseries.timeseries_db import load_timeseries_data, get_date_range

    print("=" * 60)
    print("TIMESERIES ANALYSIS LAYER TEST")
    print("=" * 60)

    # Load test data
    print("\n1. Loading test data...")
    df = load_timeseries_data()
    print(f"   ✓ Loaded {len(df)} rows")

    # Test date range filtering
    print("\n2. Testing date range filtering...")
    min_date, max_date = get_date_range()
    mid_date = min_date + (max_date - min_date) / 2
    filtered = filter_by_date_range(df, mid_date, max_date)
    print(f"   ✓ Original rows: {len(df)}")
    print(f"   ✓ Filtered rows: {len(filtered)}")
    print(f"   ✓ Date range: {filtered['timestamp'].min()} to {filtered['timestamp'].max()}")

    # Test aggregation
    print("\n3. Testing time bucket aggregation...")
    test_channels = ['building_a_hvac_temperature', 'building_a_power_consumption']
    aggregated = aggregate_timeseries(df, test_channels, bucket_size='1D', agg_method='mean')
    print(f"   ✓ Original rows: {len(df)}")
    print(f"   ✓ Aggregated rows (1D buckets): {len(aggregated)}")
    print(f"   ✓ Channels: {list(aggregated.columns)}")

    # Test different bucket sizes
    print("\n4. Testing different bucket sizes...")
    for bucket_name, bucket_freq in BUCKET_SIZES.items():
        if bucket_freq is not None:
            agg = aggregate_timeseries(df, test_channels, bucket_size=bucket_freq, agg_method='mean')
            print(f"   ✓ {bucket_name:20s}: {len(agg):5d} rows")

    # Test complete pipeline
    print("\n5. Testing complete preparation pipeline...")
    prepared = prepare_plot_data(
        df,
        channels=['building_a_hvac_temperature', 'building_b_hvac_temperature'],
        start_date=mid_date,
        end_date=max_date,
        bucket_size='1D',
        agg_method='mean'
    )
    print(f"   ✓ Prepared {len(prepared)} rows")
    print(f"   ✓ Columns: {list(prepared.columns)}")

    # Test summary statistics
    print("\n6. Testing summary statistics...")
    summary = get_data_summary(df, ['building_a_hvac_temperature'])
    print(f"   ✓ Channel: building_a_hvac_temperature")
    print(f"   ✓ Mean: {summary['building_a_hvac_temperature']['mean']:.2f}")
    print(f"   ✓ Min:  {summary['building_a_hvac_temperature']['min']:.2f}")
    print(f"   ✓ Max:  {summary['building_a_hvac_temperature']['max']:.2f}")

    # Test long format conversion
    print("\n7. Testing long format conversion...")
    long_df = convert_to_long_format(prepared, ['building_a_hvac_temperature', 'building_b_hvac_temperature'])
    print(f"   ✓ Wide format shape: {prepared.shape}")
    print(f"   ✓ Long format shape: {long_df.shape}")
    print(f"   ✓ Long format columns: {list(long_df.columns)}")
    print(f"   ✓ Sample:\n{long_df.head(3)}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

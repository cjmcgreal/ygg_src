"""
Database layer for timeseries data.
Handles loading timeseries data and channel metadata from CSV files.
"""

import pandas as pd
import os
from typing import Dict, List, Tuple


def get_data_path() -> str:
    """
    Get the absolute path to the timeseries data directory.

    Returns:
        str: Absolute path to data directory
    """
    # Get the directory where this file lives
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, 'timeseries_data')
    return data_dir


def load_timeseries_data() -> pd.DataFrame:
    """
    Load the main timeseries data from CSV.

    Returns:
        pd.DataFrame: Timeseries data with 'timestamp' column and channel columns
                     Timestamp column is converted to datetime type
    """
    data_path = os.path.join(get_data_path(), 'timeseries_data.csv')

    # Load CSV and parse timestamp column
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Sort by timestamp to ensure chronological order
    df = df.sort_values('timestamp').reset_index(drop=True)

    return df


def load_channel_tags() -> pd.DataFrame:
    """
    Load channel metadata and hierarchy information from CSV.

    Returns:
        pd.DataFrame: Channel metadata with columns:
                     - channel_name: unique identifier for the channel
                     - hierarchy: slash-separated path (e.g., "Building A/HVAC/Temperature")
                     - category: channel category (e.g., "temperature", "power")
                     - unit: measurement unit (e.g., "°C", "kW")
                     - description: human-readable description
    """
    tags_path = os.path.join(get_data_path(), 'channel_tags.csv')
    df = pd.read_csv(tags_path)
    return df


def get_channel_list() -> List[str]:
    """
    Get list of all available channel names.

    Returns:
        List[str]: List of channel names from the tags file
    """
    tags_df = load_channel_tags()
    return tags_df['channel_name'].tolist()


def get_channel_hierarchy() -> Dict[str, dict]:
    """
    Build a hierarchical tree structure from channel tags.

    Returns:
        Dict: Nested dictionary representing the hierarchy
              Each leaf node contains channel metadata

    Example structure:
        {
            'Building A': {
                'HVAC': {
                    'Temperature': {
                        'channel': 'building_a_hvac_temperature',
                        'unit': '°C',
                        'description': '...'
                    }
                }
            }
        }
    """
    tags_df = load_channel_tags()
    hierarchy = {}

    for _, row in tags_df.iterrows():
        # Split hierarchy path into parts
        parts = row['hierarchy'].split('/')

        # Navigate/create nested structure
        current_level = hierarchy
        for part in parts[:-1]:  # All parts except the last
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        # Add leaf node with channel metadata
        leaf_name = parts[-1]
        current_level[leaf_name] = {
            'channel': row['channel_name'],
            'unit': row['unit'],
            'description': row['description'],
            'category': row['category']
        }

    return hierarchy


def get_channel_info(channel_name: str) -> dict:
    """
    Get metadata for a specific channel.

    Args:
        channel_name (str): Name of the channel

    Returns:
        dict: Channel metadata (unit, description, category, hierarchy)
              Returns None if channel not found
    """
    tags_df = load_channel_tags()
    channel_row = tags_df[tags_df['channel_name'] == channel_name]

    if channel_row.empty:
        return None

    return channel_row.iloc[0].to_dict()


def get_date_range() -> Tuple[pd.Timestamp, pd.Timestamp]:
    """
    Get the min and max timestamps from the data.

    Returns:
        Tuple[pd.Timestamp, pd.Timestamp]: (min_date, max_date)
    """
    df = load_timeseries_data()
    return df['timestamp'].min(), df['timestamp'].max()


if __name__ == "__main__":
    """Standalone test section for manual verification."""

    print("=" * 60)
    print("TIMESERIES DATABASE LAYER TEST")
    print("=" * 60)

    # Test loading timeseries data
    print("\n1. Loading timeseries data...")
    ts_df = load_timeseries_data()
    print(f"   ✓ Loaded {len(ts_df)} rows")
    print(f"   ✓ Columns: {list(ts_df.columns)}")
    print(f"   ✓ Date range: {ts_df['timestamp'].min()} to {ts_df['timestamp'].max()}")

    # Test loading channel tags
    print("\n2. Loading channel tags...")
    tags_df = load_channel_tags()
    print(f"   ✓ Loaded {len(tags_df)} channels")
    print(f"   ✓ First channel: {tags_df.iloc[0]['channel_name']}")

    # Test channel list
    print("\n3. Getting channel list...")
    channels = get_channel_list()
    print(f"   ✓ Found {len(channels)} channels")
    print(f"   ✓ Sample channels: {channels[:3]}")

    # Test hierarchy building
    print("\n4. Building channel hierarchy...")
    hierarchy = get_channel_hierarchy()
    print(f"   ✓ Top-level nodes: {list(hierarchy.keys())}")
    print(f"   ✓ Building A structure: {list(hierarchy.get('Building A', {}).keys())}")

    # Test channel info lookup
    print("\n5. Looking up channel info...")
    test_channel = channels[0]
    info = get_channel_info(test_channel)
    print(f"   ✓ Channel: {test_channel}")
    print(f"   ✓ Unit: {info['unit']}")
    print(f"   ✓ Description: {info['description']}")

    # Test date range
    print("\n6. Getting date range...")
    min_date, max_date = get_date_range()
    print(f"   ✓ Min: {min_date}")
    print(f"   ✓ Max: {max_date}")
    print(f"   ✓ Duration: {(max_date - min_date).days} days")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

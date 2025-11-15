#!/usr/bin/env python3
"""
Generate sample timeseries data for the visualization tool.
Creates realistic multi-channel data with daily granularity over 90 days.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# Generate timestamps: last 90 days, hourly data
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
timestamps = pd.date_range(start=start_date, end=end_date, freq='1H')

# Initialize data dictionary
data = {'timestamp': timestamps}

# Building A - HVAC Temperature (Celsius, with daily cycle)
hours = np.array(range(len(timestamps))) % 24
data['building_a_hvac_temperature'] = (
    20 + 3 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 0.5, len(timestamps))
)

# Building A - HVAC Humidity (Percentage)
data['building_a_hvac_humidity'] = (
    55 + 10 * np.sin(2 * np.pi * hours / 24 + np.pi/4) + np.random.normal(0, 2, len(timestamps))
)

# Building A - Power Consumption (kW, higher during day)
data['building_a_power_consumption'] = (
    150 + 50 * np.sin(2 * np.pi * hours / 24 - np.pi/2) + np.random.normal(0, 10, len(timestamps))
)

# Building B - HVAC Temperature
data['building_b_hvac_temperature'] = (
    21 + 2.5 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 0.6, len(timestamps))
)

# Building B - HVAC Humidity
data['building_b_hvac_humidity'] = (
    50 + 12 * np.sin(2 * np.pi * hours / 24 + np.pi/3) + np.random.normal(0, 2.5, len(timestamps))
)

# Building B - Power Consumption
data['building_b_power_consumption'] = (
    180 + 60 * np.sin(2 * np.pi * hours / 24 - np.pi/2) + np.random.normal(0, 12, len(timestamps))
)

# Factory - Production Line 1 - Speed (units/hour, only during work hours 6-22)
work_hours_mask = (hours >= 6) & (hours <= 22)
base_speed_1 = np.zeros(len(timestamps))
base_speed_1[work_hours_mask] = 450 + np.random.normal(0, 30, work_hours_mask.sum())
data['factory_line1_speed'] = base_speed_1

# Factory - Production Line 1 - Temperature (higher when running)
data['factory_line1_temperature'] = (
    25 + (base_speed_1 / 450) * 15 + np.random.normal(0, 1, len(timestamps))
)

# Factory - Production Line 2 - Speed
base_speed_2 = np.zeros(len(timestamps))
base_speed_2[work_hours_mask] = 520 + np.random.normal(0, 35, work_hours_mask.sum())
data['factory_line2_speed'] = base_speed_2

# Factory - Production Line 2 - Temperature
data['factory_line2_temperature'] = (
    25 + (base_speed_2 / 520) * 18 + np.random.normal(0, 1.2, len(timestamps))
)

# Warehouse - Inventory Count (decreases during day, restocked at night)
# Create a decreasing trend during day, reset at night
inventory_base = 10000
daily_variation = []
current_inventory = inventory_base
for i in range(len(timestamps)):
    hour = hours[i]
    if hour == 0:  # Restock at midnight
        current_inventory = inventory_base + np.random.normal(0, 200)
    else:
        # Decrease during business hours
        if 8 <= hour <= 18:
            current_inventory -= np.random.uniform(20, 50)
    daily_variation.append(current_inventory)
data['warehouse_inventory_count'] = daily_variation

# Warehouse - Environmental Temperature
data['warehouse_env_temperature'] = (
    18 + 2 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 0.8, len(timestamps))
)

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
output_path = 'src/timeseries/timeseries_data/timeseries_data.csv'
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} rows of timeseries data")
print(f"Saved to: {output_path}")
print(f"Channels: {len(df.columns) - 1}")
print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

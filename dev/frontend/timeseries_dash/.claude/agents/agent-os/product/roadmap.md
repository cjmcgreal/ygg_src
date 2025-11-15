# Product Roadmap

1. [ ] CSV Data Layer Foundation — Build the data loading and channel metadata system that reads timeseries CSV files and channel tag hierarchies, returning structured DataFrames with timestamp parsing and channel metadata lookups. `S`

2. [ ] Data Analysis and Aggregation Engine — Implement time-bucketing and aggregation logic that transforms raw timeseries data into plot-ready datasets with configurable bucket sizes (hourly, daily, weekly, monthly) and aggregation methods (mean, sum, min, max, median). `M`

3. [ ] Hierarchical Channel Browser UI — Create the collapsible tree navigation that displays channels organized by hierarchy with visual indicators (folder icons, expand/collapse controls) and renders channel metadata (units, descriptions) in an intuitive browsable structure. `M`

4. [ ] Drag-and-Drop Channel Selection — Implement client-side drag-and-drop interaction that allows users to drag channels from the browser tree and drop them onto the plot area, with visual feedback (cursor changes, drop zone highlighting) and state management for selected channels. `L`

5. [ ] Interactive Plotly Visualization — Build the main plot component that renders multi-channel timeseries data using Plotly with automatic color assignment, responsive sizing, zoom/pan controls, hover tooltips, and legend management. `M`

6. [ ] Time Range and Aggregation Controls — Create the settings panel with date pickers for start/end dates, dropdowns for bucket size and aggregation method, with validation to ensure end date is after start date and bucket size is appropriate for the selected time range. `S`

7. [ ] Channel Management Interface — Build the selected channels display area with visual badges showing currently selected channels, remove buttons for individual channels, and a clear-all button to reset selections, with color coding that matches plot traces. `S`

8. [ ] Plot Interactivity Enhancements — Add advanced Plotly features including unified hover mode for cross-channel comparison, custom hover templates showing channel hierarchy and units, and plot reset functionality to return to default zoom/pan state. `S`

9. [ ] Date Range Validation and Edge Cases — Implement validation logic that handles edge cases like date ranges with no data, channels with missing data in selected range, and aggregation buckets that are too large or too small for the selected date range. `S`

10. [ ] Sample Data Generator — Create a utility script that generates realistic sample timeseries data for testing with multiple building/facility hierarchies, various sensor types (temperature, humidity, power, speed, inventory), and configurable time ranges to demonstrate the tool's capabilities. `S`

> Notes
> - Features ordered by technical dependencies: data layer first, then analysis, UI components, and finally polish
> - Core drag-and-drop functionality (items 1-5) forms the MVP - users can load data, navigate channels, and visualize
> - Items 6-9 add essential controls and polish for production use
> - Item 10 enables easy evaluation and testing with realistic data

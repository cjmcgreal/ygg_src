# Product Mission

## Pitch
Epic Timeseries Visualization Tool is an interactive web application that helps engineers, data analysts, and operations teams explore multi-channel sensor and telemetry data by providing intuitive hierarchical navigation, drag-and-drop channel selection, and powerful interactive visualizations with flexible time aggregation.

## Users

### Primary Customers
- **Engineering Teams**: Monitor and analyze industrial systems, building automation, and process control data
- **Operations Teams**: Track real-time and historical performance metrics across facilities and production lines
- **Data Analysts**: Investigate trends, anomalies, and correlations in timeseries sensor data

### User Personas

**Operations Engineer** (28-45 years)
- **Role:** Facilities or Manufacturing Engineer
- **Context:** Responsible for monitoring HVAC systems, production lines, inventory, and equipment across multiple buildings or facilities
- **Pain Points:** Existing tools require deep technical knowledge, don't provide intuitive channel selection, lack flexible time aggregation, and make it difficult to compare metrics across systems
- **Goals:** Quickly identify issues, compare performance across locations, visualize trends over custom time periods, and drill down into specific systems without needing SQL or programming skills

**Data Analyst** (25-40 years)
- **Role:** Data Scientist or Business Analyst
- **Context:** Analyzes operational data to identify efficiency improvements, cost savings, and performance optimization opportunities
- **Pain Points:** Data is scattered across multiple sources, visualization tools are inflexible, time aggregation requires custom scripts, and it's difficult to explore hierarchical relationships in the data
- **Goals:** Rapidly explore large timeseries datasets, test hypotheses about correlations, aggregate data at different time resolutions, and create clear visualizations for stakeholder presentations

**System Administrator** (30-50 years)
- **Role:** IT or Building Management Systems Administrator
- **Context:** Maintains and troubleshoots facility automation systems, sensors, and monitoring infrastructure
- **Pain Points:** Legacy monitoring tools have poor UX, require manual data exports for analysis, don't support quick comparisons, and lack modern interactive features
- **Goals:** Quickly diagnose system issues, validate sensor readings, compare baseline vs current performance, and export data for reporting

## The Problem

### Data Exploration is Unnecessarily Complex
Engineers and analysts need to explore timeseries data from dozens or hundreds of sensor channels across multiple facilities, production lines, or systems. Existing tools either require programming knowledge (Python/R scripts), are locked behind expensive enterprise platforms, or provide rigid interfaces that don't support intuitive exploration. This results in wasted time, delayed insights, and missed opportunities to optimize operations.

**Our Solution:** A lightweight, interactive web application with drag-and-drop channel selection, hierarchical navigation that mirrors physical asset structure, and real-time visualization updates that work out of the box with CSV data sources.

### Time Aggregation Requires Technical Skills
Analyzing timeseries data at different time resolutions (hourly, daily, weekly, monthly) typically requires writing custom aggregation queries or scripts. Non-technical users are blocked from exploring data at the granularity they need, forcing them to rely on data teams for simple requests.

**Our Solution:** Built-in time aggregation with intuitive controls - users simply select their desired bucket size (1 hour, 1 day, 1 week, 1 month) and aggregation method (mean, sum, min, max, median), and the tool handles the rest.

### Channel Selection is Tedious and Error-Prone
When working with systems that have dozens or hundreds of channels, finding the right channels to compare is painful. Tools that show flat lists of channel names or require memorizing channel IDs create friction and increase the likelihood of selecting wrong channels.

**Our Solution:** Hierarchical channel browser organized by physical structure (Building A > HVAC > Temperature) with drag-and-drop interaction. Users navigate familiar asset hierarchies and intuitively add channels to their visualization.

## Differentiators

### Modern Interactive Experience
Unlike legacy SCADA interfaces or business intelligence tools that require extensive configuration, we provide a modern, responsive web interface with drag-and-drop interaction, instant plot updates, and Plotly's powerful zoom, pan, and hover capabilities built in.

This results in reduced training time, higher user adoption, and faster time-to-insight.

### No Infrastructure Required
Unlike enterprise platforms that require database setup, server configuration, and IT involvement, our tool works directly with CSV files. Load your data, define your channel hierarchy, and start visualizing immediately.

This results in rapid deployment, zero infrastructure costs, and complete data ownership.

### Flexible yet Simple
Unlike rigid dashboards that show predetermined views or complex analytics platforms that require training, we balance flexibility with simplicity. Users can freely select any combination of channels, adjust time ranges and aggregation on the fly, but the interface remains clean and approachable.

This results in power users getting the flexibility they need while new users aren't overwhelmed by options.

## Key Features

### Core Features
- **Hierarchical Channel Browser:** Navigate sensors and metrics organized by physical structure (buildings, lines, zones) with expandable/collapsible tree view that makes finding the right channels intuitive
- **Drag-and-Drop Channel Selection:** Grab any channel and drop it onto the plot area for instant visualization - no forms to fill out, no queries to write
- **Interactive Plotly Visualizations:** Zoom into time periods, pan across data, hover for precise values, and double-click to reset - all standard Plotly interactions work out of the box
- **Flexible Time Aggregation:** Select from hourly, daily, weekly, or monthly time buckets with aggregation methods (mean, sum, min, max, median) to view data at the resolution you need

### Collaboration Features
- **Multi-Channel Comparison:** Add multiple channels to the same plot to identify correlations, compare performance across locations, or validate sensor readings against each other
- **Date Range Selection:** Set custom start and end dates to focus analysis on specific time periods, incidents, or operational phases
- **Clear Channel Management:** Easily remove individual channels or clear all selections to start fresh - visual badges show selected channels at a glance

### Advanced Features
- **Color-Coded Traces:** Automatically assigns distinct colors to each channel for clear visual separation and easy legend identification
- **CSV-Based Data Model:** Works directly with CSV files for timeseries data and channel metadata - no database setup required
- **Responsive Design:** Bootstrap-based UI adapts to different screen sizes and maintains usability on laptops, desktops, and large displays
- **Real-Time Plot Updates:** Plots refresh instantly as you adjust date ranges, aggregation settings, or channel selections

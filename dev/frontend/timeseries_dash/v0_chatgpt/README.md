# Badass Time Series Dashboard (Dash + Plotly)

Drag-and-drop channels from a tree into the chart, control date range, aggregation buckets (daily/weekly/monthly/quarterly),
and switch between line/area/bars or per-series combo modes (stacked or grouped).

## Quickstart

```bash
cd timeseries_dashboard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8050

## Files
- `app.py`: Dash server app
- `requirements.txt`: Python dependencies
- `data/sample_timeseries.csv`: Example data with multiple channels across Energy, Traffic, Sales, Ops, Finance

## Features
- **Drag & drop** channels from the left tree into **Selected** (ordered).
- **Reorder** selected series by dragging inside the Selected tree.
- **Date range** picker.
- **Aggregation** buckets: None, Daily (D), Weekly (W), Monthly (M), Quarterly (Q) with mean/sum/min/max.
- **Chart Type**: Line, Area, Bars, or **Combo** with per-series type.
- **Bar mode**: Group, Stack, Overlay, Relative.
- **Log/Linear** Y scale toggle.
- Dark theme because of course.

## Notes
- The drag-and-drop trees use the community component `dash-treeview-antd`. If you run into issues:
  - Ensure the version in `requirements.txt` is installed.
  - The component exposes `nDrops` + `recentlyDroppedNode/Target` used by the app to add/reorder channels.
- To use your own data, replace `data/sample_timeseries.csv` with your file that has a `time` column and any number
  of numeric channels. Use `Group/Metric` names (e.g., `Energy/Power_kW`) to have them appear nicely grouped in the tree.

## License
MIT

# Badass Time Series Dashboard — Latest Dash Variant

This version uses **Dash >= 2.17**, **Mantine** styling, and **SortableJS** for drag-and-drop between lists.
It avoids the older `dash_treeview_antd` internals, so you can stay current with Dash.

## Quickstart
```bash
cd timeseries_dashboard_latest
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:8050

## Features
- Drag channels from **Available** into **Selected** (cloned); drag within **Selected** to reorder; drag out to remove.
- Date range picker.
- Aggregation buckets: None / D / W / M / Q; functions: mean/sum/min/max.
- Chart types: Line, Area, Bars, **Combo** (per-series types).
- Bar modes: group / stack / overlay / relative.
- Y scale: linear / log.
- Dark theme (dbc.DARKLY).

## Data
CSV at `data/sample_timeseries.csv` with `time` column + numeric channels named like `Group/Metric`.
Replace with your own to go live.

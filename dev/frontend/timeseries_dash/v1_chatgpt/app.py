from datetime import datetime
from pathlib import Path
import json

import pandas as pd
import numpy as np
import plotly.graph_objs as go

import dash
from dash import html, dcc, Input, Output, State, ctx, ALL, MATCH
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# SortableJS wrapper (community component)
# Docs: https://pypi.org/project/dash-sortable/
from dash_sortable import Sortable, SortableItem

DATA_PATH = Path(__file__).parent / "data" / "sample_timeseries.csv"

df = pd.read_csv(DATA_PATH, parse_dates=["time"]).sort_values("time")
all_channels = [c for c in df.columns if c != "time"]

# Group channels by "Group/Leaf"
def group_channels(chs):
    groups = {}
    for ch in chs:
        parts = ch.split("/", 1)
        if len(parts) == 2:
            g, leaf = parts
        else:
            g, leaf = "Other", parts[0]
        groups.setdefault(g, []).append((ch, leaf))
    return {g: sorted(v, key=lambda x: x[1]) for g, v in groups.items()}

grouped = group_channels(all_channels)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Badass Time Series Dashboard — Latest"

def make_available_panel():
    # Build a flat Sortable list with group headers and draggable leaves. Headers are non-draggable.
    items = []
    for g, leaves in sorted(grouped.items()):
        # group header (non-draggable, just a label)
        items.append(SortableItem(
            id={"type": "avail-header", "group": g},
            children=html.Div(g, className="fw-bold text-info py-1"),
            options={"disabled": True}  # not draggable
        ))
        for full_key, leaf in leaves:
            items.append(SortableItem(
                id={"type": "avail-item", "key": full_key},
                children=html.Div([
                    html.Span(leaf, className=""),
                    html.Span(f"  [{g}]", className="text-muted ms-2 small")
                ], className="p-1"),
            ))
    return Sortable(
        id="available-list",
        children=items,
        options={
            "group": {"name": "channels", "pull": "clone", "put": False},  # clone into selected
            "sort": False,  # keep available static order
            "animation": 150,
        },
        className="bg-dark p-2 rounded",
        style={"height": "62vh", "overflow": "auto", "border": "1px solid #333"}
    )

def make_selected_panel():
    return Sortable(
        id="selected-list",
        children=[],   # filled by callback via stored selected order
        options={
            "group": {"name": "channels", "pull": True, "put": True},
            "animation": 150,
        },
        className="bg-dark p-2 rounded",
        style={"height": "22vh", "overflow": "auto", "border": "1px solid #333"}
    )

def render_selected_items(selected):
    items = []
    for ch in selected:
        items.append(SortableItem(
            id={"type": "sel-item", "key": ch},
            children=html.Div(ch, className="p-1"),
        ))
    return items

app.layout = dbc.Container([
    dcc.Store(id="selected-channels", data=[]),
    dcc.Store(id="series-config", data={}),
    dbc.Row([
        dbc.Col([
            html.H4("Data Channels"),
            dmc.Text("Drag from Available into Selected. Drag within Selected to reorder.", size="sm", color="dimmed"),
            make_available_panel(),
            html.Hr(),
            dmc.Text("Selected (drag to reorder or drag out to remove)", size="sm", color="dimmed"),
            make_selected_panel(),
            dbc.Button("Clear", id="clear-selected", size="sm", color="secondary", className="mt-2"),
        ], width=3),

        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.Label("Date Range"),
                    dcc.DatePickerRange(
                        id="date-range",
                        start_date=df["time"].min().date(),
                        end_date=df["time"].max().date(),
                        display_format="YYYY-MM-DD",
                        minimum_nights=0
                    )
                ], md=4),
                dbc.Col([
                    html.Label("Aggregate (bucket)"),
                    dcc.Dropdown(
                        id="agg-freq",
                        options=[
                            {"label": "None (raw)", "value": ""},
                            {"label": "Daily (D)", "value": "D"},
                            {"label": "Weekly (W)", "value": "W"},
                            {"label": "Monthly (M)", "value": "M"},
                            {"label": "Quarterly (Q)", "value": "Q"},
                        ],
                        value="",
                        clearable=False
                    ),
                ], md=3),
                dbc.Col([
                    html.Label("Aggregation Function"),
                    dcc.Dropdown(
                        id="agg-func",
                        options=[
                            {"label": "Mean", "value": "mean"},
                            {"label": "Sum", "value": "sum"},
                            {"label": "Min", "value": "min"},
                            {"label": "Max", "value": "max"},
                        ],
                        value="mean",
                        clearable=False
                    ),
                ], md=3),
                dbc.Col([
                    html.Label("Chart Type"),
                    dcc.Dropdown(
                        id="chart-type",
                        options=[
                            {"label": "Line", "value": "line"},
                            {"label": "Area", "value": "area"},
                            {"label": "Bars", "value": "bar"},
                            {"label": "Combo (per-series)", "value": "combo"},
                        ],
                        value="line",
                        clearable=False
                    )
                ], md=2),
            ], align="end", className="gy-2"),

            dbc.Row([
                dbc.Col([
                    html.Label("Bar Mode (when Bars or Combo)"),
                    dcc.Dropdown(
                        id="bar-mode",
                        options=[
                            {"label": "Group (side-by-side)", "value": "group"},
                            {"label": "Stack", "value": "stack"},
                            {"label": "Overlay", "value": "overlay"},
                            {"label": "Relative (stacked, signed)", "value": "relative"},
                        ],
                        value="group",
                        clearable=False
                    )
                ], md=3),
                dbc.Col([
                    html.Label("Y Scale"),
                    dcc.RadioItems(
                        id="y-scale",
                        options=[{"label": "Linear", "value": "linear"}, {"label": "Log", "value": "log"}],
                        value="linear",
                        inline=True
                    )
                ], md=3),
                dbc.Col([
                    html.Label("Per-series type (Combo only)"),
                    html.Div(id="series-type-pills")
                ], md=6),
            ], className="mt-2"),

            dcc.Loading(
                dcc.Graph(id="main-graph", style={"height": "70vh"}),
                type="cube"
            )
        ], width=9)
    ])
], fluid=True)

# --- Helpers ---
def filter_and_aggregate(df, channels, start, end, freq, func):
    if not channels:
        return pd.DataFrame({"time": df["time"]})
    d = df[(df["time"] >= pd.to_datetime(start)) & (df["time"] <= pd.to_datetime(end))]
    d = d[["time"] + channels].copy()
    if freq:
        d = d.set_index("time").resample(freq).agg(func)
        d = d.reset_index()
    return d

# --- DnD logic ---
@app.callback(
    Output("selected-channels", "data"),
    Output("selected-list", "children"),
    Input("selected-list", "order"),
    Input("available-list", "order"),
    State("selected-channels", "data"),
    prevent_initial_call=True
)
def handle_sortable(sel_order, avail_order, selected):
    # The SortableJS component provides 'order' lists with the item ids.
    # We care about 'selected-list.order' for current selection order.
    # Items dragged from 'available-list' into 'selected-list' will appear in sel_order.
    selected = selected or []
    trig = ctx.triggered_id
    if trig == "selected-list":
        # Extract keys from ids that look like {"type":"sel-item","key": "..."} or {"type":"avail-item","key":"..."}
        def key_from(item_id):
            if isinstance(item_id, dict):
                return item_id.get("key")
            return None

        new_order = []
        for item in sel_order or []:
            k = key_from(item)
            if k in all_channels:
                new_order.append(k)
        # remove duplicates but keep order (Sortable shouldn't duplicate, but just in case)
        seen = set()
        dedup = []
        for k in new_order:
            if k not in seen:
                dedup.append(k)
                seen.add(k)
        return dedup, [SortableItem(id={"type":"sel-item","key":k}, children=html.Div(k, className="p-1")) for k in dedup]

    # 'available-list' order doesn't change (sort=False); ignore
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output("selected-channels", "data", allow_duplicate=True),
    Output("selected-list", "children", allow_duplicate=True),
    Input("clear-selected", "n_clicks"),
    prevent_initial_call=True
)
def clear_selected(n):
    return [], []

# Per-series type controls in Combo mode
@app.callback(
    Output("series-type-pills", "children"),
    Input("selected-channels", "data"),
    Input("chart-type", "value"),
    State("series-config", "data"),
)
def render_series_type_pills(selected, chart_type, cfg):
    selected = selected or []
    cfg = cfg or {}
    if chart_type != "combo" or not selected:
        return html.Div("—")

    pills = []
    for ch in selected:
        current = cfg.get(ch, "line")
        pills.append(
            dbc.Badge([
                ch.split("/", 1)[-1] + ": ",
                dcc.Dropdown(
                    id={"type": "series-type", "channel": ch},
                    options=[
                        {"label": "Line", "value": "line"},
                        {"label": "Area", "value": "area"},
                        {"label": "Bar", "value": "bar"},
                    ],
                    value=current,
                    clearable=False,
                    style={"width": 140, "display": "inline-block", "marginLeft": "6px"}
                )
            ], color="secondary", className="me-2 mb-2 p-2")
        )
    return pills

@app.callback(
    Output("series-config", "data"),
    Input({"type": "series-type", "channel": ALL}, "value"),
    State({"type": "series-type", "channel": ALL}, "id"),
    State("series-config", "data"),
    prevent_initial_call=True
)
def update_series_cfg(values, ids, cfg):
    cfg = cfg or {}
    if not ids:
        return cfg
    for v, idobj in zip(values, ids):
        cfg[idobj["channel"]] = v
    return cfg

# Main Graph
@app.callback(
    Output("main-graph", "figure"),
    Input("selected-channels", "data"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("agg-freq", "value"),
    Input("agg-func", "value"),
    Input("chart-type", "value"),
    Input("bar-mode", "value"),
    Input("y-scale", "value"),
    State("series-config", "data")
)
def update_graph(selected, start, end, freq, func, chart, bar_mode, yscale, cfg):
    selected = selected or []
    cfg = cfg or {}

    if not selected:
        return go.Figure(
            layout=go.Layout(
                template="plotly_dark",
                title="Drop channels to get started",
                xaxis={"title": ""},
                yaxis={"title": ""},
                paper_bgcolor="#111111",
                plot_bgcolor="#111111",
            )
        )

    d = filter_and_aggregate(df, selected, start, end, freq, func)

    fig = go.Figure()
    is_bar = (chart == "bar")
    is_area = (chart == "area")
    is_combo = (chart == "combo")

    for ch in selected:
        series_type = chart if not is_combo else cfg.get(ch, "line")
        if series_type == "bar":
            fig.add_trace(go.Bar(x=d["time"], y=d[ch], name=ch))
        elif series_type == "area":
            fig.add_trace(go.Scatter(x=d["time"], y=d[ch], name=ch, mode="lines", stackgroup="one"))
        else:
            fig.add_trace(go.Scatter(x=d["time"], y=d[ch], name=ch, mode="lines"))

    if is_bar or (is_combo and any(cfg.get(ch, "line") == "bar" for ch in selected)):
        fig.update_layout(barmode=bar_mode)

    fig.update_layout(
        template="plotly_dark",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        hovermode="x unified",
    )
    fig.update_xaxes(title="Time")
    fig.update_yaxes(title="", type=yscale)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8050)

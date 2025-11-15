import json
from datetime import datetime
import pandas as pd
import numpy as np
from pathlib import Path

import dash
from dash import html, dcc, Input, Output, State, ctx, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objs as go

# Community component with real drag-and-drop tree
import dash_treeview_antd as dta

DATA_PATH = Path(__file__).parent / "data" / "sample_timeseries.csv"

# ---------------------
# Load Data
# ---------------------
df = pd.read_csv(DATA_PATH, parse_dates=["time"])
df = df.sort_values("time")

# Identify channels as all non-time columns
all_channels = [c for c in df.columns if c != "time"]

# Build a nested tree structure from "Group/Leaf" channel names
def build_tree(channels):
    groups = {}
    for ch in channels:
        parts = ch.split("/", 1)
        if len(parts) == 2:
            group, leaf = parts
        else:
            group, leaf = "Other", parts[0]
        groups.setdefault(group, []).append(leaf)

    tree = []
    for g, leaves in sorted(groups.items()):
        children = []
        for leaf in sorted(leaves):
            full_key = f"{g}/{leaf}"
            children.append({
                "title": leaf,
                "key": full_key,
                "icon": "file",
                "isLeaf": True,
            })
        tree.append({
            "title": g,
            "key": g,
            "children": children,
            "icon": "folder",
        })
    return tree

available_tree = build_tree(all_channels)

# ---------------------
# App + Layout
# ---------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "Badass Time Series Dashboard"

app.layout = dbc.Container([
    dcc.Store(id="selected-channels", data=[]),           # ordered list of channel keys
    dcc.Store(id="series-config", data={}),               # per-series chart types

    dbc.Row([
        dbc.Col([
            html.H4("Data Channels"),
            html.Div("Drag channels into Selected below."),
            dta.Tree(
                id="available-tree",
                data=available_tree,
                draggable=True,
                multiple=True,
                showIcon=True,
                style={"height": "60vh", "overflow": "auto", "background": "#111", "padding": "6px", "borderRadius": "10px"}
            ),
            html.Hr(),
            html.Div([
                html.Div("Selected (drag to reorder)", className="text-muted mb-1"),
                dta.Tree(
                    id="selected-tree",
                    data=[],
                    draggable=True,
                    multiple=True,
                    showIcon=True,
                    style={"height": "22vh", "overflow": "auto", "background": "#111", "padding": "6px", "borderRadius": "10px"}
                ),
                dbc.Button("Clear", id="clear-selected", size="sm", color="secondary", className="mt-2")
            ])
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

# ---------------------
# Helpers
# ---------------------
def filter_and_aggregate(df, channels, start, end, freq, func):
    if not channels:
        return pd.DataFrame({"time": df["time"]})
    d = df[(df["time"] >= pd.to_datetime(start)) & (df["time"] <= pd.to_datetime(end))]
    d = d[["time"] + channels].copy()
    if freq:
        d = d.set_index("time").resample(freq).agg(func)
        d = d.reset_index()
    return d

def selected_tree_from_list(ch_list):
    # Build a tree where each selected channel is a leaf under a "Selected" group
    children = [{
        "title": ch.split("/", 1)[-1],
        "key": ch,
        "icon": "file",
        "isLeaf": True
    } for ch in ch_list]
    return [{
        "title": "Selected",
        "key": "Selected",
        "icon": "folder",
        "children": children
    }]

# ---------------------
# Drag & Drop handling
# - available-tree and selected-tree are both draggable.
# - We listen for "recentlyDropped" info exposed by dash_treeview_antd's 'recentlyDroppedNode'
#   and 'recentlyDroppedTarget' props (mirrored via nDrops). Then update the stored order.
# ---------------------
@app.callback(
    Output("selected-channels", "data"),
    Output("selected-tree", "data"),
    Input("available-tree", "nDrops"),
    State("available-tree", "recentlyDroppedNode"),
    State("available-tree", "recentlyDroppedTarget"),
    Input("selected-tree", "nDrops"),
    State("selected-tree", "recentlyDroppedNode"),
    State("selected-tree", "recentlyDroppedTarget"),
    State("selected-channels", "data"),
    prevent_initial_call=True
)
def handle_drops(
    avail_ndrops, avail_node, avail_target,
    sel_ndrops, sel_node, sel_target,
    selected
):
    # Start from current selection
    selected = selected or []

    triggered = ctx.triggered_id

    def safe_key(node):
        try:
            return node.get("node", {}).get("key")
        except Exception:
            return None

    def safe_target_key(target):
        try:
            return target.get("node", {}).get("key")
        except Exception:
            return None

    if triggered == "available-tree":
        # Dropped FROM available-tree onto selected-tree (or inside available-tree). If
        # target is "Selected" or a leaf inside "Selected", we add the leaf there.
        node_key = safe_key(avail_node)
        target_key = safe_target_key(avail_target)

        if node_key and node_key in all_channels:
            # If they dropped anywhere, interpret as "add to selected"
            if node_key not in selected:
                selected.append(node_key)

    elif triggered == "selected-tree":
        # Handle reordering within selected-tree, or removing if dropped on available root
        node_key = safe_key(sel_node)
        target_key = safe_target_key(sel_target)

        if node_key and node_key in selected:
            # Reorder: if dropped on another selected leaf, move before it.
            if target_key in selected and target_key != node_key:
                old_idx = selected.index(node_key)
                new_idx = selected.index(target_key)
                selected.pop(old_idx)
                selected.insert(new_idx, node_key)
            # Drop on "Selected" node -> no reorder, keep
            # Drop elsewhere: ignore

    # Return new selected tree
    return selected, selected_tree_from_list(selected)

@app.callback(
    Output("selected-channels", "data", allow_duplicate=True),
    Output("selected-tree", "data", allow_duplicate=True),
    Input("clear-selected", "n_clicks"),
    prevent_initial_call=True
)
def clear_selected(n):
    return [], selected_tree_from_list([])

# ---------------------
# Per-series type pills (for Combo)
# ---------------------
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

# ---------------------
# Main Graph
# ---------------------
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
        series_type = chart
        if is_combo:
            series_type = cfg.get(ch, "line")

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

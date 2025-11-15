"""
Epic Drag-and-Drop Timeseries Tool - Simplified & Fast Version
Optimized for performance with manual channel selection and instant plotting

Run with: python app_simple.py
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import json

# Import data layers
from src.timeseries import timeseries_db as db
from src.timeseries import timeseries_analysis as analysis

# Initialize app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
)
app.title = "⚡ Epic Timeseries Tool"

# Load data once at startup
print("Loading data...")
hierarchy = db.get_channel_hierarchy()
all_channels = db.get_channel_list()
min_date, max_date = db.get_date_range()
bucket_options = list(analysis.BUCKET_SIZES.keys())
raw_data = db.load_timeseries_data()  # Load once and reuse
print(f"✓ Loaded {len(all_channels)} channels")

# Color palette
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']


def get_all_channels_from_hierarchy(hier, parent="", result=None):
    """Flatten hierarchy into list of (path, channel_id, unit)."""
    if result is None:
        result = []

    for key, value in hier.items():
        path = f"{parent}/{key}" if parent else key
        if isinstance(value, dict) and 'channel' in value:
            display = '/'.join(path.split('/')[1:])  # Remove top level
            result.append((display, value['channel'], value['unit']))
        else:
            get_all_channels_from_hierarchy(value, path, result)

    return result


def create_channel_list_by_category(hierarchy):
    """Create simple list grouped by category - no drag/drop, just checkboxes."""
    accordion_items = []

    for category, content in hierarchy.items():
        channels = []
        get_all_channels_from_hierarchy({category: content}, "", channels)

        # Create checkboxes for each channel
        channel_items = []
        for path, channel_id, unit in channels:
            item = dbc.Checkbox(
                id={'type': 'channel-checkbox', 'channel': channel_id},
                label=f"{path} ({unit})",
                value=False,
                className="mb-2"
            )
            channel_items.append(item)

        accordion_item = dbc.AccordionItem(
            html.Div(channel_items, className="p-2"),
            title=f"📁 {category}",
            item_id=f"cat-{category}"
        )
        accordion_items.append(accordion_item)

    return dbc.Accordion(accordion_items, start_collapsed=False, always_open=True, flush=True)


# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-bolt me-3", style={'color': '#ffc107'}),
                "Epic Timeseries Tool"
            ], className="text-primary mt-3 mb-2"),
            html.P("Select channels and watch the plot update in real-time!", className="text-muted"),
            html.Hr()
        ])
    ]),

    dbc.Row([
        # Left: Channel selection
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([html.I(className="fas fa-list me-2"), "Select Channels"], className="mb-0"),
                    dbc.Button("Clear All", id='clear-all', size='sm', color='secondary', className='float-end')
                ]),
                dbc.CardBody([
                    create_channel_list_by_category(hierarchy)
                ], style={'maxHeight': '75vh', 'overflowY': 'auto'})
            ])
        ], width=3),

        # Right: Plot and controls
        dbc.Col([
            # Controls
            dbc.Card([
                dbc.CardHeader(html.H6([html.I(className="fas fa-sliders me-2"), "Settings"], className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Start Date", className="small fw-bold"),
                            dcc.DatePickerSingle(
                                id='start-date',
                                date=min_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date()
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("End Date", className="small fw-bold"),
                            dcc.DatePickerSingle(
                                id='end-date',
                                date=max_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date()
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Bucket", className="small fw-bold"),
                            dcc.Dropdown(
                                id='bucket',
                                options=[{'label': k, 'value': k} for k in bucket_options],
                                value='1 Day',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Aggregation", className="small fw-bold"),
                            dcc.Dropdown(
                                id='agg',
                                options=[
                                    {'label': 'Mean', 'value': 'mean'},
                                    {'label': 'Sum', 'value': 'sum'},
                                    {'label': 'Min', 'value': 'min'},
                                    {'label': 'Max', 'value': 'max'}
                                ],
                                value='mean',
                                clearable=False
                            )
                        ], width=3)
                    ])
                ])
            ], className="mb-3"),

            # Plot
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        dcc.Graph(id='plot', style={'height': '600px'}, config={'displayModeBar': True}),
                        type='circle'
                    )
                ])
            ])
        ], width=9)
    ])
], fluid=True, style={'backgroundColor': '#f8f9fa', 'padding': '20px'})


@app.callback(
    Output({'type': 'channel-checkbox', 'channel': ALL}, 'value'),
    Input('clear-all', 'n_clicks'),
    prevent_initial_call=True
)
def clear_all_selections(n_clicks):
    """Clear all checkbox selections."""
    return [False] * len(ctx.outputs_list)


@app.callback(
    Output('plot', 'figure'),
    Input({'type': 'channel-checkbox', 'channel': ALL}, 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('bucket', 'value'),
    Input('agg', 'value'),
    State({'type': 'channel-checkbox', 'channel': ALL}, 'id')
)
def update_plot(checkbox_values, start_date, end_date, bucket, agg, checkbox_ids):
    """Update plot based on selected channels."""

    # Get selected channels
    selected = [checkbox_ids[i]['channel'] for i, val in enumerate(checkbox_values) if val]

    # Empty state
    if not selected:
        fig = go.Figure()
        fig.add_annotation(
            text="Select channels from the left to start visualizing",
            xref="paper", yref="paper", x=0.5, y=0.5,
            showarrow=False, font=dict(size=18, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=600
        )
        return fig

    # Prepare data
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)
    bucket_freq = analysis.BUCKET_SIZES.get(bucket)

    plot_data = analysis.prepare_plot_data(
        df=raw_data,
        channels=selected,
        start_date=start_dt,
        end_date=end_dt,
        bucket_size=bucket_freq,
        agg_method=agg
    )

    # Create figure
    fig = go.Figure()

    for i, channel in enumerate(selected):
        if channel in plot_data.columns:
            metadata = db.get_channel_info(channel)
            label = f"{metadata['hierarchy']} ({metadata['unit']})" if metadata else channel
            color = COLORS[i % len(COLORS)]

            fig.add_trace(go.Scatter(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                mode='lines+markers',
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=3),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

    # Layout
    fig.update_layout(
        template='plotly_white',
        title=dict(text='Timeseries Visualization', x=0.5, xanchor='center'),
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=600,
        margin=dict(l=60, r=40, t=80, b=60)
    )

    fig.update_xaxes(showgrid=True, gridcolor='#e9ecef')
    fig.update_yaxes(showgrid=True, gridcolor='#e9ecef')

    return fig


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 EPIC TIMESERIES TOOL - FAST & SIMPLE EDITION")
    print("=" * 60)
    print(f"📊 {len(all_channels)} channels ready")
    print(f"📅 {min_date.date()} to {max_date.date()}")
    print("🌐 http://127.0.0.1:8050")
    print("=" * 60)
    print("\n💡 Select channels with checkboxes - plot updates instantly!\n")

    app.run_server(debug=False, port=8050, host='127.0.0.1')

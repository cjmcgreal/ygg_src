"""
Epic Drag-and-Drop Timeseries Visualization Tool - V2
Built with Plotly Dash for real-time interactivity

This version uses proper drag-and-drop with instant plot updates!

Run with: python app_v2.py
"""

import dash
from dash import dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import json

# Import our data layers
from src.timeseries import timeseries_db as db
from src.timeseries import timeseries_analysis as analysis

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

app.title = "⚡ Epic Timeseries Tool"

# Load initial data
hierarchy = db.get_channel_hierarchy()
all_channels = db.get_channel_list()
min_date, max_date = db.get_date_range()
bucket_options = list(analysis.BUCKET_SIZES.keys())

# Color palette
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]


def create_channel_tree_by_category(hierarchy):
    """Create accordion with draggable channels."""
    accordion_items = []

    for category, content in hierarchy.items():
        # Recursively get all channels for this category
        channels = []
        get_all_channels_recursive(content, category, channels)

        # Create channel items
        channel_divs = []
        for path, channel_id, unit in channels:
            channel_div = html.Div([
                html.I(className="fas fa-grip-vertical me-2", style={'color': '#6c757d'}),
                html.Span(path, className="fw-bold"),
                html.Span(f" ({unit})", className="text-muted ms-1 small"),
            ],
            id=channel_id,
            draggable='true',
            className='draggable-channel',
            style={
                'cursor': 'grab',
                'padding': '8px 12px',
                'marginBottom': '6px',
                'backgroundColor': '#ffffff',
                'border': '1px solid #dee2e6',
                'borderRadius': '6px',
                'transition': 'all 0.2s',
                'userSelect': 'none'
            })
            channel_divs.append(channel_div)

        accordion_item = dbc.AccordionItem(
            html.Div(channel_divs, style={'padding': '8px'}),
            title=f"📁 {category}",
            item_id=f"category-{category}"
        )
        accordion_items.append(accordion_item)

    return dbc.Accordion(
        accordion_items,
        start_collapsed=False,
        always_open=True,
        flush=True
    )


def get_all_channels_recursive(hierarchy_node, parent_path, result):
    """Recursively extract all channels from hierarchy."""
    for key, value in hierarchy_node.items():
        current_path = f"{parent_path}/{key}" if parent_path else key

        if isinstance(value, dict) and 'channel' in value:
            # Leaf node
            display_path = '/'.join(current_path.split('/')[1:])  # Remove top level
            result.append((display_path, value['channel'], value['unit']))
        else:
            # Branch - recurse
            get_all_channels_recursive(value, current_path, result)


# Layout
app.layout = dbc.Container([
    # Title
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-bolt me-3", style={'color': '#ffc107'}),
                "Epic Timeseries Visualization Tool"
            ], className="text-primary mt-4 mb-2"),
            html.P("Drag and drop channels to visualize your data in real-time", className="text-muted"),
            html.Hr()
        ])
    ]),

    # Main content
    dbc.Row([
        # Left sidebar - Channel tree
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-folder-tree me-2"),
                        "Available Channels"
                    ], className="mb-0"),
                    html.Small("Drag channels to plot →", className="text-muted d-block mt-1")
                ]),
                dbc.CardBody([
                    create_channel_tree_by_category(hierarchy)
                ], style={
                    'maxHeight': '75vh',
                    'overflowY': 'auto',
                    'overflowX': 'hidden'
                })
            ], className="shadow-sm")
        ], width=3),

        # Right side - Plot area
        dbc.Col([
            # Selected channels drop zone
            dbc.Card([
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col([
                            html.H5([
                                html.I(className="fas fa-chart-line me-2"),
                                "Selected Channels"
                            ], className="mb-0")
                        ], width=8),
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-trash me-1"),
                                "Clear"
                            ],
                            id='clear-btn',
                            color='danger',
                            size='sm',
                            className='float-end',
                            n_clicks=0)
                        ], width=4)
                    ])
                ]),
                dbc.CardBody([
                    html.Div(
                        id='drop-zone',
                        children=[
                            html.Div([
                                html.I(className="fas fa-hand-pointer fa-3x mb-3", style={'color': '#adb5bd'}),
                                html.P("Drop channels here", className="text-muted h5")
                            ], className="text-center", style={'padding': '30px 0'})
                        ],
                        style={
                            'minHeight': '120px',
                            'border': '3px dashed #dee2e6',
                            'borderRadius': '8px',
                            'padding': '15px',
                            'backgroundColor': '#f8f9fa',
                            'transition': 'all 0.3s'
                        }
                    )
                ])
            ], className="mb-3 shadow-sm"),

            # Plot controls
            dbc.Card([
                dbc.CardHeader([
                    html.H6([
                        html.I(className="fas fa-sliders me-2"),
                        "Plot Settings"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Start Date", className="fw-bold small mb-1"),
                            dcc.DatePickerSingle(
                                id='start-date',
                                date=min_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date(),
                                display_format='YYYY-MM-DD'
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("End Date", className="fw-bold small mb-1"),
                            dcc.DatePickerSingle(
                                id='end-date',
                                date=max_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date(),
                                display_format='YYYY-MM-DD'
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Time Bucket", className="fw-bold small mb-1"),
                            dcc.Dropdown(
                                id='bucket-size',
                                options=[{'label': k, 'value': k} for k in bucket_options],
                                value='1 Day',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Aggregation", className="fw-bold small mb-1"),
                            dcc.Dropdown(
                                id='agg-method',
                                options=[
                                    {'label': 'Mean', 'value': 'mean'},
                                    {'label': 'Sum', 'value': 'sum'},
                                    {'label': 'Min', 'value': 'min'},
                                    {'label': 'Max', 'value': 'max'},
                                    {'label': 'Median', 'value': 'median'}
                                ],
                                value='mean',
                                clearable=False
                            )
                        ], width=3)
                    ])
                ], className="p-3")
            ], className="mb-3 shadow-sm"),

            # Plot
            dbc.Card([
                dbc.CardBody([
                    dcc.Loading(
                        dcc.Graph(
                            id='main-plot',
                            style={'height': '500px'},
                            config={
                                'displayModeBar': True,
                                'displaylogo': False,
                                'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                            }
                        ),
                        type='default'
                    )
                ], className="p-2")
            ], className="shadow-sm")
        ], width=9)
    ]),

    # Hidden divs for state management
    html.Div(id='drop-trigger', style={'display': 'none'}),
    dcc.Interval(id='interval', interval=200, n_intervals=0),  # Check for drops every 200ms
    dcc.Store(id='selected-channels', data=[])

], fluid=True, style={'backgroundColor': '#f0f2f5', 'minHeight': '100vh', 'padding': '20px'})


# Callback to detect dropped channels
app.clientside_callback(
    """
    function(n_intervals) {
        const triggerDiv = document.getElementById('drop-trigger');
        if (triggerDiv && window.droppedChannels) {
            return window.droppedChannels;
        }
        return [];
    }
    """,
    Output('selected-channels', 'data'),
    Input('interval', 'n_intervals')
)


# Callback to clear channels
app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0 && window.clearAllChannels) {
            window.clearAllChannels();
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('clear-btn', 'n_clicks'),
    Input('clear-btn', 'n_clicks')
)


@app.callback(
    Output('drop-zone', 'children'),
    Input('selected-channels', 'data')
)
def update_drop_zone(selected_channels):
    """Update the drop zone display with selected channels."""
    if not selected_channels or len(selected_channels) == 0:
        return html.Div([
            html.I(className="fas fa-hand-pointer fa-3x mb-3", style={'color': '#adb5bd'}),
            html.P("Drop channels here", className="text-muted h5")
        ], className="text-center", style={'padding': '30px 0'})

    # Create badges for selected channels
    badges = []
    for i, channel_id in enumerate(selected_channels):
        metadata = db.get_channel_info(channel_id)
        if metadata:
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
            badge = dbc.Badge([
                html.Span(metadata['hierarchy'], className="me-2"),
                html.I(
                    className="fas fa-times",
                    id={'type': 'remove-btn', 'channel': channel_id},
                    n_clicks=0,
                    style={'cursor': 'pointer', 'marginLeft': '4px'}
                )
            ],
            color="primary",
            className="me-2 mb-2",
            style={
                'padding': '8px 12px',
                'fontSize': '0.9rem',
                'backgroundColor': color,
                'border': 'none'
            })
            badges.append(badge)

    return html.Div(badges, style={'padding': '10px'})


@app.callback(
    Output('interval', 'disabled'),
    Input({'type': 'remove-btn', 'channel': dash.dependencies.ALL}, 'n_clicks'),
    State('selected-channels', 'data'),
    prevent_initial_call=True
)
def remove_channel(n_clicks_list, selected_channels):
    """Remove a channel when X is clicked."""
    if not ctx.triggered:
        return False

    # Get the channel ID from the triggered button
    triggered_id = ctx.triggered_id
    if triggered_id and isinstance(triggered_id, dict):
        channel_to_remove = triggered_id['channel']

        # Call JavaScript function to remove channel
        # This is done via clientside callback
        app.clientside_callback(
            f"""
            function(n) {{
                if (window.removeChannel) {{
                    window.removeChannel('{channel_to_remove}');
                }}
                return window.dash_clientside.no_update;
            }}
            """,
            Output('drop-trigger', 'data-remove'),
            Input({'type': 'remove-btn', 'channel': channel_to_remove}, 'n_clicks')
        )

    return False


@app.callback(
    Output('main-plot', 'figure'),
    Input('selected-channels', 'data'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('bucket-size', 'value'),
    Input('agg-method', 'value')
)
def update_plot(selected_channels, start_date, end_date, bucket_size, agg_method):
    """Update plot instantly when channels are dropped or settings change."""

    # Empty state
    if not selected_channels or len(selected_channels) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="Drag and drop channels to start visualizing",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, color="#adb5bd")
        )
        fig.update_layout(
            template='plotly_white',
            paper_bgcolor='#f8f9fa',
            plot_bgcolor='#ffffff',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=500,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        return fig

    # Convert dates
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    # Load and prepare data
    raw_data = db.load_timeseries_data()
    bucket_freq = analysis.BUCKET_SIZES.get(bucket_size)

    plot_data = analysis.prepare_plot_data(
        df=raw_data,
        channels=selected_channels,
        start_date=start_dt,
        end_date=end_dt,
        bucket_size=bucket_freq,
        agg_method=agg_method
    )

    # Create figure
    fig = go.Figure()

    for i, channel in enumerate(selected_channels):
        if channel in plot_data.columns:
            metadata = db.get_channel_info(channel)
            label = f"{metadata['hierarchy']} ({metadata['unit']})" if metadata else channel
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]

            fig.add_trace(go.Scatter(
                x=plot_data['timestamp'],
                y=plot_data[channel],
                mode='lines+markers',
                name=label,
                line=dict(color=color, width=2.5),
                marker=dict(size=4, color=color),
                hovertemplate='<b>%{fullData.name}</b><br>%{x|%Y-%m-%d %H:%M}<br>Value: %{y:.2f}<extra></extra>'
            ))

    # Update layout
    fig.update_layout(
        template='plotly_white',
        title=dict(
            text='Real-Time Timeseries Visualization',
            x=0.5,
            xanchor='center',
            font=dict(size=22, color='#1f77b4', family='Arial Black')
        ),
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#dee2e6',
            borderwidth=1
        ),
        height=500,
        margin=dict(l=60, r=40, t=80, b=60),
        paper_bgcolor='#ffffff',
        plot_bgcolor='#f8f9fa'
    )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#e9ecef',
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#e9ecef',
        zeroline=False
    )

    return fig


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀  EPIC TIMESERIES VISUALIZATION TOOL - DRAG & DROP EDITION")
    print("=" * 70)
    print(f"📊  Loaded {len(all_channels)} channels from {len(hierarchy)} categories")
    print(f"📅  Date range: {min_date.date()} to {max_date.date()}")
    print(f"🎯  Features: Real-time drag-and-drop | Interactive plots | Live updates")
    print("=" * 70)
    print("🌐  Opening at: http://127.0.0.1:8050")
    print("=" * 70)
    print("\n💡  TIP: Drag channels from the left panel and drop them on the plot area!")
    print("     The plot updates instantly as you drag and drop.\n")

    app.run_server(debug=True, port=8050, host='127.0.0.1', use_reloader=False)

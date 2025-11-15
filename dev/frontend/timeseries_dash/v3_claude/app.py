"""
Epic Drag-and-Drop Timeseries Visualization Tool
Built with Plotly Dash for real-time interactivity

Run with: python app.py
"""

import dash
from dash import dcc, html, Input, Output, State, ALL, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Import our data layers
from src.timeseries import timeseries_db as db
from src.timeseries import timeseries_analysis as analysis

# Initialize the Dash app with Bootstrap theme
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

# Color palette for channels
COLOR_PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]


def create_channel_tree_items(hierarchy, path="", level=0):
    """
    Recursively create collapsible tree items for the channel hierarchy.

    Returns list of dbc.AccordionItem components.
    """
    items = []

    for key, value in hierarchy.items():
        current_path = f"{path}/{key}" if path else key

        # Check if this is a leaf node (channel)
        if isinstance(value, dict) and 'channel' in value:
            # Leaf node - create draggable channel item
            channel_id = value['channel']
            channel_card = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.I(className="fas fa-chart-line me-2"),
                        html.Span(f"{key}", className="fw-bold"),
                        html.Span(f" ({value['unit']})", className="text-muted ms-1"),
                    ],
                    id={'type': 'channel-item', 'channel': channel_id},
                    draggable='true',
                    className='draggable-channel p-2',
                    style={
                        'cursor': 'grab',
                        'borderRadius': '4px',
                        'marginBottom': '4px',
                        'backgroundColor': '#f8f9fa'
                    })
                ], className="p-1")
            ], className="mb-1", style={'border': 'none'})

            items.append(channel_card)
        else:
            # Branch node - recurse
            sub_items = create_channel_tree_items(value, current_path, level + 1)
            items.extend(sub_items)

    return items


def create_tree_by_category(hierarchy):
    """Create accordion with top-level categories."""
    accordion_items = []

    for category, content in hierarchy.items():
        # Get all channel items for this category
        channel_items = create_channel_tree_items({category: content})

        accordion_item = dbc.AccordionItem(
            html.Div(channel_items),
            title=f"📁 {category}",
            item_id=f"category-{category}"
        )
        accordion_items.append(accordion_item)

    accordion = dbc.Accordion(
        accordion_items,
        start_collapsed=False,
        always_open=True,
        flush=True
    )

    return accordion


# Create the layout
app.layout = dbc.Container([
    # Title
    dbc.Row([
        dbc.Col([
            html.H1([
                html.I(className="fas fa-bolt me-3"),
                "Epic Timeseries Visualization Tool"
            ], className="text-primary mt-4 mb-3"),
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
                    html.Small("Drag channels to the plot area →", className="text-muted d-block mt-1")
                ]),
                dbc.CardBody([
                    create_tree_by_category(hierarchy)
                ], style={'maxHeight': '70vh', 'overflowY': 'auto'})
            ])
        ], width=3),

        # Right side - Plot area
        dbc.Col([
            # Drop zone for selected channels
            dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-chart-area me-2"),
                        "Selected Channels"
                    ], className="mb-0 d-inline-block"),
                    dbc.Button(
                        [html.I(className="fas fa-trash me-2"), "Clear All"],
                        id='clear-all-btn',
                        color='danger',
                        size='sm',
                        className='float-end'
                    )
                ]),
                dbc.CardBody([
                    html.Div(
                        id='drop-zone',
                        children=[
                            html.Div([
                                html.I(className="fas fa-hand-pointer fa-3x mb-3 text-muted"),
                                html.P("Drag channels here to visualize", className="text-muted")
                            ], className="text-center p-5")
                        ],
                        style={
                            'minHeight': '100px',
                            'border': '2px dashed #dee2e6',
                            'borderRadius': '8px',
                            'padding': '10px'
                        }
                    )
                ], className="p-2")
            ], className="mb-3"),

            # Plot controls
            dbc.Card([
                dbc.CardHeader(html.H6([
                    html.I(className="fas fa-sliders me-2"),
                    "Plot Settings"
                ], className="mb-0")),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Start Date", className="fw-bold small"),
                            dcc.DatePickerSingle(
                                id='start-date',
                                date=min_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date(),
                                display_format='YYYY-MM-DD',
                                className='w-100'
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("End Date", className="fw-bold small"),
                            dcc.DatePickerSingle(
                                id='end-date',
                                date=max_date.date(),
                                min_date_allowed=min_date.date(),
                                max_date_allowed=max_date.date(),
                                display_format='YYYY-MM-DD',
                                className='w-100'
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Time Bucket", className="fw-bold small"),
                            dcc.Dropdown(
                                id='bucket-size',
                                options=[{'label': k, 'value': k} for k in bucket_options],
                                value='1 Day',
                                clearable=False
                            )
                        ], width=3),
                        dbc.Col([
                            html.Label("Aggregation", className="fw-bold small"),
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
                ])
            ], className="mb-3"),

            # Plot area
            dbc.Card([
                dbc.CardBody([
                    dcc.Graph(
                        id='main-plot',
                        style={'height': '500px'},
                        config={'displayModeBar': True, 'displaylogo': False}
                    )
                ])
            ])
        ], width=9)
    ]),

    # Hidden div to store selected channels
    dcc.Store(id='selected-channels', data=[]),

], fluid=True, className="p-4", style={'backgroundColor': '#f8f9fa'})


# JavaScript for drag and drop functionality
app.clientside_callback(
    """
    function(n_clicks) {
        // Set up drag and drop event listeners
        document.addEventListener('dragstart', function(e) {
            if (e.target.classList.contains('draggable-channel')) {
                const channelData = e.target.id;
                e.dataTransfer.setData('text/plain', channelData);
                e.target.style.opacity = '0.5';
            }
        });

        document.addEventListener('dragend', function(e) {
            if (e.target.classList.contains('draggable-channel')) {
                e.target.style.opacity = '1';
            }
        });

        const dropZone = document.getElementById('drop-zone');
        if (dropZone) {
            dropZone.addEventListener('dragover', function(e) {
                e.preventDefault();
                e.currentTarget.style.backgroundColor = '#e3f2fd';
            });

            dropZone.addEventListener('dragleave', function(e) {
                e.currentTarget.style.backgroundColor = '';
            });

            dropZone.addEventListener('drop', function(e) {
                e.preventDefault();
                e.currentTarget.style.backgroundColor = '';
                const data = e.dataTransfer.getData('text/plain');

                // Trigger callback by updating a hidden element
                const event = new CustomEvent('channelDropped', {detail: data});
                document.dispatchEvent(event);
            });
        }

        return window.dash_clientside.no_update;
    }
    """,
    Output('drop-zone', 'data-drag-setup'),
    Input('drop-zone', 'id')
)


@app.callback(
    Output('selected-channels', 'data'),
    Input('drop-zone', 'n_clicks'),
    Input('clear-all-btn', 'n_clicks'),
    State('selected-channels', 'data'),
    prevent_initial_call=True
)
def update_selected_channels(drop_clicks, clear_clicks, current_channels):
    """Update the list of selected channels."""
    if ctx.triggered_id == 'clear-all-btn':
        return []

    return current_channels


@app.callback(
    Output('drop-zone', 'children'),
    Input('selected-channels', 'data')
)
def render_selected_channels(selected_channels):
    """Render the selected channels in the drop zone."""
    if not selected_channels:
        return html.Div([
            html.I(className="fas fa-hand-pointer fa-3x mb-3 text-muted"),
            html.P("Drag channels here to visualize", className="text-muted")
        ], className="text-center p-5")

    channel_badges = []
    for i, channel in enumerate(selected_channels):
        metadata = db.get_channel_info(channel)
        if metadata:
            color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
            badge = dbc.Badge([
                html.Span(f"{metadata['hierarchy']}", className="me-2"),
                html.I(className="fas fa-times",
                       id={'type': 'remove-channel', 'channel': channel},
                       style={'cursor': 'pointer'})
            ], color="primary", className="me-2 mb-2 p-2",
            style={'backgroundColor': color})
            channel_badges.append(badge)

    return html.Div(channel_badges)


@app.callback(
    Output('main-plot', 'figure'),
    Input('selected-channels', 'data'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('bucket-size', 'value'),
    Input('agg-method', 'value')
)
def update_plot(selected_channels, start_date, end_date, bucket_size, agg_method):
    """Update the plot based on selected channels and settings."""

    # Create empty figure if no channels selected
    if not selected_channels:
        fig = go.Figure()
        fig.add_annotation(
            text="Add channels to start visualizing data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20, color="gray")
        )
        fig.update_layout(
            template='plotly_white',
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=500
        )
        return fig

    # Convert dates to datetime
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
                mode='lines',
                name=label,
                line=dict(color=color, width=2),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>%{y:.2f}<extra></extra>'
            ))

    # Update layout
    fig.update_layout(
        template='plotly_white',
        title=dict(
            text='Timeseries Visualization',
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        xaxis_title='Time',
        yaxis_title='Value',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=500,
        margin=dict(l=60, r=40, t=80, b=60)
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting Epic Timeseries Visualization Tool")
    print("=" * 60)
    print(f"📊 Loaded {len(all_channels)} channels")
    print(f"📅 Date range: {min_date.date()} to {max_date.date()}")
    print("🌐 Opening browser at http://127.0.0.1:8050")
    print("=" * 60)
    app.run_server(debug=True, port=8050)

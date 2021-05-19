from os import supports_bytes_environ
from backend.backend import BackendBase
import ai
from dash import Dash
from flask import current_app as app
import dash_html_components as html
import dash_core_components as dcc  

dash_app = None

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    
    global dash_app
    
    tables = app._backend.get_tables()
    table_options = [{'label': table, 'value': table} for table in tables]

    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/css/dash.css',
            '/static/css/style.css',
        ]
    )

    dash_app.layout = html.Div([
        dcc.Store(id='files_uploaded'),
        html.Div(className="div-header center-items", children=[
            html.A(href='/', children=[
                html.Img(src='/static/img/cogitel-logo.png')
            ])
        ]),
        html.Div(className="dash-container", children=[
            html.Div(id="backend-status-div", children=[
                html.Div(className="backend-status", id="status-db", children=''),
                html.Div(className="backend-status", id="status-ai", children=''),
                html.Div(className="backend-status", id='output-data-upload', children=''),
            ]),
            html.Div(id='dash-chart', children=[
                html.Div(className='chart-btn-list', children=[
                    dcc.Upload(id='upload-data', className='button-square', children=[
                        html.Span(className="btn-square-span", children='Upload data')
                    ]),
                    html.Button(className="button-square", id='update-chart-btn', children=[
                        html.Span(className="btn-square-span", children='Update chart')
                    ]),
                ]),
                dcc.Graph(id="line-chart"),
                dcc.Graph(id="box-plot")
            ]),
        ]),
    ])

    from . import callbacks

    return dash_app.server
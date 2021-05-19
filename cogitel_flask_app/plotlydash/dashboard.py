from backend.backend import BackendBase
import ai
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc

def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    global dash_app
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
            html.Div(id='dash-chart', children=[
                html.Div(className='chart-btn-list', children=[
                    dcc.Upload(id='upload-data', className='button-square', children=[
                        html.Span(className="btn-square-span", children='Upload data')
                    ]),
                    html.Div(id='output-data-upload', children=''),
                    html.Button(className="button-square", id='update-chart-btn', children=[
                        html.Span(className="btn-square-span", children='Update chart')
                    ]),
                ]),
                dcc.Graph(id="line-chart"),
                dcc.Graph(id="box-plot")
            ]),
        ]),
        dcc.Dropdown(
            id='ai_dropdown',
            options=[],
            value=[]
        ),
        html.Div(id='Ai_dropdown'),
        dcc.Dropdown(
            id='table_dropdown',
            options=table_options,
            value=table_options[0]['value']
        ),
        html.Div(id='Table_dropdown')
    ])

    from . import callbacks

    return dash_app.server
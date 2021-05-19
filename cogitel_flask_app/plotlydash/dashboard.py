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
        dcc.ConfirmDialog(
            id='confirm-ai-trained',
            message='Do you want to save the newly trained AI?',
        ),
        html.Dialog(id="a-fooken-dialog"),
        dcc.Store(id='files_uploaded'),
        html.Div(className="div-header center-items", children=[
            html.A(id='logo', href='/', children=[
                html.Img(id="bugitel-logo", src='/static/img/cogitel-logo.png')
            ])
        ]),
        html.Div(className="dash-container", children=[
            html.Button(id="bugitel-report", className="button-square", children=[ # TODO: Bugitel no pls :(
                html.Span(className="btn-square-span", children='Bug report')
            ]),
            html.Button(id="button-train-ai", className="button-square", children=[
                html.Span(className="btn-square-span", children='Train AI')
            ]),
            html.Div(id="backend-status-div", children=[
                html.Div(className="backend-status", id="status-db", children=''),
                html.Div(className="backend-status", id="status-ai", children=''),
                html.Div(className="backend-status", id='output-data-upload', children=''),
                html.Div(className="backend-status", id='output-ai-save', children=''),
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
            ]),
            html.Div(className='dropdown-menus', children=[
                html.Div([
                    dcc.Dropdown(
                        id='table-dropdown',
                        options= [{'label': table, 'value': table} for table in app._backend.get_tables()],
                        value = app._backend.get_tables()[0]
                        ),
                    html.Button(className="button-square", id='table-accept-btn', children=[
                            html.Span(className="btn-square-span", children='Load table')
                        ]),
                ]),
                html.Div([
                    dcc.Dropdown(
                        id='ai-dropdown',
                        options= [{'label': a, 'value': f'./ai/saved_models/{a}'} for a in ai.get_ai_names()],
                        value = ai.get_ai_names()[0]
                        ),
                    html.Button(className="button-square", id='ai-accept-btn', children=[
                            html.Span(className="btn-square-span ai-accept-btn", children='Load ai')
                        ]),
                ]),
            ]),
            dcc.Graph(id="line-chart"),
            dcc.Graph(id="box-plot")
        ]),
    ])

    from . import callbacks

    return dash_app.server
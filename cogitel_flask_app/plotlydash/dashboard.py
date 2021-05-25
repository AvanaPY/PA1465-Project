from os import supports_bytes_environ
from backend.backend import BackendBase
import ai
from dash import Dash
from flask import current_app as app
import dash_html_components as html
import dash_core_components as dcc  

dash_app = None

DROPDOWN_STYLE = {
    "width":"14em",
}

def get_first_table():
    tables = app._backend.get_tables()
    if len(tables) == 0:
        return ''
    return tables[0]

def generate_table_dropdown_labels():
    tables = app._backend.get_tables()
    return [{'label': table, 'value': table} for table in tables]

def generate_ai_dropdown_labels():
    ai_names = ai.get_ai_names()
    return [{'label': a, 'value': a} for a in ai_names]

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
        dcc.ConfirmDialog(
            id='confirm-ai-trained',
            message='Do you want to save the newly trained AI?',
        ),
        html.Dialog(id="a-fooken-dialog"),
        dcc.Store(id='files_uploaded'),
        html.Div(className="div-header center-items", children=[
            html.A(id='logo', href='/', children=[
                html.Img(id="cugitel-logo", src='/static/img/cogitel-logo.png')
            ])
        ]),
        html.Div(className="dash-container", children=[
            html.Div(className="backend-status-div", children=[
                html.Div(className="backend-status-list", children=[
                    html.Div(className="backend-status-sublist", children=[
                        html.Div(className="backend-status", id="status-db", children=''),
                        html.Div(className="backend-status", id="status-ai", children=''),
                        html.Div(className="backend-status", id='output-data-upload', children='Data backend output'),
                        html.Div(className="backend-status", id='output-ai-save', children='AI backend output'),
                        html.Div(className="backend-status", id='button-drop-table-output', children='Drop down table output'),
                        html.Div(className="backend-status", id='output-reclassify', children='Reclassify output'),
                    ])
                ]),
            ]),
            html.Div(className='chart-btn-list', children=[
                dcc.Upload(className='button-square', id='upload-data', children=[
                    html.Span(className="btn-square-span", children='Upload data')
                ]),
                html.Button(className="button-square", id='update-chart-btn', children=[
                    html.Span(className="btn-square-span", children='Update chart')
                ]),
                html.Button(className="button-square", id="button-train-ai", children=[
                    html.Span(className="btn-square-span", children='Train AI')
                ]),
                html.Button(className="button-square", id="button-drop-table", children=[
                    html.Span(className="btn-square-span", children='Drop table')
                ]),
                html.Button(className="button-square", id="button-classify-database", children=[
                    html.Span(className="btn-square-span", children='Reclassify')
                ]),
            ]),
            html.Div(className='dropdown-menus', children=[
                html.Div(className='dropdown-select', children=[
                    dcc.Dropdown(
                        id='table-dropdown',
                        options= generate_table_dropdown_labels(),
                        value = get_first_table(),
                        style=DROPDOWN_STYLE
                    ),
                    html.Button(className="button-square", id='button-load-table', children=[
                            html.Span(className="btn-square-span", children='Load table')
                        ]),
                ]),
                html.Div(className='dropdown-select', children=[
                    dcc.Dropdown(
                        id='ai-dropdown',
                        options = generate_ai_dropdown_labels(),
                        value = app._backend._ai_model_name,
                        style=DROPDOWN_STYLE
                    ),
                    html.Button(className="button-square", id='button-load-ai', children=[
                            html.Span(className="btn-square-span", children='Load ai')
                        ]),
                ]),
            ]),
            dcc.Graph(id="line-chart", className="graph-plot"),
            dcc.Graph(id="box-plot", className="graph-plot")
        ]),
    ])

    from . import callbacks

    return dash_app.server
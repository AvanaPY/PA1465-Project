from dash import Dash
import dash_html_components as html
import dash_core_components as dcc  

dash_app = None
def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    global dash_app
    dash_app = Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            #'/static/css/style.css',
        ]
    )

    # Create Dash Layout
    dash_app.layout = html.Div(id='dash-container')

    dash_app.layout = html.Div([
        html.Div(id='container', children=[
            html.Button(id='update-chart-btn', n_clicks=0, children='Submit'),
            dcc.Graph(id="line-chart")
        ]),
    ])

    from . import callbacks

    return dash_app.server
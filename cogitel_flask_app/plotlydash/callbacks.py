from cogitel_flask_app.plotlydash.dashboard import dash_app
from cogitel_flask_app import App
from cogitel_flask_app import app
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


app : App = app

@dash_app.callback(
    Output("line-chart", "figure"), 
    [Input("update-chart-btn", "n_clicks")])
def update_line_chart(clicks):
    cols = app._backend.get_database_column_names('atable') # TODO: Make this a dropdown option on the website
    data = app._backend.get_all_data('atable', convert_datetime=True)
    dct = {
        col:[] for col in cols
    }
    for tpl in data:
        for col, d in zip(cols, tpl):
            dct[col].append(d)

    anomalies = app._backend._get_all_anomalies('atable')
    anom_dct = {
        col:[] for col in cols
    }
    for tpl in anomalies:
        for col, d in zip(cols, tpl):
            anom_dct[col].append(d)

    sens_preds = app._backend.get_sensor_prediction_column_name_pairs('atable')
    fig = go.Figure()

    for sensor, pred in sens_preds:
        fig.add_trace(go.Scatter(x=dct['date'], y=dct[sensor], mode='lines',
            name=sensor,
            line=dict(width=1),
            connectgaps=True,
        ))

        fig.add_trace(go.Scatter(x=dct['date'], y=dct[pred], mode='lines',
            name=pred,
            line=dict(width=1),
            connectgaps=True,
        ))
    
        fig.add_trace(go.Scatter(x=anom_dct['date'], y=anom_dct[pred],
                    mode='markers',
                    line=dict(color='rgb(0, 0, 0)', width=8),
                    name=sensor + 'Anoms'))
    return fig
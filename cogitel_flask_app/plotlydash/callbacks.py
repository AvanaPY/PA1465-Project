import ai
from logging import exception

import dash
from cogitel_flask_app.plotlydash.dashboard import dash_app
from cogitel_flask_app import App
from cogitel_flask_app import app
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import base64
import os
import numpy as np

import shutil

BASE_DIR = os.path.dirname(__file__)
upload_dir_path = os.path.join(BASE_DIR, 'web/uploads')
app : App = app

def generate_line_fig(table_name='atable'):
    cols = app._backend.get_database_column_names(table_name) # TODO: Make this a dropdown option on the website
    data = app._backend.get_all_data(table_name, convert_datetime=True)
    dct = {
        col:[] for col in cols
    }
    for tpl in data:
        for col, d in zip(cols, tpl):
            dct[col].append(d)

    anomalies = app._backend._get_all_anomalies(table_name)
    anom_dct = {
        col:[] for col in cols
    }
    for tpl in anomalies:
        for col, d in zip(cols, tpl):
            anom_dct[col].append(d)

    sens_preds = app._backend.get_sensor_prediction_column_name_pairs(table_name)
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

    sensors = app._backend.get_sensor_column_names(table_name)

    for sensor, pred in sens_preds:
        dct[sensor][dct[sensor] == None] = 0
        dct[pred][dct[pred] == None] = 0

        for i, (sv, pv) in enumerate(zip(dct[sensor], dct[pred])):
            if sv is None:
                dct[sensor][i] = 0
            if pv is None:
                dct[pred][i] = dct[sensor][i]

        diff = np.array(dct[sensor]) - np.array(dct[pred])
        dct[f'diff{sensor}'] = diff.astype(float)

    df = pd.DataFrame.from_dict(dct)
    df = df[[f'diff{sensor}' for sensor in sensors]]
    box_fig = px.box(df)  
    return fig, box_fig

@dash_app.callback([Output("line-chart", "figure"),
                    Output("box-plot", "figure")], 
                   [Input("update-chart-btn", "n_clicks")])
def update_line_chart(clicks):
    try:
        line_fig, box_fig = generate_line_fig()
        return line_fig, box_fig
    except Exception as e:
        return go.Figure(), go.Figure()

@dash_app.callback([Output('output-data-upload', 'children'),
                    Output('files_uploaded', 'data')],
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('files_uploaded', 'data'),
              prevent_initial_call=True)
def upload_data(contents, name, clicks):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    fpath = os.path.join(upload_dir_path, name)
    if not os.path.exists(upload_dir_path):
        os.makedirs(upload_dir_path)
    with open(fpath, 'wb') as f:
        f.write(decoded)
    print('Uploading data...')
    try:
        if name.endswith('.json'):
            app._backend.import_data_json(fpath, 'atable', use_historical=False, classify_if_not_exist=False)
        elif name.endswith('.csv'):
            app._backend.import_data_csv(fpath, 'atable', use_historical=False, classify_if_not_exist=False)
        else:
            raise Exception('Unknown extension')
    except Exception as e:
        message = str(e)
    else:
        message = 'Dataset has been received'
    try:
        os.remove(fpath)
    except:
        pass

    print('Uploaded data complete')

    clicks = clicks + 1 if clicks else 1
    return f'({clicks}) {message}', clicks

@dash_app.callback([Output('status-db', 'children'),
                    Output('status-ai', 'children')],
                    Input("update-chart-btn", "n_clicks"))
def update_backend_status_labels(clicks):
    return f'Database loaded: {app._backend._my_db is not None}', f'AI model loaded: {app._backend._load_ai} ({app._backend._ai_model_name})'

# TODO: Bugitel no pls :(
@dash_app.callback([Output('bugitel-logo', 'src')],
                    Input('bugitel-report', 'n_clicks'),
                    prevent_initial_call=True)
def bug_report(clicks):
    return ['/static/img/bugitel.png']

@dash_app.callback([Output('confirm-ai-trained', 'displayed'),
 #                   Output('confirm-ai-trained', 'message'),
                    ],
                    Input('button-train-ai', 'n_clicks'),
                    prevent_initial_call=True)
def train_ai(value, table_name='atable'):
    app._backend.train_ai(table_name, app._backend.get_sensor_column_names(table_name), 
                        save_ai=True, save_ai_path='./ai/saved_models/temp_ai', max_epochs=100, patience=5)
    return [True]#, f'Do you want to save the ai model as {ai_name}?'

@dash_app.callback(Output('output-ai-save', 'children'),
                    Input('confirm-ai-trained', 'submit_n_clicks'),
                    prevent_initial_call=True)
def display_confirm_save_ai_after_train(value, ai_name='temp_ai_saved'):
    npath = f'./ai/saved_models/{ai_name}'
    if os.path.exists(npath):
        shutil.rmtree(npath)
    os.rename('./ai/saved_models/temp_ai', npath)
    return f'AI has been saved as "{ai_name}"'

@dash_app.callback(
    Output('button-load-table', 'value'),
    Input('button-load-table', 'n_clicks'),
    State('table-dropdown', 'value'),
    prevent_initial_call=True,
)
def callback_load_table(n_clicks, tname):
    #line_fig, box_fig = generate_line_fig(table_name=tname[0])
    return tname

@dash_app.callback(
        Output('button-drop-table-output', 'children'),
        Input('button-drop-table', 'n_clicks'),
        State('table-dropdown', 'value'),
        prevent_initial_call=True
)
def callback_drop_table(n_clicks, table_name):
    try:
        app._backend.delete_table(table_name)
        return f'Dropped table "{table_name}".'
    except Exception as e:
        return f'Failed to drop table "{table_name}": {e}'

@dash_app.callback(
    Output('button-load-ai', 'options'),
    [Input('button-load-ai', 'n_clicks')],
    State('ai-dropdown', 'value'),
    prevent_initial_call=True,
)
def callback_load_ai(n_clicks, aname):
    try:
        app._backend.load_ai(aname)
        print(f'Loaded AI model: {aname}')
    except:
        print("Why you try to load fuck shit?")
    return ai.get_ai_names()
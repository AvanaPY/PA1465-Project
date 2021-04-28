import seaborn as sns
import pandas as pd
import plotly.express as px
import ai
import json
import numpy as np
import tensorflow as tf
import math
import plotly.graph_objects as go
import matplotlib.pyplot as plt


def predict_json_file(data_file):
    with open(data_file, "r") as f:
            open_file = json.load(f)
            dates = open_file.keys()
            values = open_file.values()
            new_dict = {"dates": dates, "values": values}
            df = pd.DataFrame(new_dict)
    visualize_df = ai.run_ai(df)
    return visualize_df

def visualize(df_data, shifting):
    df_data_vis = df_data.copy()
    for i in range(shifting):
        df_data_vis.loc[df_data_vis.iloc[-1].name + 1,:] = np.nan #creates a new nan row
    df_data_vis['predictions'] = df_data_vis['predictions'].shift(shifting) #shifts all predictions down
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["predictions"],
                    mode='lines+markers',
                    name='predictions'))
    fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["values"],
                    mode='lines+markers',
                    name='values'))
                
    fig.show()

if __name__ == "__main__":

    if input("Do you want to use a previously saved version?[y/n]") == "n":
        with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
            open_file = json.load(f)
            dates = open_file.keys()
            values = list(open_file.values())
            for index, value in enumerate(values):
                values[index] = index % 5
        new_dict = {"dates": dates, "values": values}
        df = pd.DataFrame(new_dict)
        df.pop("dates")
        
        w2 = ai.create_window(df, input_width=6, label_width = 1, shift=6)

        model = ai.create_ai_model()

        ai.train_ai(model, w2.train, w2.val, max_epochs = 10)

        if input("do you want to save?[y/n]") == "y":
            ai.save_ai_model(model, 'backend/ai/saved_model/my_model')
    else:
        model = ai.load_ai_model('backend/ai/saved_model/my_model')

    value = None
    values = []
    while True:
        value = int(input("vilket värde ska jag gissa på?"))
        values.append(value)
        if len(values) > 5:
            values_dict = {"values": values[-6:]}
            own_df = pd.DataFrame.from_dict(values_dict)
            if len(values) == 6:
                df_data = ai.run_ai(model, own_df, return_full = "yes")
            else:
                df_data = df_data.append(ai.run_ai(model, own_df, return_full = "no"), ignore_index=True)
            print(df_data)
            visualize(df_data, 6)

#visualize_df = export_to_ai("backend/ai/Raspberry_data/temp_dataset_3.json")        

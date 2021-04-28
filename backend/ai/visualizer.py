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

def visualize(df_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_data.index, y=df_data["predictions"],
                    mode='lines+markers',
                    name='lines+markers'))
    fig.add_trace(go.Scatter(x=df_data.index, y=df_data["values"],
                    mode='lines+markers',
                    name='lines+markers'))
                
    #fig = px.line(x=df_data.index, y=df_data["predictions"])
    fig.show()

if __name__ == "__main__":

    if input("Do you want to use a previously saved version?[y/n]") == "n":
        with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
            open_file = json.load(f)
            dates = open_file.keys()
            values = open_file.values()
        new_dict = {"dates": dates, "values": values}
        df = pd.DataFrame(new_dict)
        df.pop("dates")
        
        w2 = ai.create_window(df)

        model = ai.create_ai_model()

        ai.train_ai(model, w2.train, w2.val)

        if input("do you want to save?[y/n]") == "y":
            ai.save_ai_model(model, 'backend/ai/saved_model/my_model')
    else:
        model = ai.load_ai_model('backend/ai/saved_model/my_model')

    """ #DONT KEEP THIS :3
    with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
        open_file = json.load(f)
        dates = open_file.keys()
        values = open_file.values()
    new_dict = {"dates": dates, "values": values}
    df = pd.DataFrame(new_dict)
    df.pop("dates") """

    # plt.hist(df, bins = 13)
    # plt.show()

    value = None
    values = []
    while True:
        value = int(input("vilket värde ska jag gissa på?"))
        values.append(value)
        values_dict = {"values": values}
        own_df = pd.DataFrame.from_dict(values_dict)
        df_data = ai.run_ai(model, own_df)
        print(df_data)
        #if input("do you want to save?[y/n]") == "y":
        visualize(df_data)

#visualize_df = export_to_ai("backend/ai/Raspberry_data/temp_dataset_3.json")        

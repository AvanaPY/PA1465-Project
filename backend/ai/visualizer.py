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
import plotly.io as pio

import random


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
                    mode='markers+lines',
                    name='predicted values'))
    fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["values"],
                    mode='markers+lines',
                    name='real values'))
    
    #pio.write_html(fig, file=’index.html’, auto_open=True) 
    
    fig.show()

def fill_missing_avg(dataset):

    missing_dataset = dataset.isnull()
    index = 0
    for boolean in missing_dataset["Lufttemperatur"]:
        if boolean == True:
            index_a = index - 1
            index_b = index + 1
            while missing_dataset['Lufttemperatur'].iloc[index_a] == True:
                index_a -= 1
            while missing_dataset['Lufttemperatur'].iloc[index_b] == True:
                index_b += 1

            dataset['Lufttemperatur'].iloc[index] = (dataset['Lufttemperatur'].iloc[index_a] + dataset['Lufttemperatur'].iloc[index_b])/2
        index += 1
    return dataset

def generate_interval(number, size, dataset):
    intervals = []
    for i in range(number):
        upperdata = len(dataset["values"]) - size

        random_bound = random.randint(0, upperdata)
        upper_bound = random_bound
        lower_bound = random_bound - size

        interval_data = dataset["values"][lower_bound:upper_bound]
        interval = np.array(interval_data)
        intervals.append(interval)

    return intervals

if __name__ == "__main__":
    INPUT_WIDTH = 2
    SHIFT = 1
    LABEL_WIDTH = 1

    """
    with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
        open_file = json.load(f)
        dates = list(open_file.keys())[:30000]
        values = list(open_file.values())[:30000]
        for index, value in enumerate(values):
            #values[index] = index % 10
            values[index] = round(np.sin(((index * 17 % 360) * np.pi) / 180), 1)
            #values[index] = np.sin(((index * 17 % 360) * np.pi) / 180)
    new_dict = {"dates": dates, "values": values}
    df = pd.DataFrame(new_dict)
    df.pop("dates")
    """
    
    with open("backend/ai/SMHI_Data.csv", "r") as f:
        open_file = pd.read_csv(f)
    df = pd.DataFrame(open_file["Lufttemperatur"])
    df = fill_missing_avg(df)
    df.columns = ["values"]
    

    w2 = ai.create_window(df, input_width=INPUT_WIDTH, label_width = LABEL_WIDTH, shift=SHIFT)
    #print("w2:", list(w2.train)[0])
    if input("Do you want to use a previously saved version?[y/n]") == "n":

        model = ai.create_ai_model()

        ai.train_ai(model, w2.train, w2.val, max_epochs = 10)

        if input("do you want to save?[y/n]") == "y":
            ai.save_ai_model(model, 'backend/ai/saved_model/my_model')
    else:
        model = ai.load_ai_model('backend/ai/saved_model/my_model')

    #create a sample size from data
    #feed the sample data-points one at a time into "values" as if they were inputed
    n = len(df)
    df_train = df = df[0:int(n*0.7)]
    mean = df_train.mean() #meadian
    std = df_train.std() #standard deviation (expecting every data being normal distributed)

    normal_df = (df_train - mean) / std

    while True:

        values_samples = generate_interval(1, 20, normal_df)
        for sample in values_samples:
            value = None
            values = []
            for a in sample:
            #while True:
                #value = float(input("vilket värde ska jag gissa på?"))
                value = a
                values.append(value)
                if len(values) >= INPUT_WIDTH:
                    values_dict = {"values": values[-1 * INPUT_WIDTH +1 -SHIFT:]}
                    own_df = pd.DataFrame.from_dict(values_dict)
                    if len(values) == INPUT_WIDTH:
                        df_data = ai.run_ai(model, own_df, return_full = "yes")
                    else:
                        new_row = ai.run_ai(model, own_df, return_full = "no")
                        if abs(new_row["values"] - new_row["predictions"]) > 1:
                            new_row["anomaly"] = "True"
                        df_data = df_data.append(new_row, ignore_index=True)
            print(df_data)
            visualize(df_data, SHIFT)
        #print(df_data)
        #visualize(df_data, 6) #(only visualizes the data after all data-points in the sample has been done)
        if input("want to try again?[y/n]") == "n":
            break

#visualize_df = export_to_ai("backend/ai/Raspberry_data/temp_dataset_3.json")        

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
import os
import datetime

import random

def visualize(df_datas, shifting):

    fig = go.Figure()

    for i in range(len(df_datas)):
        df_data_vis = df_datas[i].copy()
        
        for i in range(shifting):
            df_data_vis.loc[df_data_vis.iloc[-1].name + 1,:] = np.nan #creates a new nan row
        df_data_vis['predictions'] = df_data_vis['predictions'].shift(shifting) #shifts all predictions down
        
        color1 = ["black", "antiquewhite", "aqua", "aquamarine", "azure",
            "beige", "bisque", "aliceblue", "blanchedalmond", "blue",
            "blueviolet", "brown", "burlywood", "cadetblue",
            "chartreuse", "chocolate", "coral", "cornflowerblue",
            "cornsilk", "crimson", "cyan", "darkblue", "darkcyan",
            "darkgoldenrod", "darkgray", "darkgrey", "darkgreen"]

        fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis[df_data_vis.columns[0]],
                        mode='lines',
                        name="real - " + df_data_vis.columns[0],
                        line=dict(color="black", width=4)))
        
        fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["predictions"],
                        mode='lines',
                        name="pred - " + df_data_vis.columns[0],
                        line=dict(color="magenta", width=4, dash='dot')))
                        #color= i))# *5))

        fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["predictions"],
                        mode='markers',
                        name="anomalies - " + df_data_vis.columns[0],
                        marker_color = "red",
                        opacity=df_data_vis["anom"].tolist()))
    
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

def generate_interval(number, size, dataset, sample_columns = []):
    if sample_columns == True:
        sample_columns = dataset.columns
    intervals = []
    for i in range(number):
        upperdata = len(dataset[dataset.columns[0]]) - size

        random_bound = random.randint(0, upperdata)
        lower_bound = random_bound
        upper_bound = random_bound + size

        if len(sample_columns) != 0:
            interval_data = []

            for column in sample_columns:
                interval_data.append(dataset[column][lower_bound:upper_bound])
        else:
            interval_data = dataset[:][lower_bound:upper_bound]
        #interval_data = dataset["values"][lower_bound:upper_bound]
        interval = np.array(interval_data)
        intervals.append(interval)
    return intervals

def run_sample(model, normal_df, sample_size, shift, input_width, prediction_labes):
    """
        Args::
            model: Ai model to use
            normal_df: 
            label_width: how many predictions the ai does (one at a time)
            shift: how far in the future the prediction(s) are
            label_columns: a list containing what values that should be predicted from the input dataset

        Returns::
            w2: a window object containing training, validation and test data.

        Raises::
        --
    """
    values_sample = generate_interval(1, sample_size, normal_df)[0]

    output, anomaly = ai.run_ai(model, values_sample, shift = shift, input_width = input_width)
    output = output #väljer bara de första dimentioner av output
    anomaly = anomaly #väljer bara de första dimentioner av output

    vis_dict = []
    only_value_sample = generate_interval(1, sample_size, normal_df, sample_columns = True)[0]
    for i in range(len(output)):
        difference = output[i] - only_value_sample[i]
        vis_dict.append({prediction_labes[i]: only_value_sample[i], "predictions": output[i], "dif": difference, "anom": anomaly[i]})
    return vis_dict

def import_tf_special_dataset():
    """
        Downloads and formats a tensorflow weather dataset

        Args::
            --

        Returns::
            df: a dataframe containing all the formated data from the datasource

        Raises::
        --
    """
    dataset = "tf"

    if dataset == "sin":
        with open("ai/Raspberry_data/temp_dataset_3.json", "r") as f:
            open_file = json.load(f)
            dates = list(open_file.keys())[:3000]
            values = list(open_file.values())[:3000]
            values2 = []
            for index, value in enumerate(values):
                #values[index] = index % 10
                values[index] = round(np.sin(((index * 17 % 360) * np.pi) / 180), 1)
                values2.append(index % 10)
                #values[index] = np.sin(((index * 17 % 360) * np.pi) / 180)
        new_dict = {"dates": dates * 2, "values": values * 2, "values2": values2 * 2}
        df = pd.DataFrame(new_dict)
        df.pop("dates")
    
    """
    with open("backend/ai/SMHI_Data.csv", "r") as f:
        open_file = pd.read_csv(f)
    open_file = open_file[-5000:] #enbart de 5000 sista värderna (för att testa om den kan bli superbra även om den overfittas)
    df = pd.DataFrame(open_file["Lufttemperatur"])
    df = fill_missing_avg(df)
    df["values2"] = df["Lufttemperatur"].copy()
    df.columns = ["values", "values2"]
    """

    if dataset == "tf":
        #Tesorflow dataset input
        zip_path = tf.keras.utils.get_file(
            origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip',
            fname='jena_climate_2009_2016.csv.zip',
            extract=True)
        csv_path, _ = os.path.splitext(zip_path)

        df = pd.read_csv(csv_path)
        # slice [start:stop:step], starting from index 5 take every 6th record.
        df = df[5::6]

        date_time = pd.to_datetime(df.pop('Date Time'), format='%d.%m.%Y %H:%M:%S')

        wv = df['wv (m/s)']
        bad_wv = wv == -9999.0
        wv[bad_wv] = 0.0

        max_wv = df['max. wv (m/s)']
        bad_max_wv = max_wv == -9999.0
        max_wv[bad_max_wv] = 0.0

        # The above inplace edits are reflected in the DataFrame
        df['wv (m/s)'].min()

        wv = df.pop('wv (m/s)')
        max_wv = df.pop('max. wv (m/s)')

        # Convert to radians.
        wd_rad = df.pop('wd (deg)')*np.pi / 180

        # Calculate the wind x and y components.
        df['Wx'] = wv*np.cos(wd_rad)
        df['Wy'] = wv*np.sin(wd_rad)

        # Calculate the max wind x and y components.
        df['max Wx'] = max_wv*np.cos(wd_rad)
        df['max Wy'] = max_wv*np.sin(wd_rad)

        timestamp_s = date_time.map(datetime.datetime.timestamp)

        day = 24*60*60
        year = (365.2425)*day

        df['Day sin'] = np.sin(timestamp_s * (2 * np.pi / day))
        df['Day cos'] = np.cos(timestamp_s * (2 * np.pi / day))
        df['Year sin'] = np.sin(timestamp_s * (2 * np.pi / year))
        df['Year cos'] = np.cos(timestamp_s * (2 * np.pi / year))
    

    return df

if __name__ == "__main__":
    tf.get_logger().setLevel('ERROR')

    path = 'ai/saved_models/'
    directory_contents = os.listdir(path)
    print()
    print("~*~ Saved models ~*~")
    for enum, direc in enumerate(directory_contents):
        print(enum + 1, "-", direc)
    print()
    use_saved_input = input("Do you want to use a previously saved version?[y/n]")
    
    if use_saved_input == "n":

        INPUT_WIDTH = int(input("Imput width: "))
        SHIFT = int(input("shift: "))
        LABEL_WIDTH = int(input("Label width: "))
        in_dim = int(input("Input dimentions: "))
        out_dim = int(input("Output dimentions: "))
        
        df = import_tf_special_dataset()
        df = df[df.columns[0:in_dim]]
        prediction_labes = list(df.columns[0:out_dim])

        w2 = ai.create_window(df, input_width=INPUT_WIDTH, label_width = LABEL_WIDTH, shift=SHIFT, label_columns=prediction_labes)
        normal_df = w2.val

        model = ai.create_ai_model(output_dim=out_dim)

        ai.train_ai(model, w2.train, w2.val, max_epochs = 50)

        if input("do you want to save?[y/n]") == "y":
            name = input("what name should the ai_model have: ")
            input_path = 'ai/saved_models/' + name

            ai.save_ai_model(model, input_path, input_width=INPUT_WIDTH, SHIFT=SHIFT, LABEL_WIDTH= LABEL_WIDTH, in_dimentions=in_dim, out_dimentions=out_dim)

    else:
        name = int(input("model number to use: "))
        input_path = 'ai/saved_models/' + directory_contents[name - 1]
        model, INPUT_WIDTH, SHIFT, LABEL_WIDTH, in_dim, out_dim = ai.load_ai_model(input_path)
        
        df = import_tf_special_dataset()
        df = df[df.columns[0:in_dim]]
        prediction_labes = list(df.columns[0:out_dim])

        w2 = ai.create_window(df, input_width=INPUT_WIDTH, label_width = LABEL_WIDTH, shift=SHIFT, label_columns=["p (mbar)",  "values", "Tpot (K)"])
        normal_df = w2.val_df

    while True:
        vis_dicts = run_sample(model, normal_df, sample_size = len(normal_df), shift = SHIFT, input_width = INPUT_WIDTH, prediction_labes = prediction_labes)
        
        result_dfs = []
        supertotal_df = {}
        for enum, vis_dict in enumerate(vis_dicts):
            result_df = pd.DataFrame.from_dict(vis_dict)
            result_dfs.append(result_df)
            
            supertotal_df[prediction_labes[enum]] = abs(result_df["dif"])

        visualize(result_dfs, 0)

        supertotal_df = pd.DataFrame.from_dict(supertotal_df)
        if input("go again?[y/n][g for graf]") == "g":
            fig, ax = plt.subplots()
            ax = sns.boxplot(data=supertotal_df, showfliers=False, orient="h")
            plt.show()
            input("press any key to go again")









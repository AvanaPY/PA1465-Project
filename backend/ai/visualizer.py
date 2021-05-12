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
                    name='predicted values',
                    marker_color=df_data["anom"]))
    fig.add_trace(go.Scatter(x=df_data_vis.index, y=df_data_vis["values"],
                    mode='markers+lines',
                    name='real values'))
    #fig.add_trace(go.Scatter(x=df_data_vis.index, y=abs(df_data_vis["dif"]),
    #                mode='markers+lines',
    #                name='abs difference'))
    #fig.add_trace(go.Scatter(x=df_data_vis.index, y=abs(df_data_vis["anom"]),
    #                mode='markers+lines',
    #                name='anomaly'))
    
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

def generate_interval(number, size, dataset, sample_columns = False):
    intervals = []
    for i in range(number):
        upperdata = len(dataset["values"]) - size

        random_bound = random.randint(0, upperdata)
        lower_bound = random_bound
        upper_bound = random_bound + size

        if sample_columns != False:
            interval_data = []
            for column in sample_columns:
                interval_data.append(dataset[column][lower_bound:upper_bound])
        else:
            interval_data = dataset[:][lower_bound:upper_bound]
        #interval_data = dataset["values"][lower_bound:upper_bound]
        interval = np.array(interval_data)
        intervals.append(interval)
    return intervals

def loop_through_samples(samples_df, num_of_samples = 1, sample_size = 20, all = False, anom_range = 1):

    INPUT_WIDTH = 2
    SHIFT = 1
    LABEL_WIDTH = 1

    if all == True:
        values_samples = [samples_df["values"][-1000:]]
        print(values_samples)
    else:
        values_samples = generate_interval(num_of_samples, sample_size, normal_df)

    for sample in values_samples:
        value = None
        values = []
        for index, a in enumerate(sample):
            if index % 100 == 0 and all == True:
                print(index, "samples done of", len(sample))
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

                    #ai.test_run_ai(model, own_df, return_full = "no")
                    
                    
                    if abs(new_row["values"] - new_row["predictions"]) > anom_range:
                        new_row["anomaly"] = "True"
                        new_row["color"] = "firebrick"
                    else:
                        new_row["color"] = "deepskyblue"
                    df_data = df_data.append(new_row, ignore_index=True)
                           
        df_data_vis = df_data.copy()
        for i in range(SHIFT):
            df_data_vis.loc[df_data_vis.iloc[-1].name + 1,:] = np.nan #creates a new nan row
        df_data_vis['predictions'] = df_data_vis['predictions'].shift(SHIFT) #shifts all predictions down

        print(df_data_vis)
        visualize(df_data, SHIFT)
    return df_data   

def anomaly_range(total_df):
    total_df["dif"] = total_df.eval("values-predictions").abs()
    return total_df

def run_sample(model, normal_df, sample_size, shift):
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

    output, anomaly = ai.run_ai(model, values_sample, shift = shift)

    only_value_sample = generate_interval(1, sample_size, normal_df, sample_columns = ["values"])[0][0]
    difference = output - only_value_sample
    vis_dict = {"values": only_value_sample, "predictions": output, "dif": difference, "anom": anomaly}
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

    fft = tf.signal.rfft(df['T (degC)'])
    f_per_dataset = np.arange(0, len(fft))

    n_samples_h = len(df['T (degC)'])
    hours_per_year = 24*365.2524
    years_per_dataset = n_samples_h/(hours_per_year)

    df = df.rename(columns={'T (degC)': "values"})

    return df

if __name__ == "__main__":
    tf.get_logger().setLevel('ERROR')
    INPUT_WIDTH = 10
    SHIFT = 10
    LABEL_WIDTH = INPUT_WIDTH 

    df = import_tf_special_dataset()
    df = df[["p (mbar)",  "values", "Tpot (K)"]]

    """
    with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
        open_file = json.load(f)
        dates = list(open_file.keys())[:3000]
        values = list(open_file.values())[:3000]
        for index, value in enumerate(values):
            #values[index] = index % 10
            values[index] = round(np.sin(((index * 17 % 360) * np.pi) / 180), 1)
            #values[index] = np.sin(((index * 17 % 360) * np.pi) / 180)
    new_dict = {"dates": dates, "values": values}
    df = pd.DataFrame(new_dict)
    df.pop("dates")
    """
    
    """
    with open("backend/ai/SMHI_Data.csv", "r") as f:
        open_file = pd.read_csv(f)
    open_file = open_file[-5000:] #enbart de 5000 sista värderna (för att testa om den kan bli superbra även om den overfittas)
    df = pd.DataFrame(open_file["Lufttemperatur"])
    df = fill_missing_avg(df)
    df["values2"] = df["Lufttemperatur"].copy()
    df.columns = ["values", "values2"]
    """



    path = 'backend/ai/saved_models/'
    directory_contents = os.listdir(path)
    print()
    print("Saved models: [input width, shift, label width]")
    for enum, direc in enumerate(directory_contents):
        print(enum + 1, " | [", direc, "]", sep = "")
    print()
    use_saved_input = input("Do you want to use a previously saved version?[y/n]")
    
    if use_saved_input == "n":

        INPUT_WIDTH = int(input("Imput width: "))
        SHIFT = int(input("shift: "))
        LABEL_WIDTH = int(input("Label width: "))
        w2 = ai.create_window(df, input_width=INPUT_WIDTH, label_width = LABEL_WIDTH, shift=SHIFT)
        normal_df = w2.val_df

        model = ai.create_ai_model()

        ai.train_ai(model, w2.train, w2.val, max_epochs = 100)

        if input("do you want to save?[y/n]") == "y":
            name = str(INPUT_WIDTH) + ", " + str(SHIFT) + ", " + str(LABEL_WIDTH)
            input_path = 'backend/ai/saved_models/' + name

            ai.save_ai_model(model, input_path)
    else:
        name = int(input("model number to use: "))
        input_path = 'backend/ai/saved_models/' + directory_contents[name - 1]
        model, INPUT_WIDTH, SHIFT, LABEL_WIDTH = ai.load_ai_model(input_path)
        
        print("info:", INPUT_WIDTH, SHIFT, LABEL_WIDTH)
        w2 = ai.create_window(df, input_width=INPUT_WIDTH, label_width = LABEL_WIDTH, shift=SHIFT)
        normal_df = w2.val_df


    while True:
        #vis_dict = run_sample(model, normal_df, sample_size = 10000 , shift= SHIFT) #sample_size = INPUT_WIDTH + SHIFT
        vis_dict = run_sample(model, normal_df, sample_size = len(normal_df) , shift = SHIFT)
        result_df = pd.DataFrame.from_dict(vis_dict)
        print(result_df)

        visualize(result_df, 0)
        #loop_through_samples(normal_df, 1, 50, all = False, anom_range = 0.03) # fix until next time - colors and integrations
        if input("go again?[y/n][g for graf]") == "g":
            fig, ax = plt.subplots()
            N, bins, patches = plt.hist(result_df["dif"], bins = 100)
            plt.show()
            input("press any key to go again")









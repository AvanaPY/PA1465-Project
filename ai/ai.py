import pandas as pd
import numpy as np
import tensorflow as tf
import seaborn as sns
import math
import json
import os

ANOM_VALUE_TRUE = 1
ANOM_VALUE_FALSE = 0

def create_ai_model(output_dim = 1):
    """
        Creates an AI model

        Args::
            --

        Returns::
            Tensorflow AI model

        Raises::
            --
    """
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(50, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        tf.keras.layers.LSTM(100, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        tf.keras.layers.LSTM(50, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        #tf.keras.layers.LSTM(10, return_sequences=True),#, dropout=0.5, recurrent_dropout=0.1),
        tf.keras.layers.Dense(units=70),
        tf.keras.layers.Dense(units=50),
        tf.keras.layers.Dense(units=30),
        tf.keras.layers.Dense(units=output_dim)
    ])

    model.compile(loss=tf.losses.MeanSquaredError(),
                    optimizer=tf.optimizers.Adam(),
                    metrics=[tf.metrics.MeanAbsoluteError()])
    return model

def load_ai_model(load_ai_path):
    """
        Loads the AI model from a file

    Args::
        load_ai_path: str object representing the file path to load the ai from

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when loading the ai model
    """
    model = tf.keras.models.load_model(load_ai_path)

    with open(load_ai_path + '/ai_info.json') as json_file:
        data = json.load(json_file)
        
    INPUT_WIDTH = data["timeframe"][0]["input_width"]
    SHIFT = data["timeframe"][0]["shift"]
    LABEL_WIDTH = data["timeframe"][0]["label_width"]

    IN_DIM = data["dimention"][0]["input_dim"]
    OUT_DIM = data["dimention"][0]["output_dim"]


    return model, INPUT_WIDTH, SHIFT, LABEL_WIDTH, IN_DIM, OUT_DIM

def save_ai_model(model, save_ai_path, INPUT_WIDTH = 1, SHIFT = 1, LABEL_WIDTH = 1, in_dimentions = 1, out_dimentions = 1):
    """
        Saves the AI model into a file

    Args::
        model: A tensorflow AI model
        save_ai_path: str object representing the file path to save the ai model to.

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when saving the ai model
    """
    model.save(save_ai_path)

    # TODO: Save meta-data about AI in a json file
    # Save things such as input size in datapoints, 
    # output size, how many steps it predicts forward
    # in a .json file
    # expected_input_size = 0
    # expected_output = 0

    data = {}
    data['timeframe'] = []
    data['timeframe'].append({
        'input_width': INPUT_WIDTH,
        'shift': SHIFT,
        'label_width': LABEL_WIDTH
    })
    data['dimention'] = []
    data['dimention'].append({
        'input_dim': in_dimentions,
        'output_dim': out_dimentions,
    })
    with open(save_ai_path + '/ai_info.json', 'w') as outfile:
        json.dump(data, outfile)
    
    return model #, expected_input_size, expected_output

def train_ai(model, train_data, validation_data, patience = 2, max_epochs = 5):
    """
        Trains an AI model

        Args::
            model: A tensorflow AI model
            train_data: training data from window object
            validation_data: validation data from window object
            patience: how many Epocs to train without val_loss decreasing before stopping
            max_epochs: how many Epocs to train maximum

        Returns::
            --

        Raises::
           --
    """

    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

    history = model.fit(train_data, epochs=max_epochs,
                      validation_data=validation_data,
                      callbacks=[early_stopping])

    #used to be history
    return

def test_run_ai(model, df_data, return_full = "no"):
    input_data = df_data["values"]

    input_data = [[value] for value in input_data] #[värde1, värde2] --> [[värde 1][värde 2]]
    input_data = tf.stack([tf.stack(value) for value in input_data]) #[[värde 1][värde 2]] --> tf.stack([värde 1][värde 2])
    input_data = tf.stack([input_data] * 1) #tf.stack([värde 1][värde 2]) --> tf.stack(tf.stack([värde 1][värde 2]))
    #shape = [batch size, time steps, inputs] = [1, 2, 1] I vårt test fall

    output = model.predict(input_data)

    #own_data = tf.stack([value for value in input_data])
    #own_data = tf.stack([own_data] * 1)
    #print("shape:", own_data.shape())
    #output = model(own_data)
    new_array = [n[0] for n in np.array(output)[0]]
    for i in range(len(new_array) - 1):
        new_array[i] = np.nan
    df_data["predictions"] = new_array

    new_anomaly_array = [n[0] for n in np.array(output)[0]]
    for i in range(len(new_array)):
        new_anomaly_array[i] = "False"
    df_data["anomaly"] = new_anomaly_array

    if return_full == "no":
        df_data_last_row = df_data.iloc[-1]
        return df_data_last_row
    else:
        return df_data

def run_ai(model, input_list, input_width = 2, shift = 1, label_width = 1, lower_sensitivity = 1.5, upper_sensitivity = 1.5, verbose = 0):
    """
        Runs the Ai

        Args::
            model: A tensorflow AI model
            input_list: A list containing datapoints. Each datapoint is a list with inputs (input list will be shortened to compensate for shift to make sure that all predicted values have a real value to compare to)
            shift: How long in the future to predict (in datapoints) (1 = the next value, 2 = the next next value from the input(s))

        Returns::
            output_array: array with predictions (shifted)
            anomaly: list containing True / False for each prediction (shifted)

        Raises::
           --
    """

    #for i in input_list:
    #    print(i)
    input_data_og = input_list
    total_size = len(input_list)

    input_data = input_list[:-1 * shift]
    #print(input_data)

    #input list should be in shape of nr_of_batches[nr_of_timesteps[values, b], b]
    #print(input_list)
    #input_data = [[value] for value in input_list[:-1 * shift]] #[värde1, värde2] --> [[värde 1][värde 2]]
    #input_data = tf.stack([tf.stack(value) for value in input_data]) #[[värde 1][värde 2]] --> tf.stack([värde 1][värde 2])
    input_data = tf.stack([input_data] * 1) #tf.stack([värde 1][värde 2]) --> tf.stack(tf.stack([värde 1][värde 2]))
    #shape = [batch size, time steps, inputs] = [1, 2, 1] I vårt test fall

    output = model.predict(input_data)
    non_output_size = input_width + shift - label_width  #4 - 1 right now = 3
    output = [n for n in np.array(output[0])]
    #one_d_output = [n[0] for n in output]
    #real_output = one_d_output[non_output_size - shift:]
    real_real_output = output[non_output_size - shift:]
    #print("non output size:", non_output_size)
    #print("rro:", real_real_output)

    output_array = []
    anomaly = []
    for j in range(len(real_real_output[0])):
        difference_dic = {"difference" : []}
        output_array.append([])

        real_values = [datapoint[j] for datapoint in input_data_og]

        for _ in range(len(real_real_output[0])):
            full_size_pred = [np.nan] * non_output_size + [n[j] for n in np.array(real_real_output)]
            output_array[j] = full_size_pred

        for i in range(len(output_array[j])):
            difference_dic["difference"].append(real_values[i] - output_array[j][i])

        difference_df = pd.DataFrame(difference_dic)

        Q1 = difference_df["difference"].quantile(0.25)
        Q3 = difference_df["difference"].quantile(0.75)

        IQR = Q3 - Q1

        lower_whisker = Q1 - lower_sensitivity * IQR    #- lower_sensitivityIQR
        upper_whisker = Q3 + upper_sensitivity * IQR  #+ upper_sensitivityIQR
        if verbose == 1:
            print("low:", lower_whisker)
            print("high:", upper_whisker)

        anomaly.append([])
        for value in difference_df["difference"]:
            if value <= lower_whisker or value >= upper_whisker:
                anomaly[j].append(ANOM_VALUE_TRUE)
                #anomaly.append(True)
            else:
                #anomaly.append(False)
                anomaly[j].append(ANOM_VALUE_FALSE)

        #print("o", output_array, "a", anomaly)
    #print("output", output_array, anomaly)
    return output_array, anomaly

def create_window(df, input_width=6, label_width=1, shift=1, label_columns=['values']):
    """
        Creates a window object for storing training, validation and test data

        Args::
            df: dataframe to format into training/validation and test data [only values allowed]
            input_width: how many datapoints (in timeunits) the model takes in in each training
            label_width: how many predictions the ai does (one at a time)
            shift: how far in the future the prediction(s) are
            label_columns: a list containing what values that should be predicted from the input dataset

        Returns::
            w2: a window object containing training, validation and test data.

        Raises::
        --
    """
    n = len(df)
    train_df = df[0:int(n*0.7)] #trainging data = first 70%
    val_df = df[int(n*0.7):int(n*0.9)] #validation = 90-70 = 20%
    test_df = df[int(n*0.9):] #test = last 10%
    if True: #is it tho?
        train_mean = train_df.mean() #meadian
        train_std = train_df.std() #standard deviation (expecting every data being normal distributed)

        #Converting every value into standard deviations from the mean of training data
        train_df = (train_df - train_mean) / train_std
        val_df = (val_df - train_mean) / train_std
        test_df = (test_df - train_mean) / train_std

    class WindowGenerator():
    #inpun width = how many indexes of data before making each prediction (in single prediction)
    #label_width = how many predictions the model will make (per label (I expect))
    #shift = how big the gap is from the input indexes to the nodes we want to predict (including the labels)
    #label_columns = the labels we want it to predict
        def __init__(self, input_width, label_width, shift,
                    train_df=train_df, val_df=val_df, test_df=test_df,
                    label_columns=None):
            # Store the raw data.
            self.train_df = train_df
            self.val_df = val_df
            self.test_df = test_df

            # Work out the label column indices.
            self.label_columns = label_columns
            if label_columns is not None:
                self.label_columns_indices = {name: i for i, name in enumerate(label_columns)}
            self.column_indices = {name: i for i, name in enumerate(train_df.columns)}

            # Work out the window parameters.
            self.input_width = input_width
            self.label_width = label_width
            self.shift = shift

            self.total_window_size = input_width + shift

            self.input_slice = slice(0, input_width) #skapar en slice:are?
            self.input_indices = np.arange(self.total_window_size)[self.input_slice] #skapar en mall för villka som är input i en indice

            self.label_start = self.total_window_size - self.label_width #at what number of indexes that prediction labels start
            self.labels_slice = slice(self.label_start, None) #a slicer to slice out the labels
            self.label_indices = np.arange(self.total_window_size)[self.labels_slice] #skapar en mall för vilka som är labels

            #def __repr__(self): #print the values
            #    return '\n'.join([
            #        f'Total window size: {self.total_window_size}',
            #        f'Input indices: {self.input_indices}',
            #        f'Label indices: {self.label_indices}',
            #        f'Label column name(s): {self.label_columns}'])

    def split_window(self, features):
        inputs = features[:, self.input_slice, :]
        labels = features[:, self.labels_slice, :]
        if self.label_columns is not None:
            labels = tf.stack([labels[:, :, self.column_indices[name]] for name in self.label_columns],axis=-1)

        # Slicing doesn't preserve static shape information, so set the shapes
        # manually. This way the `tf.data.Datasets` are easier to inspect.
        inputs.set_shape([None, self.input_width, None])
        labels.set_shape([None, self.label_width, None])

        return inputs, labels

    WindowGenerator.split_window = split_window

    def make_dataset(self, data):
        data = np.array(data, dtype=np.float32)
        ds = tf.keras.preprocessing.timeseries_dataset_from_array(
            data=data,
            targets=None,
            sequence_length=self.total_window_size,
            sequence_stride=1, #how many jumps betweeen predicted outputs
            shuffle=True, #shuffle the batches
            batch_size=32,) #batch size == how many training examples in each training cycle

        ds = ds.map(self.split_window)

        return ds

    WindowGenerator.make_dataset = make_dataset

    @property
    def train(self):
        return self.make_dataset(self.train_df)

    @property
    def val(self):
        return self.make_dataset(self.val_df)

    @property
    def test(self):
        return self.make_dataset(self.test_df)

    WindowGenerator.train = train
    WindowGenerator.val = val
    WindowGenerator.test = test

    w2 = WindowGenerator(input_width=input_width, label_width=label_width, shift=shift,
                    label_columns=label_columns)
    return w2
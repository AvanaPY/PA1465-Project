import pandas as pd
import numpy as np
import tensorflow as tf
import seaborn as sns
import math
import json
import os

def create_ai_model():
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
        tf.keras.layers.LSTM(30, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        tf.keras.layers.LSTM(70, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        tf.keras.layers.LSTM(30, return_sequences=True),#, dropout=0.2, recurrent_dropout=0.1),
        #tf.keras.layers.LSTM(10, return_sequences=True),#, dropout=0.5, recurrent_dropout=0.1),
        tf.keras.layers.Dense(units=50),
        tf.keras.layers.Dense(units=30),
        tf.keras.layers.Dense(units=10),
        tf.keras.layers.Dense(units=1)
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

    ai_name = list(load_ai_path.split("/"))[-1]
    model_info_list = [int(i) for i in list(ai_name.split(", "))]
        
    INPUT_WIDTH = model_info_list[0]
    SHIFT = model_info_list[1]
    LABEL_WIDTH = model_info_list[2]
    return model, INPUT_WIDTH, SHIFT, LABEL_WIDTH

def save_ai_model(model, save_ai_path):
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

def run_ai(model, input_list, shift = 1, label_width = 1, lower_sensitivity = 1.5, upper_sensitivity = 1.5, verbose = 0):
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
    total_size = len(input_list[0])

    input_data = input_list[:-1 * shift]
    #print(input_data)

    #input list should be in shape of nr_of_batches[nr_of_timesteps[values, b], b]
    #print(input_list)
    #input_data = [[value] for value in input_list[:-1 * shift]] #[värde1, värde2] --> [[värde 1][värde 2]]
    #input_data = tf.stack([tf.stack(value) for value in input_data]) #[[värde 1][värde 2]] --> tf.stack([värde 1][värde 2])
    input_data = tf.stack([input_data] * 1) #tf.stack([värde 1][värde 2]) --> tf.stack(tf.stack([värde 1][värde 2]))
    #shape = [batch size, time steps, inputs] = [1, 2, 1] I vårt test fall

    output = model.predict(input_data)
    non_output_size = total_size - label_width + shift
    #print("out", output)
    output = [n[0] for n in np.array(output[0])]
    real_output = output[non_output_size - shift:]
    #print(np.array(real_output), np.array(real_output))
    output_array = [np.nan] * non_output_size + [n for n in np.array(real_output)]
    #output_array = [np.nan] * shift + [n[0] for n in np.array(output)[0]]

    difference_dic = {"difference" : []}

    real_values = [datapoint[1] for datapoint in input_data_og]
    #print(real_values, output_array)
    for i in range(len(output_array)):
        difference_dic["difference"].append(real_values[i] - output_array[i])

    difference_df = pd.DataFrame(difference_dic)

    Q1 = difference_df["difference"].quantile(0.25)
    Q3 = difference_df["difference"].quantile(0.75)

    IQR = Q3 - Q1

    lower_whisker = Q1 - lower_sensitivity * IQR    #- lower_sensitivityIQR
    upper_whisker = Q3 + upper_sensitivity * IQR  #+ upper_sensitivityIQR
    if verbose == 1:
        print("low:", lower_whisker)
        print("high:", upper_whisker)

    anomaly = []
    for value in difference_df["difference"]:
        if value <= lower_whisker or value >= upper_whisker:
            anomaly.append(1)
            #anomaly.append(True)
        else:
            #anomaly.append(False)
            anomaly.append(0)

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


if __name__ == "__main__":
    #until next time: Clean out ai and keep the data outside of it and ai in separate functions
    import json
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    import seaborn as sns
    import math

    if input("Do you want to use a previously saved version?[y/n]") == "n":
        #with open("Raspberry data/hum_dataset_1.json", "r") as f:
        with open("backend/ai/Raspberry_data/temp_dataset_3.json", "r") as f:
            open_file = json.load(f)
            #open_file = pd.DataFrame(open_file)#, index=False)
            dates = open_file.keys()
            values = open_file.values()
        
        new_dict = {"dates": dates, "values": values}
        df = pd.DataFrame(new_dict)
        df.pop("dates")
        
        w2 = create_window(df)

        model = create_ai_model()

        train_ai(model, w2.train, w2.val)

        val_performance = {}
        performance = {}
        val_performance['LSTM'] = model.evaluate(w2.val)
        performance['LSTM'] = model.evaluate(w2.test, verbose=0)

        if input("do you want to save?[y/n]") == "y":
            name = input("what name should the model use?")
            input_path = 'backend/ai/saved_models/' + name

            save_ai_model(model, input_path)
    else:
        print()
        name = input("what model should we use?")
        input_path = 'backend/ai/saved_models/' + name
        model = load_ai_model(input_path)


    value = None
    values = []
    while True:
        value = int(input("vilket värde ska jag gissa på?"))
        values.append(value)
        values_dict = {"values": values}
        own_df = pd.DataFrame.from_dict(values_dict)
        df_data = run_ai(model, own_df)
        print(df_data)
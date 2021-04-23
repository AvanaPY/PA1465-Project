

def create_ai_model():

    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(1, return_sequences=True),
        tf.keras.layers.Dense(units=1)
    ])

    model.compile(loss=tf.losses.MeanSquaredError(),
                    optimizer=tf.optimizers.Adam(),
                    metrics=[tf.metrics.MeanAbsoluteError()])
    """
        Creates an AI model

        Args::
            --

        Returns::
            Tensorflow AI model

        Raises::
            --
    """
    return model

def load_ai_model(load_weights_path):
    model = tf.keras.models.load_model(load_weights_path)
    """
        Loads the AI model's weights from a file

    Args::
        model: A tensorflow AI model
        load_weights_path: str object representing the file path to load the weights from

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when loading weights
    """
    return model

def save_ai_model(model, save_weights_path):
    model.save(save_weights_path)
    """
        Saves the AI model's weights into a file

    Args::
        model: A tensorflow AI model
        save_weights_path: str object representing the file path to save the weights to

    Returns::
        Tensorflow AI model

    Raises::
        Any errors tensorflow might've raised when loading weights
    """
    return model

def train_ai(model, train_data, validation_data, patience = 2, max_epochs = 5): #need to fix data into train and validation

    early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

    history = model.fit(train_data, epochs=max_epochs,
                      validation_data=validation_data,
                      callbacks=[early_stopping])
    return history
    """
        Trains an AI model

        Args::
            model:: A tensorflow AI model
            data:: Some data you can train the AI on, I don't know

        Returns::
            --

        Raises::
           --
    """
    pass

if __name__ == "__main__":
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
        n = len(df)
        train_df = df[0:int(n*0.7)] #trainging data = first 70%
        val_df = df[int(n*0.7):int(n*0.9)] #validation = 90-70 = 20%
        test_df = df[int(n*0.9):] #test = last 10%
        if False:
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

        w2 = WindowGenerator(input_width=6, label_width=6, shift=6,
                        label_columns=['values'])

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

        val_performance = {}
        performance = {}

        model = create_ai_model()

        train_ai(model, w2.train, w2.val)

        val_performance['LSTM'] = model.evaluate(w2.val)
        performance['LSTM'] = model.evaluate(w2.test, verbose=0)

        if input("do you want to save?[y/n]") == "y":
            save_ai_model(model, 'backend/ai/saved_model/my_model')
    else:
        model = load_ai_model('backend/ai/saved_model/my_model')

    #own_data = [1]
    #own_data = tf.stack([own_data] * 6)
    #own_data = tf.stack([own_data] * 1)

    #print("training on own data")
    #print(model(own_data))


    value = None
    values = []
    while True:
        value = int(input("vilket värde ska jag gissa på?"))
        values.append(value)
        own_data = tf.stack([value for value in values])
        own_data = tf.stack([own_data] * 1)
        output = model(own_data)
        print(values, "-->", output)



        
    """
    Epoch 1/5
    3071/3071 [==============================] - 30s 10ms/step - loss: 0.1866 - mean_absolute_error: 0.2566 - val_loss: 0.3495 - val_mean_absolute_error: 0.3635
    Epoch 2/5
    3071/3071 [==============================] - 30s 10ms/step - loss: 0.0081 - mean_absolute_error: 0.0497 - val_loss: 0.1244 - val_mean_absolute_error: 0.1944
    Epoch 3/5
    3071/3071 [==============================] - 30s 10ms/step - loss: 0.0030 - mean_absolute_error: 0.0296 - val_loss: 0.0500 - val_mean_absolute_error: 0.1114
    Epoch 4/5
    3071/3071 [==============================] - 29s 10ms/step - loss: 0.0015 - mean_absolute_error: 0.0216 - val_loss: 0.0255 - val_mean_absolute_error: 0.0739
    Epoch 5/5
    3071/3071 [==============================] - 29s 10ms/step - loss: 0.0011 - mean_absolute_error: 0.0182 - val_loss: 0.0169 - val_mean_absolute_error: 0.0603
    878/878 [==============================] - 4s 5ms/step - loss: 0.0169 - mean_absolute_error: 0.0603
    """
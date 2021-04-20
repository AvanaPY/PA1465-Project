#https://www.tensorflow.org/tutorials/structured_data/time_series

print("starting tensorflow")

import os
import datetime

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf

print("tensorflow ready")

#mpl.rcParams['figure.figsize'] = (8, 6)
#mpl.rcParams['axes.grid'] = False

print("starting downloading")
zip_path = tf.keras.utils.get_file(
    origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip',
    fname='jena_climate_2009_2016.csv.zip',
    extract=True)
csv_path, _ = os.path.splitext(zip_path)



df = pd.read_csv(csv_path)
print("done downloading")
# slice [start:stop:step], starting from index 5 take every 6th record.
df = df[5::6]

date_time = pd.to_datetime(df.pop('Date Time'), format='%d.%m.%Y %H:%M:%S')

column_indices = {name: i for i, name in enumerate(df.columns)}

print("column_indices:", column_indices)

n = len(df)
train_df = df[0:int(n*0.7)] #trainging data = first 70%
val_df = df[int(n*0.7):int(n*0.9)] #validation = 90-70 = 20%
test_df = df[int(n*0.9):] #test = last 10%


num_features = df.shape[1]

print("num features:", num_features)


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
      self.label_columns_indices = {name: i for i, name in
                                    enumerate(label_columns)}
    self.column_indices = {name: i for i, name in
                           enumerate(train_df.columns)}

    print("label_columns_indices", self.label_columns_indices, " - column_indices", self.column_indices)

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

  def __repr__(self): #print the values
    return '\n'.join([
        f'Total window size: {self.total_window_size}',
        f'Input indices: {self.input_indices}',
        f'Label indices: {self.label_indices}',
        f'Label column name(s): {self.label_columns}'])


def split_window(self, features):
  inputs = features[:, self.input_slice, :]
  labels = features[:, self.labels_slice, :]
  if self.label_columns is not None:
    labels = tf.stack(
        [labels[:, :, self.column_indices[name]] for name in self.label_columns],
        axis=-1)

  # Slicing doesn't preserve static shape information, so set the shapes
  # manually. This way the `tf.data.Datasets` are easier to inspect.
  inputs.set_shape([None, self.input_width, None])
  labels.set_shape([None, self.label_width, None])

  return inputs, labels

WindowGenerator.split_window = split_window


w2 = WindowGenerator(input_width=6, label_width=1, shift=1,
                     label_columns=['T (degC)'])

# Stack three slices, the length of the total window:
example_window = tf.stack([np.array(train_df[:w2.total_window_size]),
                           np.array(train_df[100:100+w2.total_window_size]),
                           np.array(train_df[200:200+w2.total_window_size])])


example_inputs, example_labels = w2.split_window(example_window)

print('All shapes are: (batch, time, features)')
print(f'Window shape: {example_window.shape}')
print(f'Inputs shape: {example_inputs.shape}')
print(f'labels shape: {example_labels.shape}')


"""
def plot(self, model=None, plot_col='T (degC)', max_subplots=3):
  inputs, labels = self.example 
  plt.figure(figsize=(12, 8))
  plot_col_index = self.column_indices[plot_col]
  max_n = min(max_subplots, len(inputs))
  for n in range(max_n):
    plt.subplot(3, 1, n+1)
    plt.ylabel(f'{plot_col} [normed]')
    plt.plot(self.input_indices, inputs[n, :, plot_col_index],
             label='Inputs', marker='.', zorder=-10)

    if self.label_columns:
      label_col_index = self.label_columns_indices.get(plot_col, None)
    else:
      label_col_index = plot_col_index

    if label_col_index is None:
      continue

    plt.scatter(self.label_indices, labels[n, :, label_col_index],
                edgecolors='k', label='Labels', c='#2ca02c', s=64)
    if model is not None:
      predictions = model(inputs)
      plt.scatter(self.label_indices, predictions[n, :, label_col_index],
                  marker='X', edgecolors='k', label='Predictions',
                  c='#ff7f0e', s=64)

    if n == 0:
      plt.legend()

  plt.xlabel('Time [h]')

WindowGenerator.plot = plot
"""


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

"""
@property
def example(self):
  """"""Get and cache an example batch of `inputs, labels` for plotting.""""""
  result = getattr(self, '_example', None)
  if result is None:
    # No example batch was found, so get one from the `.train` dataset
    result = next(iter(self.train))
    # And cache it for next time
    self._example = result
  return result
"""

WindowGenerator.train = train
WindowGenerator.val = val
WindowGenerator.test = test
#WindowGenerator.example = example





val_performance = {}
performance = {}


wide_window = WindowGenerator(
    input_width=24, label_width=24, shift=1,
    label_columns=['T (degC)'])


#our own stuff
#tf.keras.callbacks.CSVLogger(
#    "outputdata_questionmark.csv", separator=',', append=False
#)
csv_logger = tf.keras.callbacks.CSVLogger("outputdata_questionmark.csv", separator=',', append=False)
#dos only save statistical
#end of out own stuff


MAX_EPOCHS = 1 #used to be 20

def compile_and_fit(model, window, patience=2): #patience = 2
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss',
                                                    patience=patience,
                                                    mode='min')

  model.compile(loss=tf.losses.MeanSquaredError(),
                optimizer=tf.optimizers.Adam(),
                metrics=[tf.metrics.MeanAbsoluteError()])

  history = model.fit(window.train, epochs=MAX_EPOCHS,
                      validation_data=window.val,
                      callbacks=[early_stopping])
  return history



lstm_model = tf.keras.models.Sequential([
    # Shape [batch, time, features] => [batch, time, lstm_units]
    tf.keras.layers.LSTM(1, return_sequences=True),
    #tf.keras.layers.LSTM(32 * 2, return_sequences=True),
    #tf.keras.layers.LSTM(32 * 5, return_sequences=True),
    # Shape => [batch, time, features]
    tf.keras.layers.Dense(units=1)
])



history = compile_and_fit(lstm_model, wide_window)

#IPython.display.clear_output()
val_performance['LSTM'] = lstm_model.evaluate(wide_window.val)
performance['LSTM'] = lstm_model.evaluate(wide_window.test, verbose=0)

print("sltm model", lstm_model, type(lstm_model))
#print("", wide_window.example)

#wide_window.plot(lstm_model)

#plt.show()

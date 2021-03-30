import os
import datetime
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from datetime import timedelta
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.utils import Sequence

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def create_data():
  zip_path = tf.keras.utils.get_file(
    origin='https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip',
    fname='jena_climate_2009_2016.csv.zip',
    extract=True)
  csv_path, _ = os.path.splitext(zip_path)
  df = pd.read_csv(csv_path)

  df = df[5::1] # every 10 min instead of 60

  df = df.loc[0:100000, ['Date Time', 'T (degC)']]

  df['Date Time'] = pd.to_datetime(df['Date Time'])
  df.sort_values('Date Time', inplace=True, ascending=True)
  df = df.reset_index(drop=True)

  return df
  
def training_data(df):  
  test_cutoff_date = df['Date Time'].max() - timedelta(days=7)
  val_cutoff_date = test_cutoff_date - timedelta(days=14)
  df_test = df[df['Date Time'] > test_cutoff_date]
  df_val = df[(df['Date Time'] > val_cutoff_date) & (df['Date Time'] <= test_cutoff_date)]
  df_train = df[df['Date Time'] <= val_cutoff_date]

  #print('Test dates: {} to {}'.format(df_test['Date Time'].min(), df_test['Date Time'].max()))
  #print('Validation dates: {} to {}'.format(df_val['Date Time'].min(), df_val['Date Time'].max()))
  #print('Train dates: {} to {}'.format(df_train['Date Time'].min(), df_train['Date Time'].max()))

  return df_test, df_val, df_train

def create_training_files(df, start_index, end_index, history_length, step_size, taget_step, num_rows_per_file,data_folder):
  assert start_index >= 0, "ERROR: start size needs to be over or equal to 0"
  assert step_size > 0, "ERROR: step size needs to be over 0"

  if not os.path.exists(data_folder):
    os.makedirs(data_folder)

  time_lags = sorted(range(target_step+1, target_step+history_length+1, step_size), reverse=True)
  #col_names = []
  #for i in time_lags:
  #  col_names.append("x_lag" + str(i))
  #col_names.append('y')
  col_names = [f'x_lag{i}' for i in time_lags] + ['y']
  start_index = start_index + history_length
  if end_index is None:
    end_index = len(dataset) - target_step

  rng = range(start_index, end_index)
  num_rows = len(rng)
  num_files = math.ceil(num_rows/num_rows_per_file)

  print(f'Creating {num_files} files.')
  for i in range(num_files):
    filename = f'{data_folder}/ts_file{i}.pkl'
    
    if i % 10 == 0:
      print(f'{filename}')
        
    # get the start and end indices.
    ind0 = i*num_rows_per_file
    ind1 = min(ind0 + num_rows_per_file, end_index)
    data_list = []
    
    # j in the current timestep. Will need j-n to j-1 for the history. And j + target_step for the target.
    for j in range(ind0, ind1):
      indices = range(j-1, j-history_length-1, -step_size)
      data = dataset[sorted(indices) + [j+target_step]]
      
      # append data to the list.
      data_list.append(data)

    df_ts = pd.DataFrame(data=data_list, columns=col_names)
    df_ts.to_pickle(filename)
            
  return len(col_names)-1

class TimeSeriesLoader:
    def __init__(self, ts_folder, filename_format):
        self.ts_folder = ts_folder
        
        # find the number of files.
        i = 0
        file_found = True
        while file_found:
            filename = self.ts_folder + '/' + filename_format.format(i)
            file_found = os.path.exists(filename)
            if file_found:
                i += 1
                
        self.num_files = i
        self.files_indices = np.arange(self.num_files)
        self.shuffle_chunks()
        
    def num_chunks(self):
        return self.num_files
    
    def get_chunk(self, idx):
        assert (idx >= 0) and (idx < self.num_files)
        
        ind = self.files_indices[idx]
        filename = self.ts_folder + '/' + filename_format.format(ind)
        df_ts = pd.read_pickle(filename)
        num_records = len(df_ts.index)
        
        features = df_ts.drop('y', axis=1).values
        target = df_ts['y'].values
        
        # reshape for input into LSTM. Batch major format.
        features_batchmajor = np.array(features).reshape(num_records, -1, 1)
        return features_batchmajor, target
    
    # this shuffles the order the chunks will be outputted from get_chunk.
    def shuffle_chunks(self):
        np.random.shuffle(self.files_indices)

if False: #Creating the Data Folder
  df = create_data()

  df_test, df_val, df_train = training_data(df) #slices data into different validation and training sets

  global_active_power = df_train['T (degC)'].values 
  # Scaled to work with Neural networks.
  scaler = MinMaxScaler(feature_range=(0, 1))
  global_active_power_scaled = scaler.fit_transform(global_active_power.reshape(-1, 1)).reshape(-1, )

  start_index = 0
  end_index = None
  history_length = 7*24*6
  step_size = 1
  target_step = 12
  num_rows_per_file = 144
  data_folder = "DataFolder"

  num_timesteps = create_training_files(dataset = global_active_power_scaled,
    start_index = 0,
    end_index = None,
    history_length = 7*24*6,
    step_size = 1,
    target_step = 12,
    num_rows_per_file = 144,
    data_folder = "DataFolder" )
  print(num_timesteps)

#Feed data into model   
ts_folder = 'DataFolder'
filename_format = 'ts_file{}.pkl'
tss = TimeSeriesLoader(ts_folder, filename_format)

#Keras model

#creating model
num_timesteps = 1000 #change after dev (Number of data points in each file)
ts_inputs = tf.keras.Input(shape=(num_timesteps, 1))
x = layers.LSTM(units=10)(ts_inputs)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(1, activation='linear')(x)
model = tf.keras.Model(inputs=ts_inputs, outputs=outputs)

#adding optimizer and loss function to the model
model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.01),
              loss=tf.keras.losses.MeanSquaredError(),
              metrics=['mse'])

model.summary() #shows the input and output values

# train in batch sizes of 128.
BATCH_SIZE = 128
NUM_EPOCHS = 1
NUM_CHUNKS = tss.num_chunks()

for epoch in range(NUM_EPOCHS):
  print('epoch #{}'.format(epoch))
  for i in range(NUM_CHUNKS):
    X, y = tss.get_chunk(i)
    
    # model.fit does train the model incrementally. ie. Can call multiple times in batches.
    # https://github.com/keras-team/keras/issues/4446
    model.fit(x=X, y=y, batch_size=BATCH_SIZE)
      
  # shuffle the chunks so they're not in the same order next time around.
  tss.shuffle_chunks()


global_active_power_val = df_val['Global_active_power'].values
global_active_power_val_scaled = scaler.transform(global_active_power_val.reshape(-1, 1)).reshape(-1, )

history_length = 7*24*60  # The history length in minutes.
step_size = 10  # The sampling rate of the history. Eg. If step_size = 1, then values from every minute will be in the history.
                #                                       If step size = 10 then values every 10 minutes will be in the history.
target_step = 10  # The time step in the future to predict. Eg. If target_step = 0, then predict the next timestep after the end of the history period.
                  #                                             If target_step = 10 then predict 10 timesteps the next timestep (11 minutes after the end of history).

# The csv creation returns the number of rows and number of features. We need these values below.
num_timesteps = create_ts_files(dataset = global_active_power_val_scaled,
                                start_index=0,
                                end_index=None,
                                history_length=history_length,
                                step_size=step_size,
                                target_step=target_step,
                                num_rows_per_file= 144, #128*100, Något skumt med detta (vi får 2 medans de får samma som de skriver här)
                                data_folder='DataValidationFolder')


# If we assume that the validation dataset can fit into memory we can do this.
df_val_ts = pd.read_pickle('DataValidationFolder/ts_file0.pkl')


features = df_val_ts.drop('y', axis=1).values
features_arr = np.array(features)

# reshape for input into LSTM. Batch major format.
num_records = len(df_val_ts.index)
features_batchmajor = features_arr.reshape(num_records, -1, 1)


y_pred = model.predict(features_batchmajor).reshape(-1, )
y_pred = scaler.inverse_transform(y_pred.reshape(-1, 1)).reshape(-1 ,)

y_act = df_val_ts['y'].values
y_act = scaler.inverse_transform(y_act.reshape(-1, 1)).reshape(-1 ,)

print('validation mean squared error: {}'.format(mean_squared_error(y_act, y_pred)))

#baseline
y_pred_baseline = df_val_ts['x_lag11'].values
y_pred_baseline = scaler.inverse_transform(y_pred_baseline.reshape(-1, 1)).reshape(-1 ,)
print('validation baseline mean squared error: {}'.format(mean_squared_error(y_act, y_pred_baseline)))




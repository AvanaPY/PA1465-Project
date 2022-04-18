from logging import exception
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Remove tensorflow debugging
import tensorflow as tf

import json
import csv
import pandas as pd
import mysql.connector.errors as merrors
import datetime
import numpy as np
import math

from ai import *

from database import *

from .ext import sql_type_to_python_type, all_type_equal_or_none, _all_types_not_equal, get_data_column_types
import backend.errors as backend_errors

DATETIME_COLUMN_NAME = 'date'
CLASSIFICATION_COLUMN_NAME = 'classification'
PREDICTION_COLUMN_NAME = 'PREDICTION'
ID_COLUMN_NAME = 'id'

WANTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class BackendBase:
    def __init__(self, confparser, database_section='mysql', ai_model='temp_ai_saved', load_ai=False):
        self._my_db, self._db_config = create_sql_connection(confparser=confparser, section=database_section)
        if self._my_db:
            self._curs = self._my_db.cursor(buffered=True)
            print(f'SUCCESSFULLY CONNECTED TO DATABASE')
        else:
            self._curs = None
            print(f'FAILED TO LOAD DATABASE: NO DATABASE AVAILABLE')

        self._load_ai = load_ai
        if load_ai:
            self.load_ai(ai_model)
        else:
            self._ai_model_name = ''
            print(f'INFO: AI MODEL NOT LOADED')

    def load_ai(self, ai_name):
        """
            Function for getting the information about a table

            Args:
                ai_name: str
            
            Returns:
                -

            Raises:
                -
        """
        self._load_ai = True
        self._ai_model_name = ai_name
        self._ai_model, self._ai_input_size, self._ai_shift_size, self._ai_output_size, self._input_dim, self._output_dim = load_ai_model(f'./ai/saved_models/{ai_name}')

    def _get_database_description_no_id_column(self, table_name):
        """
            Function for getting the information about a table

            Args:
                table_name: str
            
            Returns:
                database_col_names: list of str - each string is a column name
                database_col_types: list of str - each string is a column type

            Raises:
                Propagates any errors
        """
        my_sql_command = f'DESCRIBE {table_name}'
        self._curs.execute(my_sql_command)
        desc = self._curs.fetchall()

        database_col_names = list((a[0] for a in desc))
        database_col_names.remove(ID_COLUMN_NAME)

        database_col_types = list((sql_type_to_python_type(a[1].decode('utf-8')) for a in desc if a[0] in database_col_names))
        return database_col_names, database_col_types

    def get_database_column_names(self, table_name):
        """
            A function for getting all the column names in the table

            Args:
                table_name          : str
            
            Returns:
                database_col_names  : list of str - each string is a column name

            Raises:
                -
        """
        my_sql_command = f'DESCRIBE {table_name}'
        self._curs.execute(my_sql_command)
        desc = self._curs.fetchall()

        database_col_names = list((a[0] for a in desc))
        return database_col_names

    def get_prediction_column_names(self, table_name):
        """
            A function for getting all the names of the prediction columns in the table

            Args:
                table_name          : str
            
            Returns:
                database_col_names  : list of str - each string is a column name

            Raises:
                -
        """
        cols = self.get_database_column_names(table_name)
        pred_cols = [col for col in cols if PREDICTION_COLUMN_NAME in col]
        return pred_cols
        
    def get_sensor_column_names(self, table_name):
        """
            Function for getting the names of the sensor columns in the table

            Args:
                table_name  : str
            
            Returns:
                sens_cols   : list<str>

            Raises:
                -
        """
        cols = self.get_database_column_names(table_name)
        sens_cols = [col for col in cols if not PREDICTION_COLUMN_NAME in col and col not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME)]
        return sens_cols

    def get_sensor_prediction_column_name_pairs(self, table_name):
        """
            Function for getting the pairs of sensor-sensorprediction pairs

            Args:
                table_name  : str
            
            Returns:
                pairs       : list<tuple>

            Raises:
                -
        """
        preds = self.get_prediction_column_names(table_name)
        pairs = [(pred.replace(PREDICTION_COLUMN_NAME, ''), pred) for pred in preds]
        return pairs
        
    def _compatability_check(self, data, table_name):
        ''' 
            Checks the compatibility of a json document against the database table.

            A (probably) very over-engineered method that checks whether or not a json document is compatible with the database. 
            It achieves this by comparing the column names, types, and sizes to the database's own columns.

            This method assumes that the table exists in the database already, otherwise nothing happens.

            Args:
                data        : dict - json document
                table_name  : str - the table name

            Returns:
                boolean     : Wether or not it's compatible

            Raises:
                Backend.Error
        '''
        # Ask the database for the table's data types
        database_col_names, database_col_types = self._get_database_description_no_id_column(table_name)


        # Fast check to make sure the column counts are the same
        data_col_names = data.keys()
        
        if len(database_col_names) != len(data_col_names):
            raise backend_errors.ColumnCountNotCorrectException('Invalid column count, make sure that every column in the database also exists in the JSON file.')

        # Checking that all the column names in the data exists in the database too
        for name in data_col_names:
            if name not in database_col_names:
                raise backend_errors.InvalidColumnNameException(name)

        # Checking that all the items in the columns have the exact same type
        data_column_lengths = [ len(data[key]) for key in data ]
        all_same = all([a == data_column_lengths[0] for a in data_column_lengths])
        if not all_same:
            raise backend_errors.ColumnLengthsDifferException()

        # Checking that the columns in the data have the same type as in the database.
        data_types = {
            key: all_type_equal_or_none([type(a) for a in data[key]]) for key in data
        }
        for i, key in enumerate(database_col_names):
            t = data_types[key]
            # Column type checking
            if t is _all_types_not_equal:
                raise backend_errors.ColumnTypesNotSameException(key, data[key])

            # Database cross-checking by type
            wanted_type = database_col_types[i]
            if isinstance(wanted_type, tuple):
                if not t in wanted_type:
                    backend_errors.ColumnTypesNotMatchingException(key, database_col_types[i], t)
            else:
                if t != wanted_type:
                    raise backend_errors.ColumnTypesNotMatchingException(key, database_col_types[i], t)
                
        # If no errors occured and nothing seems wrong, let's just return True.
        return True

    def _create_table_based_on_data_dict(self, table_name, data, **kwargs):
        """
            Creates a table using a dictionary of a column-name:column-sql-types mapping.

            Args:
                table_name  : str
                data        : a dictionary of a column-name:column-sql-types mapping
            
            Returns:
                -

            Raises:
                -
        """
        table_types = self._create_table_dict(data, **kwargs)
        create_table(self._curs, table_name, table_types)

    def delete_table(self, table_name):
        """
            Deletes a table from the database.

            Args:
                table_name: str
            
            Returns:
                -

            Raises:
                Propagates any errors
        """
        if table_name:
            drop_table(self._curs, table_name)
        else:
            raise Exception('Table name is Null or has an equivalent value')

    def import_data_json(self, path_to_file, database_table, max_values=None, **kwargs):
        """
            Imports data from a json file and converts it into dict.

            Args:
                path_to_file    : str
                database_table  : str
                max_values      : int
            
            Returns:
                dct             : a dictionary containing the data in the json file 

            Raises:
                Propagates any errors
        """
        with open(path_to_file, "r") as f:
            dct = json.load(f)

        if max_values and max_values > 0:
            dct = {
                key:dct[key][:max_values] for key in dct
            }

        self.add_dict_to_database(dct, database_table, **kwargs)
                   
    def import_data_csv(self, path_to_file, database_table, **kwargs):
        """
            Imports data from a csv file and converts it into dict.

            Args:
                path_to_file    : str
                database_table  : str
            
            Returns:
                dct         : a dictionary containing the data in the csv file. 

            Raises:
                Propagates any errors.
        """
        dct = pd.read_csv(path_to_file).to_dict()
        dct = { key: [val for val in dct[key].values() ] for key in dct }
        self.add_dict_to_database(dct, database_table, **kwargs)
    
    def export_data_json(self, path_to_file, database_table, **kwargs):
        """
            Exports data as a json file.

            Args:
                path_to_file    : str
                database_table  : str
            
            Returns:
                -

            Raises:
                Propagates any errors.
        """
        columns = self.get_database_column_names(database_table)
        json_data = {
            key: [] for key in columns
        }
        data = self.get_all_data(database_table)
        for i in range(len(data)):
            for key, value in zip(columns, data[i]):
                if isinstance(value, datetime.datetime):
                    value = value.strftime(WANTED_DATETIME_FORMAT)
                json_data[key].append(value)
        with open(path_to_file, 'w') as f:
            json.dump(json_data, f)

    def export_data_csv(self, path_to_file, database_table, **kwargs):
        """
            Exports data as a csv file.

            Args:
                path_to_file    : str
                database_table  : str
            
            Returns:
                -

            Raises:
                Propagates any errors.
        """

        data = self.get_all_data(database_table)
        cols = self.get_database_column_names(database_table)
        with open(path_to_file, 'w+', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=cols)
            writer.writeheader()
            for row in data:
                writer.writerow({
                    key:value for key, value in zip(cols, row)
                })

    def add_dict_to_database(self, data_dict, database_table, date_col=None, **kwargs):
        """ 
            Adds a dictionary to the database.

            Args:
                data_dict       : dict - a dictionary containing the data from the import functions.
                database_table  : str - the table name in the database.
                date_col        : str - The column that should be considered as the datetime column.

            Returns:
                -

            Raises:
                Propagates any errors.
        """
        if not self._my_db:
            raise backend_errors.NoDatabaseConnectedException()
        self._check_has_classifications(database_table, data_dict, **kwargs)
        self._check_has_datetime_column(database_table, data_dict, **kwargs)

        keys = list(data_dict.keys())
        for key in keys:
            if key.lower() == "id":
                del data_dict[key]

        data_dict = self._sort_data_dictionary(data_dict)
        self._compatability_check(data_dict, database_table)

        inv_dct = self._invert_dictionary(data_dict)
        for row in inv_dct:
            insert_data(self._curs, database_table, row)

    def _sort_data_dictionary(self, data_dict : dict):
        """
            Sorts a dictionary into the desired structure.

            Sorted into order of:

            ID, Date, Classification, Sensor1, Sensor2... predictionSensor1, predictionSensor2...

            Args:
                data_dict   : dict

            Returns:
                sorted_data : dict

            Raises:
                -
        """
        sorted_data = {}
        for key in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME):
            if key in data_dict:
                sorted_data[key] = data_dict[key]

        sensor_keys = [key for key in data_dict if (key not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME) and PREDICTION_COLUMN_NAME not in key)]

        for key in sensor_keys:
            sorted_data[key] = data_dict[key]

        prediction_keys = [key for key in data_dict if PREDICTION_COLUMN_NAME in key]

        for key in prediction_keys:
            sorted_data[key] = data_dict[key]

        return sorted_data

    def _create_table_dict(self, data_dict, **kwargs):
        """
            Creates a table type dict based on a data dictionary.

            Args:
                data_dict           : A dictionary of data values.

            Returns:
                dct                 : Dictionary of column-name:column-sql-types.

            Raises:
                -
        """

        type_dict = {
            str: "VARCHAR(255)",
            int: "INT",
            float: "FLOAT",
            bool: int
        }
        
        dct = {
            "id": 'INT PRIMARY KEY AUTO_INCREMENT'
        }

        col_names = data_dict.keys()
        data_column_types = get_data_column_types(data_dict)
        for col in col_names:
            data_type = data_column_types[col]
            if col == DATETIME_COLUMN_NAME:
                dct[col] = 'DATETIME'
            else:
                dct[col] = type_dict[data_type]
        
        # Classification column
        dct[CLASSIFICATION_COLUMN_NAME] = 'bit'
        
        prediction_column_names = [key for key in dct if PREDICTION_COLUMN_NAME in key]

        for pkey in prediction_column_names:
            dct[pkey] = 'FLOAT(6)'

        return dct

    def _invert_dictionary(self, dct):
        """
            Inverts a dictionary

            Args:
                dct: A dictionary with lists of structure {
                    key1: [ value1, value2 ],
                    key2: [ value3, value4 ]
                }
            
            Returns:
                A list of dictionaries of structure [
                    {
                        key1: value1,
                        key2: value3
                    },
                    {
                        key1: value2,
                        key2: value4
                    }
                ]

            Raises:
                -
        """
        keys = dct.keys()
        items_in_column = len(dct[list(keys)[0]])
        o = [ { key:None for key in keys } for _ in range(items_in_column) ] # Base dictionary
        for i in range(items_in_column):
            for key in keys:
                o[i][key] = dct[key][i]
        return o

    def get_tables(self):
        """ 
            A wrapping function for returning all the tables in the databasse.

            Args:
                -
            
            Returns:
                tables: a list of all tables in the database.

            Raises:
                No tables available error.
        """
        tables = get_tables(self._curs)
        return tables

    def get_all_data(self, table_name, convert_datetime=False):
        """ 
            A wrapping function for returning all the data in the table.

            Args:
                table_name      : str
                convert_datetime: bool
            
            Returns:
                data            : a list of touples containing the data of the database, where each touple is a row.

            Raises:
                -
        """
        data = get_data(self._curs, table_name)
        if convert_datetime:
            self._convert_row_datetime(table_name, data)
        return data 

    def _convert_row_datetime(self, table_name, data):
        """ Converts the "date" column in the data from datetime.datetime objects to string values.

            Args:
                table_name  : str
                data        : list[tuple]

            Returns:
                -

            Raises:
                -
        """
        columns = self.get_database_column_names(table_name)
        date_column_index = columns.index(DATETIME_COLUMN_NAME)
        for i in range(len(data)):
            row = list(data[i])
            if isinstance(row[date_column_index], datetime.datetime):
                row[date_column_index] = row[date_column_index].strftime(WANTED_DATETIME_FORMAT)
                data[i] = tuple(row)

    def _check_has_classifications(self, table_name : str, data : dict, classify_if_not_exist=True, **kwargs):
        """ 
            Checks whether or not data has classification data.

            Checks if the data has a classification column, if it doesn't it adds the column and also classifies every "row" in the data. 
            It also checks if it has a "prediction" column, if it doesn't it also adds this column to the data with new prediction values.

            Args:
                table_name: str
                data: dict - Data dictionary of format
                {
                    "key1": [ value1, value2 ],
                    "key2": [ value3, value4 ]
                }
                classify_if_not_exist: bool
            Returns:
                -
            Raises:
                -

        """
        col_names = list(data.keys())       # All columns in data

        data_point_count = len(data[col_names[0]])

        non_reserved_column_names = [key for key in col_names if key not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME)] # All user-defined columns
        sensor_keys = [key for key in non_reserved_column_names if PREDICTION_COLUMN_NAME not in key]                                           # All columns that refer to sensors
        sensor_values = [data[key] for key in data.keys() if key in sensor_keys]
        

        prediction_column_names = [PREDICTION_COLUMN_NAME + key for key in sensor_keys]
        if classify_if_not_exist and self._load_ai:
            rows = []
            for i in range(len(sensor_values[0])):
                row = [values[i] for values in sensor_values]
                rows.append(row)

            predictions, classifications = self.classify_datapoints(table_name, rows, use_historical=kwargs.get('use_historical', False))

            if not CLASSIFICATION_COLUMN_NAME in col_names:
                data[CLASSIFICATION_COLUMN_NAME] = classifications

            for i, pkey in enumerate(prediction_column_names):
                data[pkey] = predictions[i]
        else:
            if not CLASSIFICATION_COLUMN_NAME in col_names:
                data[CLASSIFICATION_COLUMN_NAME] = [None] * data_point_count
            for pkey in prediction_column_names:
                data[pkey] = [0] * data_point_count

    def _check_has_datetime_column(self, table_name : str, data : dict, **kwargs):
        """
            Checks if thetable has a datetime column, else adds it.

            Args:
                table_name  : str
                data        : dict
            
            Returns:
                -

            Raises:
                -
        """
        if DATETIME_COLUMN_NAME not in data:
            data_points = len(list(data.values())[0])

            t = datetime.datetime.now()
            
            data[DATETIME_COLUMN_NAME] = []
            for _ in range(data_points):
                t += datetime.timedelta(0, 1)
                data[DATETIME_COLUMN_NAME].append(t.strftime(WANTED_DATETIME_FORMAT))
        
        else:
            date_format = "%Y-%m-%d"
            for i, v in enumerate(data[DATETIME_COLUMN_NAME]):
                dt_obj = datetime.datetime.strptime(v, WANTED_DATETIME_FORMAT)

    def edit_column_value(self, table_name : str, id : int, column_name : str, new_column_value):
        """ 
            Edits the value in a database.

            Args:
                table_name          : str - table name.
                id                  : int - the id of the row of the datapoint being edited.
                column_name         : str - Name of the column.
                new_column_value    : any - Value to insert into the table.
            Returns:
                -
            Raises:
                Any propagated errors.
        """
        edit_data(self._curs, table_name,
            { column_name : new_column_value },
            { ID_COLUMN_NAME: id }
        )

    def edit_classification(self, table_name : str, id : int , classification : bool):
        """ 
            Edits a classification in the table.

            Args:
                table_name      : str - table name.
                id              : int - the id of the row of the datapoint being edited.
                classification  : int - the classification of the datapoint, either 1 (True) or 0 (False).
            Returns:
                -
            Raises:
                Any propagated errors.
        """
        self.edit_column_value(table_name, id, CLASSIFICATION_COLUMN_NAME, classification)
        
    def _delete_data_point(self, table_name : str, id : int):
        """
            Delets a datapoint.

            Args:
                table_name  : str - table name.
                id          : int - the id of the datapint being deleted.
            Returns:
                -
            Raises:
                Any propagated errors.
        """
        delete_data(self._curs, table_name, { "id" : id })

    def _get_all_non_classified(self, table_name, NON_CLASSIFIED_VALUE=None, convert_datetime=False, **kwargs):
        """ 
            Returns all non-classified data points.
            
            Args:
                _table_name         : str - Default None.
                NON_CLASSIFIED_VALUE: any - the datatype Non-classified datapoints will become. Default None
                convert_datetime    : bool
            Returns:
                data: a list of touples where each touple is a row in the databasae.
            Raises:
                Any propagated errors.
        """

        data = get_data(self._curs, table_name, column_dictionary={
            CLASSIFICATION_COLUMN_NAME: NON_CLASSIFIED_VALUE,
        })
        if convert_datetime:
            self._convert_row_datetime(table_name, data)
        return data

    def _get_all_anomalies(self, table_name):
        """ 
            Returns all data points where the calssification column is 1.
            
            Args:
                table_name: str
            Returns:
                data: a list of touples where each touple is a row in the database.
            Raises:
                -
        """
        my_sql_command = f'SELECT * FROM {table_name} WHERE classification = 1;'
        self._curs.execute(my_sql_command)
        data = self._curs.fetchall()
        return data

    def strip_columns_from_data_rows(self, table_name : str, data : list, cols_to_strip : list):
        """
            OBS: SUPPOSE THAT `data` IS COLUMN-WISE ORDERED ACCORDING TO THE DATABASE!

            Function for getting the information about a table

            Args:
                table_name      : str
                data            : list
                cols_to_strip   : list<str>
            
            Returns:
                -

            Raises:
                -
        """
        data_cols = self.get_database_column_names(table_name)

        for i, row in enumerate(data):
            row = list(row)
            for d, col in zip(row[:], data_cols):
                if col in cols_to_strip:
                    row.remove(d)
            data[i] = row

    def classify_datapoints(self, table_name : str, datapoints : list, use_historical : bool=True):
        """ 
            Predicts the and checks for anomalies in the dataset. 
            
            Args:
                table_name              : str
                datapoints              : list - a list of datapoints to be predicted and checked for anomalies.
                use_historical[optional]: bool - wether to use historical data or only the data in datapoints (True: yes, False: no).
            Returns:
                preds                   : list - a list of predictions
                final_cls               : list - a list of anomaly check results.
            Raises:
                -
        """
        if use_historical:
            n = self._ai_input_size # Amount of datapoints the AI will use
            n_last_datapoints = get_data(self._curs, table_name, order_by=[DATETIME_COLUMN_NAME], order_by_asc_desc='DESC', limit_row_count=n)

            n_last_datapoints = list(reversed(n_last_datapoints))

            prediction_columns = self.get_prediction_column_names(table_name)

            self.strip_columns_from_data_rows(table_name, n_last_datapoints, 
                                            [ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME, *prediction_columns])
            input_list = [*n_last_datapoints, *datapoints]
        else:
            input_list = datapoints
            if len(input_list) < self._ai_input_size + self._ai_shift_size:
                raise backend_errors.InputListSizeNotMachingException(len(input_list), self._ai_input_size + self._ai_shift_size) 

        ilst_np = np.array(input_list)
        # std, mean = ilst_np.std(), ilst_np.mean()

        # ilst_np = (ilst_np - mean) / std

        # print(datapoints[:10])
        # print(f'Classifying data such as {ilst_np[:10]}')
        preds, classifications = run_ai(self._ai_model, ilst_np)

        preds = [[None if np.isnan(i) else np.float32(i).item() for i in pred_list] for pred_list in preds]

        col_len = len(classifications[0])
        final_cls = [[] for _ in range(col_len)]

        for i in range(col_len):
            for j in range(len(classifications)):
                final_cls[i].append(classifications[j][i])
        
        final_cls = [int(any(i)) for i in final_cls]

        if 1 in final_cls:
            flipped_preds = [[] for _ in range(col_len)]

            for i in range(col_len):
                for j in range(len(preds)):
                    flipped_preds[i].append(preds[j][i])

            with open('./jsonlog.json', 'r+') as f:
                fl = json.load(f)

            now = datetime.datetime.strftime(datetime.datetime.now(), WANTED_DATETIME_FORMAT)

            indices = [i for i, a in enumerate(final_cls) if a == 1]
            for index in indices:
                i = input_list[index-5:index+1]
                c = final_cls[index-5:index+1]
                p = flipped_preds[index-5:index+1]
                fl.append({
                    "time": now,
                    "input": i,
                    "classification": c,
                    "predictions": p
                })
                
            with open('./jsonlog.json', 'w') as f:
                json.dump(fl, f)

        return preds, final_cls

    def train_ai(self, table_name, label_columns, save_ai=False, save_ai_path='ai/saved_models/temp_ai', **kwargs):
        """ 
            Trains AI model with target_column data. It's possible to save the newly trained model through this function.
            
            Args:
                table_name      : str
                label_columns   : list<str>
                save_ai         : bool
                save_ai_path    : str
            Returns:
                -
            Raises:
                -
        """

        cols = self.get_database_column_names(table_name)
        col2idx = {k:i for i, k in enumerate(cols)}

        pred_cols = self.get_prediction_column_names(table_name)

        data_cols = [c for c in cols if c not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME, *pred_cols)]

        data = self.get_all_data(table_name)
        data_dct = {}

        for col in data_cols:
            col_id = col2idx[col]

            col_vals = [data[i][col_id] for i in range(len(data))]
            data_dct[col] = col_vals

        df = pd.DataFrame.from_dict(data_dct)
        window = ai.create_window(df, input_width=kwargs.get('input_width', 3), 
                                      label_width=kwargs.get('label_width', 3), 
                                      shift=kwargs.get('shift', 1),
                                      label_columns=label_columns)
        output_dim = len(self.get_prediction_column_names(table_name))
        new_ai = ai.create_ai_model(output_dim)
        print(f'Training on data such as {window.train_df.head()}')
        ai.train_ai(new_ai, window.train, window.val, **kwargs)

        self._ai_model = new_ai

        if save_ai:
            ai.save_ai_model(self._ai_model, save_ai_path)

    def classify_database(self, table_name):
        """
            Classifies the entire database

            Args:
                table_name: str
            
            Returns:
                bool

            Raises:
                -
        """
        if not self._load_ai:
            return False
        data = self.get_all_data(table_name)

        cols = self.get_database_column_names(table_name)
        sens_cols = self.get_sensor_column_names(table_name)
        sens_cols_idx = [cols.index(sens_col) for sens_col in sens_cols]

        data_lst = []
        for row in data:
            data = [row[sens_col_idx] for sens_col_idx in sens_cols_idx]
            data_lst.append(data)

        preds, classifications = self.classify_datapoints('atable', data_lst, use_historical=False)
        
        count = len(classifications)

        for i in range(count):
            prediction = [p[i] for p in preds]
            classification = classifications[i]

            edit_data(self._curs, table_name, {
                **{PREDICTION_COLUMN_NAME + sens_cols[j]:prediction[j] for j in range(len(prediction)) },
                CLASSIFICATION_COLUMN_NAME:classification
            }, {
                ID_COLUMN_NAME: i
            })
        return True
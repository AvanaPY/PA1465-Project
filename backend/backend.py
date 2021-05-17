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
PREDICTION_COLUMN_NAME = 'prediction'
ID_COLUMN_NAME = 'id'

WANTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class BackendBase:
    def __init__(self, confparser, database_section='mysql', ai_model='3, 1, 1'):
        self._my_db, self._db_config = create_sql_connection(confparser=confparser, section=database_section)
        self._curs = self._my_db.cursor()

        # self._ai_model, self._ai_input_size, self._ai_shift_size, self._ai_output_size = load_ai_model(f'./ai/saved_models/{ai_model}')
        
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
            A function for gatting all the columns in the table

            Args:
                table_name: str
            
            Returns:
                database_col_names: list of str - each string is a column name

            Raises:
                -
        """
        my_sql_command = f'DESCRIBE {table_name}'
        self._curs.execute(my_sql_command)
        desc = self._curs.fetchall()

        database_col_names = list((a[0] for a in desc))
        return database_col_names

    def _compatability_check(self, data, table_name):
        ''' 
            Checks the compatibility of a json document against the database table.

            A (probably) very over-engineered method that checks whether or not a json document is compatible with the database. 
            It achieves this by comparing the column names, types, and sizes to the database's own columns.

            This method assumes that the table exists in the database already, otherwise nothing happens.

            Args:
                data : dict - json document
                table_name: str - the table name

            Returns:
                boolean - Wether or not it's compatible

            Raises:
                Backend.Error
        '''
        try:
            # Ask the database for the table's data types
            database_col_names, database_col_types = self._get_database_description_no_id_column(table_name)

        except merrors.Error as e:
            raise backend_errors.TableDoesNotExistException(table_name)
        except Exception as e:
            raise

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

    def create_table_based_on_data_dict(self, table_name, data, **kwargs):
        table_types = self._create_table_dict(data, **kwargs)
        create_table(self._curs, table_name, table_types)

    def delete_table(self, table_name):
        try:
            drop_table(self._curs, table_name)
        except Exception as e:
            print(f'backend.delete_table | Failed to delete table {table_name}: {str(e)}')
            pass

    def import_data_json(self, path_to_file, database_table, **kwargs):
        """
            Imports data from a json file and converts it into dict

            Args:
                path_to_file: str
            
            Returns:
                dct: a dictionary containing the data in the json file 

            Raises:
                Propagates any errors
        """
        with open(path_to_file, "r") as f:
            dct = json.load(f)

        self.add_dict_to_database(dct, database_table, **kwargs)
                   
    def import_data_csv(self, path_to_file, database_table, **kwargs):
        """
            Imports data from a csv file and converts it into dict

            Args:
                path_to_file: str
            
            Returns:
                dct: a dictionary containing the data in the csv file 

            Raises:
                Propagates any errors
        """
        dct = pd.read_csv(path_to_file).to_dict()
        dct = { key: [val for val in dct[key].values() ] for key in dct }
        self.add_dict_to_database(dct, database_table, **kwargs)
    
    def export_data_json(self, path_to_file, database_table, **kwargs):
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
                data_dict: dict - a dictionary containing the data from the import functions
                database_table: str - the table name in the database
                date_col: str - The column that should be considered as the datetime column

            Returns:
                Nothing

            Raises:
                Propagates any errors
        """
        self.check_has_classifications(database_table, data_dict, **kwargs)
        self.check_has_datetime_column(database_table, data_dict, **kwargs)

        keys = list(data_dict.keys())
        for key in keys:
            if key.lower() == "id":
                del data_dict[key]


        try:
            self._compatability_check(data_dict, database_table)
        
        except backend_errors.TableDoesNotExistException:
            self.create_table_based_on_data_dict(database_table, data_dict, date_col=date_col, **kwargs)
            self._compatability_check(data_dict, database_table)
        
        except:
            raise

        data_dict = self._sort_data_dictionary(data_dict)

        try:
            inv_dct = self._invert_dictionary(data_dict)
            for row in inv_dct:
                insert_data(self._curs, database_table, row)
        except Exception as e:
            raise

    def _sort_data_dictionary(self, data_dict : dict):
        """
            Sorts a dictionary into the desired structure

            Args:
                data_dict : dict

            Returns:
                -

            Raises:
                -
        """
        sorted_data = {}
        for key in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, PREDICTION_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME):
            if key in data_dict:
                sorted_data[key] = data_dict.get(key)

        for key in data_dict:
            if key not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, PREDICTION_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME):
                sorted_data[key] = data_dict.get(key)
        return sorted_data
    def _create_table_dict(self, data_dict, **kwargs):
        """
            Creates a table type dict based on a data dictionary

            Args:
                data_dict: A dictionary of data values
                date_col[optional]: Which column in the data_dict that should be interpreted as datetime

            Returns:
                Dictionary of column-name:column-sql-types

            Raises:
                None
        """
        type_dict = {
            str: "VARCHAR(255)",
            int: "INT",
            float: "FLOAT"
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
        dct[PREDICTION_COLUMN_NAME] = 'FLOAT(6)'

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
                None
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
            A wrapping function for returning all the tables in the databasse

            Args:
                -
            
            Returns:
                tables: a list of all tables in the database

            Raises:
                No tables available error
        """
        try:
            tables = show_tables(self._curs)
            return tables
        except:
            raise

    def get_all_data(self, table_name, convert_datetime=False):
        """ 
            A wrapping function for returning all the data in the table

            Args:
                table_name: str
            
            Returns:
                data: a list of touples containing the data of the database, where each touple is a row

            Raises:
                -
        """
        try:
            data = get_data(self._curs, table_name)
            if convert_datetime:
                self._convert_row_datetime(table_name, data)
            return data 
        except merrors.ProgrammingError as e:
            if e.errno == 1146:
                raise backend_errors.TableDoesNotExistException(table_name)
            raise

    def _convert_row_datetime(self, table_name, data):
        """ Converts the "date" column in the data from datetime.datetime objects to string values.

            Args:
                table_name - str
                data : list[tuple]

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

    def check_has_classifications(self, table_name : str, data : dict, **kwargs):
        """ 
            Checks whether or not data has classification data.

            Checks if the data has a classification column, if it doesn't it adds the column and also classifies every "row" in the data. 
            It also checks if it has a "prediction" column, if it doesn't it also adds this column to the data with new prediction values.

            Args:
                data: dict - Data dictionary of format
                {
                    "key1": [ value1, value2 ],
                    "key2": [ value3, value4 ]
                }
            Returns:
                -
            Raises:
                -

        """
        col_names = list(data.keys())
        col_values = [data[key] for key in data.keys() if key not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME, PREDICTION_COLUMN_NAME)]
        if not CLASSIFICATION_COLUMN_NAME in col_names or not PREDICTION_COLUMN_NAME in col_names:
            rows = []
            for i in range(len(col_values[0])):
                row = [values[i] for values in col_values]
                rows.append(row)

            # predictions, classifications = self.classify_datapoints(table_name, rows, use_historical=kwargs.get('use_historical', False))
            predictions, classifications = [0] * len(rows), [0] * len(rows)

            if not CLASSIFICATION_COLUMN_NAME in col_names:
                data[CLASSIFICATION_COLUMN_NAME] = classifications
            if not PREDICTION_COLUMN_NAME in col_names:
                data[PREDICTION_COLUMN_NAME] = predictions
            
    def check_has_datetime_column(self, table_name : str, data : dict, **kwargs):
        if DATETIME_COLUMN_NAME not in data:
            data_points = len(list(data.values())[0])
            t = datetime.datetime.now()
            t = t.strftime(WANTED_DATETIME_FORMAT)

            data[DATETIME_COLUMN_NAME] = [t for _ in range(data_points)]
        
        else:
            date_format = "%Y-%m-%d"
            for i, v in enumerate(data[DATETIME_COLUMN_NAME]):
                try:
                    dt_obj = datetime.datetime.strptime(v, WANTED_DATETIME_FORMAT)
                except:
                    try:
                        dt_obj = datetime.datetime.strptime(v, date_format)
                    except:
                        dt_obj = datetime.datetime.now()
                    data[DATETIME_COLUMN_NAME][i] = datetime.datetime.strftime(dt_obj, WANTED_DATETIME_FORMAT)
    
    # TODO: Alert for anomaly function
    def scream(self):
        """
            Screams in python
        """
        print("REEEEEEEEE")

    def edit_column_value(self, table_name : str, id : int, column_name : str, new_column_value):
        """ 
            Edits the value in a database

            Args:
                table_name : str - table name
                id: int - the id of the row of the datapoint being edited
                column_name : str - Name of the column
                new_column_value: any - Value to insert into the table
            Returns:
                -
            Raises:
                Any propagated errors
        """
        try :
            edit_data(self._curs, table_name,
                { column_name : new_column_value },
                { ID_COLUMN_NAME: id }
            )
        except merrors.ProgrammingError as e:
            if e.errno == 1146:
                raise backend_errors.TableDoesNotExistException(table_name)
            else:
                raise
        except:
            raise

    def edit_classification(self, table_name : str, id : int , classification : bool):
        """ 
            Edits a classification in the table

            Args:
                table_name : str - table name
                id: int - the id of the row of the datapoint being edited
                classification: int - the classification of the datapoint, either 1 (True) or 0 (False) 
            Returns:
                -
            Raises:
                Any propagated errors
        """
        self.edit_column_value(table_name, id, CLASSIFICATION_COLUMN_NAME, classification)
        
    def _delete_data_point(self, table_name : str, id : int):
        """
            Delets a datapoint

            Args:
                table_name : str - table name
                id: int - the id of the datapint being deleted
            Returns:
                -
            Raises:
                Any propagated errors
        """
        try :
            delete_data(self._curs, table_name, { "id" : id })
        except Exception as e:
            print(e) # TODO: Same shit here, proper error

    def _get_all_non_classified(self, table_name, NON_CLASSIFIED_VALUE=None, convert_datetime=False, **kwargs):
        """ 
            Returns all non-classified data points
            
            Args:
                _table_name: str - Default None
            Returns:
                data: a list of touples where each touple is a row in the databasae
            Raises:
                Any propagated errors
        """

        try:
            data = get_data(self._curs, table_name, column_dictionary={
                CLASSIFICATION_COLUMN_NAME: NON_CLASSIFIED_VALUE,
            })
            if convert_datetime:
                self._convert_row_datetime(table_name, data)
            return data
        except Exception as e:
            raise
            # TODO: Make this a proper exception instead

    def _get_all_anomalies(self, table_name):
        """ 
            Returns all data points where the calssification column is 1
            
            Args:
                -
            Returns:
                data: a list of touples where each touple is a row in the database
            Raises:
                -
        """
        my_sql_command = f'SELECT * FROM {table_name} WHERE classification = 1;'
        self._curs.execute(my_sql_command)
        data = self._curs.fetchall()
        return data

    def strip_columns_from_data_rows(self, table_name : str, data : list, cols_to_strip : list):
        """
            SUPPOSE THAT `data` IS COLUMN-WISE ORDERED ACCORDING TO THE GOD DAMN DATABASE
        """
        data_cols = self.get_database_column_names(table_name)

        for i, row in enumerate(data):
            row = list(row)
            for d, col in zip(row[:], data_cols):
                if col in cols_to_strip:
                    row.remove(d)
            data[i] = row

    def classify_datapoints(self, table_name : str, datapoints : list, use_historical : bool=True):
        #self.model #is a thing tbc
        #self.input #is maby a thing

        if use_historical:
            n = self._ai_input_size # Amount of datapoints the AI will use
            try:
                n_last_datapoints = get_data(self._curs, table_name, order_by=[DATETIME_COLUMN_NAME], order_by_asc_desc='DESC', limit_row_count=n)
            except merrors.ProgrammingError as e:
                if e.errno == 1146:
                    raise backend_errors.TableDoesNotExistException(table_name)
                raise e
            except:
                raise
            n_last_datapoints = list(reversed(n_last_datapoints))

            self.strip_columns_from_data_rows(table_name, n_last_datapoints, 
                                            [ID_COLUMN_NAME, DATETIME_COLUMN_NAME, PREDICTION_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME])

            input_list = [*n_last_datapoints, *datapoints]
        else:
            input_list = [*datapoints]
            if len(input_list) < self._ai_input_size + self._ai_shift_size:
                raise backend_errors.InputListSizeNotMachingException(len(input_list), self._ai_input_size + self._ai_shift_size) 

        preds, classifications = run_ai(self._ai_model, input_list)
        preds = [np.float32(i).item() for i in preds]

        if use_historical:
            preds, classifications = preds[self._ai_input_size:], classifications[self._ai_input_size:]

        preds = [(None if np.isnan(i) else i) for i in preds]
        
        return preds, classifications

    def train_ai(self, table_name, target_column='sensor1'): #TODO: Jävlar vad du gnäller om TODOs samuel
        cols = self.get_database_column_names(table_name)
        col2idx = {k:i for i, k in enumerate(cols)}

        data_cols = [c for c in cols if c not in (ID_COLUMN_NAME, DATETIME_COLUMN_NAME, PREDICTION_COLUMN_NAME, CLASSIFICATION_COLUMN_NAME)]

        data = self.get_all_data(table_name)
        data_dct = {}

        for col in data_cols:
            col_id = col2idx[col]

            col_vals = [data[i][col_id] for i in range(len(data))]
            data_dct[col] = col_vals

        df = pd.DataFrame.from_dict(data_dct)

        window = ai.create_window(df, input_width=self._ai_input_size, 
                                    label_width=1, 
                                    shift=self._ai_shift_size,
                                    label_columns=[target_column])
        ai.train_ai(self._ai_model, window.train, window.val, max_epochs=100)
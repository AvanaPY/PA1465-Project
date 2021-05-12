import json
import csv
import pandas as pd
import mysql.connector.errors as merrors
import datetime

from ai import *

from database import *

from .ext import sql_type_to_python_type, all_type_equal_or_none, _all_types_not_equal
import backend.errors as backend_errors

DATETIME_COLUMN_NAME = 'date' # TODO: Check if this exists in imported data
CLASSIFICATION_COLUMN_NAME = 'classification'
PREDICTION_COLUMN_NAME = 'prediction'
ID_COLUMN_NAME = 'id'

WANTED_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class BackendBase:
    def __init__(self, confparser, database_section='mysql'):
        self._my_db, self._db_config = create_sql_connection(confparser=confparser, section=database_section)
        self._curs = self._my_db.cursor()
        self._current_table = None                                                          # The current table name that is being under consideration
                                                                                            # This is more a temporary solution and should be done on the front end instead
        try:
            drop_table(self._curs, 'atable')
        except:
            pass

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
        self.check_has_classifications(data_dict)

        keys = list(data_dict.keys())
        for key in keys:
            if key.lower() == "id":
                del data_dict[key]
        
        date_format = "%Y-%m-%d"
        if date_col != None and datetime.datetime.strptime(data_dict[date_col][0], date_format): # TODO: Move the format check in the loop instead to check for
                                                                                                 # formatting on each datapoint instead of just the first
            for i, row in enumerate(data_dict[date_col]):
                row += " 00:00:00"
                data_dict[date_col][i] = row

        try:
            self._compatability_check(data_dict, database_table)
        
        except backend_errors.TableDoesNotExistException:
            self.create_table_based_on_data_dict(database_table, data_dict, date_col=date_col, **kwargs)
            self._compatability_check(data_dict, database_table)
        
        except:
            raise
        try:
            inv_dct = self._invert_dictionary(data_dict)
            for row in inv_dct:
                insert_data(self._curs, database_table, row)
        except Exception as e:
            raise

    def _create_table_dict(self, data_dict, date_col=None, id_colum_name=None): #TODO: Replace date_col with DATETIME_COLUMN_NAME instead
                                                                                # Because it's better that we reserve the name than give them
                                                                                # the option to destroy our backend
                                                                                # because I (Emil) don't want to bother writing very advanced
                                                                                # code that will check that much
                                                                                # so it's better to just not let them have fun
                                                                                # 10/10 would code again
                                                                                # yeet :tboof:
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
            int: "INT(6)"
        }
        
        dct = {
            "id": 'INT(6) PRIMARY KEY AUTO_INCREMENT'
        }

        col_names = data_dict.keys()
        for col in col_names:
            data_type = type(data_dict[col][0])
            if date_col == col:
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
        data = get_data(self._curs, table_name)
        if convert_datetime:
            self._convert_row_datetime(table_name, data)
        return data 

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


    def set_current_table(self, table_name):
        """ 
            Sets the current table name

            Sets the current table name under consideration to a value.

            Args:
                table_name: str
            
            Returns:
                -

            Raises:
                backend.errors
        """
        tables = show_tables(self._curs)


        table_exists = False

        for table in tables :
            if table[0] == table_name :
                table_exists = True

        if table_exists == False :
            raise backend_errors.TableDoesNotExistException(table_name)
        else :
            self._current_table = table_name
            #print(f"Current device: {self._current_table}")

    def reset_current_table(self):
        """ 
            Resets the current table name

            Args:
                -
            
            Returns:
                -

            Raises:
                -
        """
        self._current_table = None

    def get_current_table(self):
        """ 
            Returns the current table saved in the backend

            Args:
                -
            
            Returns:
                self._current_table: str

            Raises:
                -
        """
        return self._current_table    

    def check_has_classifications(self, data):
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
        col_values = [data[key] for key in data.keys()]
        if not CLASSIFICATION_COLUMN_NAME in col_names or not PREDICTION_COLUMN_NAME in col_names:
            classifications, prediction_values = [], []
            for i in range(len(col_values[0])):
                prediction, classification = 0, 0 # TODO: Use the AI Api to generate those

                classifications.append(classification)
                prediction_values.append(prediction)
            
            if not CLASSIFICATION_COLUMN_NAME in col_names:
                data[CLASSIFICATION_COLUMN_NAME] = classifications
            if not PREDICTION_COLUMN_NAME in col_names:
                data[PREDICTION_COLUMN_NAME] = prediction_values
            
    
    def edit_classification(self, id):
        """ 
            Edits a classification
            
            Args:
                id: int - the id of the datapoint being edited
            Returns:
                -
            Raises:
                backend.errors
        """
        pass
    
    # TODO: Alert for anomaly function
    def scream(self):
        """
            Screams in python
        """
        print("REEEEEEEEE")

    def _insert_classifications(self, id, classification):
        """ 
            Inserts a classification into the table

            Args:
                id: int - the id of the row of the datapoint being edited
                classification: int - the classification of the datapoint, either 1 (True) or 0 (False) 
            Returns:
                -
            Raises:
                Any propagated errors
        """
        try :
            edit_data(self._curs, self._current_table, { "classification": classification }, { "id" : id })
            #print(get_data(self._curs, self._current_table, { "id" : id }))
            #print("Successful")
        except Exception as e:
            print(e)
        
    def _delete_data_point(self, id):
        """
            Delets a datapoint

            Args:
                id: int - the id of the datapint being deleted
            Returns:
                -
            Raises:
                Any propagated errors
        """
        try :
            delete_data(self._curs, self._current_table, { "id" : id })
            #print("Successful")
        except Exception as e:
            print(e)

    def _get_all_non_classified(self, table_name, NON_CLASSIFIED_VALUE=None, convert_datetime=False):
        """ 
            Returns all non-classified data points
            
            Args:
                _table_name: str - Default None
            Returns:
                data: a list of touples where each touple is a row in the databasae
            Raises:
                Any propagated errors
        """

        #table_name = ""

        # if _table_name == None:
        #     table_name = self.get_current_table
        # else:
        #     table_name = _table_name

        try:
            data = get_data(self._curs, table_name, column_dictionary={
                CLASSIFICATION_COLUMN_NAME: NON_CLASSIFIED_VALUE
            })
            if convert_datetime:
                self._convert_row_datetime(table_name, data)
            return data
        except Exception as e:
            print("Error in _get_all_non_classified(): ", str(e))

    def _get_all_anomalies(self):
        """ 
            Returns all data points where the calssification column is 1
            
            Args:
                -
            Returns:
                data: a list of touples where each touple is a row in the database
            Raises:
                -
        """
        my_sql_command = f'SELECT * FROM {self._current_table} WHERE classification = 1;'
        self._curs.execute(my_sql_command)
        data = self._curs.fetchall()
        return data

    def get_predictions(self):
        #self.model #is a thing tbc
        #self.input #is maby a thing
        run_ai(model, input_list)


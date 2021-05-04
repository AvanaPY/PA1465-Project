import json
import csv
import pandas as pd
import mysql.connector.errors as merrors

from database import *

from .ext import sql_type_to_python_type, all_type_equal_or_none, _all_types_not_equal
import backend.errors as backend_errors

CLASSIFICATION_COLUMN_NAME = "classification"

class BackendBase:
    def __init__(self, config_file_name="config.ini", section="mysql"):
        self._my_db, self._db_config = create_sql_connection(config_file_name, section)
        self._curs = self._my_db.cursor()
        self._current_table = None                                                          # The current table name that is being under consideration
                                                                                            # This is more a temporary solution and should be done on the front end instead
        # try:
        #     desc = drop_table(self._curs, 'atable')
        # except:
        #     pass

    def _compatability_check(self, data, table_name):
        ''' Checks the compatibility of a json document against the database table.

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
            my_sql_command = f'DESCRIBE {table_name}'
            self._curs.execute(my_sql_command)
            desc = self._curs.fetchall()

            database_col_names = list((a[0] for a in desc))
            

        except merrors.Error as e:
            raise backend_errors.TableDoesNotExistException(table_name)
        except Exception as e:
            raise

        # Fast check to make sure the column counts are the same
        data_col_names = data.keys()
        if len(database_col_names) - 1 != len(data_col_names):
            raise backend_errors.ColumnCountNotCorrectException('Invalid column count, make sure that every column in the database also exists in the JSON file.')

        # Checking that all the column names in the data exists in the database too
        for name in data_col_names:
            if name not in database_col_names:
                raise backend_errors.InvalidColumnNameException(name)

        # Checking that all the items in the columns have the exact same type
        database_col_types = list((sql_type_to_python_type(a[1].decode('utf-8'))for a in desc))
        data_column_lengths = [ len(data[key]) for key in data ]
        all_same = all([a == data_column_lengths[0] for a in data_column_lengths])
        if not all_same:
            raise backend_errors.ColumnLengthsDifferException()

        # Checking that the columns in the data have the same type as in the database.
        data_types = {
            key: all_type_equal_or_none([type(a) for a in data[key]]) for key in data
        }
        for i, key in enumerate(data_types):
            t = data_types[key]
            # Column type checking
            if t is _all_types_not_equal:
                raise backend_errors.ColumnTypesNotSameException(key, data[key])
            # Database cross-checking by type
            if t != database_col_types[i]:
                raise backend_errors.ColumnTypesNotMatchingException(key, database_col_types[i], t)
                
        # If no errors occured and nothing seems wrong, let's just return True.
        return True

    def create_table_based_on_data_dict(self, table_name, data, **kwargs):
        table_types = self._create_table_dict(data, **kwargs)
        create_table(self._curs, table_name, table_types)

    def import_data_json(self, path_to_file, database_table, **kwargs):
        """
            imports data from a json file and converts it into dict

            Args:
                path_to_file: str
            
            Returns:
                dct: a dictionary containing the data in the json file 

            Raises:
                Propagates any errors
        """
        with open(path_to_file, "r") as f:
            dct = json.load(f)
        print(dct)

        self.add_dict_to_database(dct, database_table, **kwargs)
        
            
    def import_data_csv(self, path_to_file, database_table, **kwargs):
        """
            imports data from a csv file and converts it into dict

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
    
    def add_dict_to_database(self, data_dict, database_table, date_col=None, **kwargs):
        """ Adds a dictionary to the database.

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
        try:
            self._compatability_check(data_dict, database_table)
        except backend_errors.TableDoesNotExistException:
            self.create_table_based_on_data_dict(database_table, data_dict, **kwargs)
            self._compatability_check(data_dict, database_table)
        except:
            raise
        try:
            inv_dct = self._invert_dictionary(data_dict)
            for row in inv_dct:
                insert_data(self._curs, database_table, row)
        except Exception as e:
            raise

    def _create_table_dict(self, data_dict, date_col=None, id_colum_name=None):
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
        dct = {}
        type_dict = {
            str: "VARCHAR(255)",
            int: "INT(6)"
        }
        
        
        col_names = data_dict.keys()
        for col in col_names:
            data_type = type(data_dict[col][0])
            if date_col == col:
                dct[col] = 'DATETIME'
            else:
                dct[col] = type_dict[data_type]
        #if not id_colum_name is None:
            #print("Added Id column!")
        dct["id"] = 'INT(6) PRIMARY KEY AUTO_INCREMENT'
        
        # Classification column
        dct[CLASSIFICATION_COLUMN_NAME] = "BIT"

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
        """ Description

            Args:
                
            
            Returns:
                -

            Raises:
                -
        """
        tables = show_tables(self._curs)

        for table in tables :
            print(table[0])

    def set_current_table(self, table_name):
        """ Sets the current table name

            Sets the current table name under consideration to a value.

            Args:
                table_name: str
            
            Returns:
                -

            Raises:
                -
        """
        tables = show_tables(self._curs)


        table_exists = False

        for table in tables :
            if table[0] == table_name :

                table_exists = True

        if table_exists == False :
            print("The table you selected was not found. Try again.")
        else :
            self._current_table = table_name
            print(f"Current device: {self._current_table}")

    def get_current_table(self):
        """ Description

            Args:
                
            
            Returns:
                -

            Raises:
                -
        """
        return self._current_table

    #def get_tables(self):
        """ Prints all the tables

            Args:
                -   
            Returns
                -
            Raises
                -
        """
   #     try:    
    #        tables = show_tables(self._curs)
   #         print(tables)
   #     except Exception as e:
   #         print(str(e))   */     

    def check_has_classifications(self, data):
        """ Checks whether or not data has the classification column

            Checks if the data has a classification column, if it doesn't it adds the column and also classifies every "row" in the data.

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
        if not CLASSIFICATION_COLUMN_NAME in data:
            data_keys = data.keys()
            cols = [data[key] for key in data_keys]
            classifications = []
            for i in range(len(cols[0])):
                d = tuple([data[key][i] for key in data_keys])
                
                classification = 0 # TODO: Use the AI Api to generate this
                classifications.append(classification)
            
            data[CLASSIFICATION_COLUMN_NAME] = classifications
    def edit_classification(self, dp):
        """ Edits a classification
            
            Args:
                dp: ???
            Returns:
                -
            Raises:
                -
        """
        pass

    def scream(self):
        """
            Screams in python
        """
        print("REEEEEEEEE")

    def helo(self):
        """ Says hello

            Args:
                -
            Returns:
                -
            Raises:
                -
        """
        data = self._insert_classifications()
        print(data)

    def _insert_classifications(self, id, classification):
        """ Not sure

            Args:
                -
            Returns:
                -
            Raises:
                -
        """
        try :
            edit_data(self._curs, self._current_table, { "classification": classification }, { "id" : id })
            print(get_data(self._curs, self._current_table, { "id" : id }))
            print("Successful")
        except Exception as e:
            print(e)
        

    def _delete_data_point(self, id):
        """ Not sure

            Args:
                -
            Returns:
                -
            Raises:
                -
        """
        try :
            delete_data(self._curs, self._current_table, { "id" : id })
            print("Successful")
        except Exception as e:
            print(e)
        

    def _get_all_non_classified(self):
        """ Returns all non-classified data points
            Args:
                -
            Returns:
                -
            Raises:
                -
        """
        my_sql_command = f'SELECT * FROM {self._current_table};'
        self._curs.execute(my_sql_command)
        data = self._curs.fetchall()
        return data

    def _get_all_anomalies(self):
        """ Returns all non-classified data points
            Args:
                -
            Returns:
                -
            Raises:
                -
        """
        my_sql_command = f'SELECT * FROM {self._current_table} WHERE classification = 1;'
        self._curs.execute(my_sql_command)
        data = self._curs.fetchall()
        return data

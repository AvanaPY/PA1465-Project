import json
import csv
import pandas as pd
import mysql.connector.errors as merrors

from database import *

from .ext import sql_type_to_python_type, all_type_equal_or_none, _all_types_not_equal


class BackendBase:
    def __init__(self, config_file_name="config.ini", section="mysql"):
        self._my_db, self._db_config = create_sql_connection(config_file_name, section)
        self._curs = self._my_db.cursor()
        # try:
        #     desc = drop_table(self._curs, 'atable')
        # except:
        #     pass

    def compatability_check_json(self, data, table_name):
        '''
        - Kolonnamn som nycklar
	    - kolonndata i form av en lista
	    - Samma datatyper i hela kolonnen
        '''
        try:
            # Ask the database for the table's data types
            my_sql_command = f'DESCRIBE {table_name}'
            self._curs.execute(my_sql_command)
            desc = self._curs.fetchall()

            database_col_names = list((a[0] for a in desc))
            print(f'Database col names: {database_col_names}')

            data_col_names = data.keys()
            if len(database_col_names) != len(data_col_names):
                return False, 'Invalid column names, make sure that every column in the database also exists in the JSON file.'

            for name in data_col_names:
                if name not in database_col_names:
                    return False, 'Invalid column names'

            database_col_types = list((sql_type_to_python_type(a[1].decode('utf-8'))for a in desc))
            print(f'Database col types: {database_col_types}')
            
            data_types = {
                key: all_type_equal_or_none([type(a) for a in data[key]]) for key in data
            }
            print(f'Data types: {data_types}')
            for i, key in enumerate(data_types):
                t = data_types[key]
                if t is _all_types_not_equal:
                    return False, f'One or more columns in the data contains values which are not of the same type: Column "{key}" of data "{data[key]}"'
                if t != database_col_types[i]:
                    return False, f'Column type does not match with the database\'s column type: Colum "{key}" with type {database_col_types[i]} against data type {t}.'

        except merrors.Error as e:
            return False, str(e)
        
        return True, None



    def compatability_check_csv(self, data, table_name):
        '''
        - kolonnamn på första raden
        - Samma datatyper i hela kolonnen
        - Får ej ha fler datapunkter i en rad än vad det finns kolonner.
        '''

        compatability = False
        
        try:
            my_sql_command = f'DESCRIBE {table_name}'
            self._curs.execute(my_sql_command)
            desc = self._curs.fetchall()
            col_names = desc[0]
            with open('some.csv', newline='') as f:
                reader = csv.reader(f)
                row1 = next(reader)
                data_col_names = row1.split(',')

            for name in data_col_names:
                if name not in col_names:
                    return compatability
        except merrors.Error as e:
            print(f'Error: {e}')

        return

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
                None
        """
        with open(path_to_file, "r") as f:
            dct = json.load(f)
        lens = [ len(dct[k]) for k in dct ]
        lens_equal = all([k == lens[0] for k in lens])
        if not lens_equal:
            raise Exception('import_data_json error: JSON columns are not equally long')
        self.add_dict_to_database(dct, database_table, **kwargs)

    def import_data_csv(self, path_to_file, database_table):
        """
            imports data from a csv file and converts it into dict

            Args:
                path_to_file: str
            
            Returns:
                dct: a dictionary containing the data in the csv file 

            Raises:
                None
        """
        dct = pd.read_csv(path_to_file).to_dict()
        dct = { key: [val for val in dct[key].values() ] for key in dct }
        self.add_dict_to_database(dct, database_table)
    
    def add_dict_to_database(self, data_dict, database_table, date_col=None, **kwargs):
        """
            Adds a dictionary to the database

            Args:
                data_dict: a dictionary containing the data from the import functions
            
            Returns:
                Nothing

            Raises:
                :tboof:
        """
        try:
            self.create_table_based_on_data_dict(database_table, data_dict, create_id_column=True)
            inv_dct = self._invert_dictionary(data_dict)
            for row in inv_dct:
                insert_data(self._curs, database_table, row)
        except Exception as e:
            raise

        #print(get_data(self._curs, database_table))

    def _create_table_dict(self, data_dict, date_col=None, create_id_column=False):
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
        
        if create_id_column:
            dct['ID'] = 'INT(6) PRIMARY KEY AUTO_INCREMENT'
        
        col_names = data_dict.keys()
        for col in col_names:
            data_type = type(data_dict[col][0])
            if date_col == col:
                dct[col] = 'DATETIME'
            else:
                dct[col] = type_dict[data_type]
        
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





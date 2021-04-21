import json
import csv
import pandas as pd
from database import *

class BackendBase:
    def __init__(self, config_file_name="config.ini", section="mysql"):
        self._my_db, self._db_config = create_sql_connection(config_file_name, section)
        self._curs = self._my_db.cursor()

    def import_data_json(self, path_to_file):
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
        self.add_dict_to_database(dct)

    def import_data_csv(self, path_to_file):
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
        dict_with_lists = { key: [val for val in dct[key].values() ] for key in dct }
        self.add_dict_to_database(dict_with_lists)
    
    def add_dict_to_database(self, data_dict, database_table, date_col=None):
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
            table_dct = _create_table_dict(data_dict)

            create_table(conn, table, table_dct)

            inv_dct = _invert_dictionary(data_dict)
            for row in inv_dct:
                insert_data(conn, table, row)

            drop_table(conn, table)

        except Exception as e:
            print(":tboof:")
            print(e)

    def _create_table_dict(self, data_dict, date_col=None):
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





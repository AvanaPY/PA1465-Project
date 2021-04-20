import json
import csv
import pandas as pd
from database import *

table = ""

def import_data_json(path_to_file):
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
    
    add_dict_to_database(dct)

def import_data_csv(path_to_file):
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
    add_dict_to_database(dict_with_lists)
 
def add_dict_to_database(data_dict, date_col=None):
    """
        Adds a dictionary to the database

        Args:
            data_dict: a dictionary containing the data from the import functions
        
        Returns:
            Nothing

        Raises:
            :tboof:
    """
    sql_connection_and_database, _ = create_sql_connection()
    conn = sql_connection_and_database.cursor()
    try:
        dct = create_table_dict(data_dict)
        table = "test_table"

        create_table(conn, table, dct)
        inv_dct = invert_dictionary(data_dict)
        for row in inv_dct:
            insert_data(conn, table, row)

        drop_table(conn, table)

    except Exception as e:
        print(":tboof:")
        print(e)

def create_table_dict(col_dict, date_col=None):
    dct = {}
    type_dict = {
        str: "VARCHAR(255)",
        int: "INT(6)"
    }
    col_names = col_dict.keys()
    for col in col_names:
        data_type = type(col_dict[col][0])
        if date_col == col:
            dct[col] = 'DATETIME'
        else:
            dct[col] = type_dict[data_type]
    return dct

def invert_dictionary(dct):
    keys = dct.keys()
    items_in_column = len(dct[list(keys)[0]])
    o = [ { key:None for key in keys } for _ in range(items_in_column) ] # Base dictionary
    for i in range(items_in_column):
        for key in keys:
            o[i][key] = dct[key][i]
    return o





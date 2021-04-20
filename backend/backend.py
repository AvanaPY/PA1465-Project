import json
import csv
import pandas as pd
from database import *

def import_data_json(path_to_file):
    """
        Deletes data from table_name

        Args:
            curs: a MySQLConnection cursor instance
            table_name: str
            column_dictionary: dictionary with columnname-columnvale mapping, e.g { "ID": "1", "Data1": "ABC" } for SQL lookup
        
        Returns:
            Nothing

        Raises:
            Any errors that occured from MySQLConnection
    """

    with open(path_to_file, "r") as f:
        dct = json.load(f)
    add_dict_to_database(dct)

def import_data_csv(path_to_file):
    """
        Deletes data from table_name

        Args:
            curs: a MySQLConnection cursor instance
            table_name: str
            column_dictionary: dictionary with columnname-columnvale mapping, e.g { "ID": "1", "Data1": "ABC" } for SQL lookup
        
        Returns:
            Nothing

        Raises:
            Any errors that occured from MySQLConnection
    """
    dct = pd.read_csv(path_to_file).to_dict()

    add_dict_to_database(dct)
 
def add_dict_to_database(data_dict):
    """
        Adds a dctionary to the database

        Args:
            data_dict: a dictionary containing the data from the import functions
        
        Returns:
            Nothing

        Raises:
            :tboof:
    """

    try:
        print(data_dict)
    except:
        print(":tboof:")




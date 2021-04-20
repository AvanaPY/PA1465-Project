import json
import csv
import pandas as pd
from database import *

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

    add_dict_to_database(dct)
 
def add_dict_to_database(data_dict):
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
        print(data_dict)
    except:
        print(":tboof:")




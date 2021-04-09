#https://www.w3schools.com/python/python_mysql_insert.asp
from mysql.connector import MySQLConnection
from python_mysql_dbconfig import read_db_config
 
def create_sql_connection(filename="config.ini", section="mysql"):
    """
        Creates a MySQLConnection instance connected to the database

        Args:
            filename: A configuration file for the MySQL database
            section:  section what the fuck does this even mean 

        Returns:
            my_db      : MySQLConnection
            db_config : dictionary 

        Raises:
            None
    """
    db_config = read_db_config(filename=filename, section=section)
    my_db = MySQLConnection(autocommit=True, **db_config)
    return my_db, db_config

def create_table(curs, table_name, column_dictionary={}):
    """
        Creates a table in the database

        Args:
            curs: a MySQLConnection cursor
            table_name: str
            column_dictionary: dictionary with columnname-columntype mapping, e.g { "first-name": "text", "last-name": "text", "age:", "INT" }
        
        Returns:
            None

        Raises:
            Propagates any exceptions from cursor.execute
    """
    COLUMNS = ', '.join([f'{key} {value}' for (key, value) in column_dictionary.items()])
    if COLUMNS:
        COLUMNS  = f' ({COLUMNS})'
    my_sql_command = f"CREATE TABLE {table_name}{COLUMNS}"
    print(my_sql_command)
    curs.execute(my_sql_command)

def show_databases(curs):
    my_sql_command = 'SHOW DATABASES'
    curs.execute(my_sql_command)
    for x in curs:
        print(x)

def drop_table(curs, table_name):
    my_sql_command = f'DROP TABLE {table_name}'
    curs.execute(my_sql_command)

def insert_data(curs, table_name, data_dictionary, sql_database_insert_char="%s"):
    """
        Inserts data into a table in the database

        Args:
            curs: a MySQLConnection cursor instance
            table_name: str
            data_dictionary: a dictionary with columnname-columnvalue mapping, e.g { "ID": "1", "Value": "123", "Value2", "456" }
        
        Returns:
            None

        Raises:
            Any errors that occured from MySQLConnection
    """
    COL_NAMES = [i for i in data_dictionary.keys() if not (data_dictionary.get(i) is None)]
    COL_VALS = [str(i) for i in list(data_dictionary.values()) if not (i is None)]

    my_sql_command = f"INSERT INTO {table_name} ({', '.join(COL_NAMES)}) VALUES ({', '.join([sql_database_insert_char] * len(COL_VALS))})"
    conn.execute(my_sql_command, tuple(COL_VALS))

def get_data(curs, table_name, column_dictionary=None):
    """
        Returns data into a table in the database

        Args:
            conn: a MySQLConnection instance
            column_dictionary: dictionary with columnname-columnvale mapping, e.g { "ID": "1", "Data1": "ABC" } for SQL lookup
        
        Returns:
            a tuple of data to be inserted into the database

        Raises:
            Any errors that occured from MySQLConnection
    """
    CONSTRAINTS = len(column_dictionary.items()) if column_dictionary else 0
    WHERE_CONSTRAINTS = ' AND '.join([f"{key}='{value}'" for (key, value) in column_dictionary.items()]) if CONSTRAINTS != 0 else ''

    my_sql_command = f"SELECT * FROM {table_name} {'WHERE' if CONSTRAINTS != 0 else ''} {WHERE_CONSTRAINTS};"
    conn.execute(my_sql_command)
    return conn.fetchall()

def edit_data(curs, table_name, column_names, column_values, new_data):
    """
        Returns data into a table in the database

        Args:
            conn: a MySQLConnection instance
            column_names: array of column names for SQL lookup
            column_values: array of column values that will be matched with column_names for SQL lookup
        
        Returns:
            a tuple of data to be inserted into the database

        Raises:
            Any errors that occured from MySQLConnection
    """
    return
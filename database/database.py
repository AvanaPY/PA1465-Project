#https://www.w3schools.com/python/python_mysql_insert.asp
from mysql.connector import MySQLConnection
from .python_mysql_dbconfig import read_db_config

def skip_none_dictionary(dictionary):
    keys = dictionary.keys()
    for key in list(keys):
        if dictionary[key] is None:
            dictionary.pop(key)

def column_dictionary_to_sql_and_join(dictionary, join_key=' AND '):
    safe_query_list = [f'{key}=%({key})s' for key in dictionary]     # Safe query
    WHERE_LOOK = join_key.join(safe_query_list)          
    return WHERE_LOOK 

def create_sql_connection(filename="config.ini", section="mysql"):
    """
        Creates a MySQLConnection instance connected to the database

        Args:
            filename: A configuration.ini file for the MySQL database
            section:  section of the configuration file in which the database configuration parameters are set

        Returns:
            my_db      : MySQLConnection
            db_config : dictionary 

        Raises:
            None
    """
    db_config = read_db_config(filename=filename, section=section)
    my_db = MySQLConnection(autocommit=True, **db_config)
    return my_db, db_config

def create_table(curs, table_name, column_dictionary):
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
    skip_none_dictionary(column_dictionary)
    columns = [f'{key} {value}' for key, value in column_dictionary.items()]
    columns = ', '.join(columns)

    my_sql_command = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
    curs.execute(my_sql_command)

def show_databases(curs):
    """
        Prints out all databases in the MySQL database

        Args:
            curs: a MySQLConnection cursor
        
        Returns:
            None

        Raises:
            Propagates any exceptions from cursor.execute
    """
    my_sql_command = 'SHOW DATABASES'
    curs.execute(my_sql_command)
    for x in curs:
        print(x)

def show_tables(curs):
    """
        Prints out all tables in the MySQL database

        Args:
            curs: a MySQLConnection cursor
        
        Returns:
            None

        Raises:
            Propagates any exceptions from cursor.execute
    """
    my_sql_command = 'SHOW TABLES'
    curs.execute(my_sql_command)
    for x in curs:
        print(x)
    return curs

def drop_table(curs, table_name):
    
    """
        Drops a table from a database

        Args:
            curs: a MySQLConnection cursor
            table_name: str
        
        Returns:
            None

        Raises:
            Propagates any exceptions from cursor.execute
    """
    my_sql_command = f'DROP TABLE {table_name}'
    curs.execute(my_sql_command)

def insert_data(curs, table_name, data_dictionary):
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
    skip_none_dictionary(data_dictionary)
    insert_names = ', '.join([str(key) for key in data_dictionary])
    insert_values = ', '.join([f'%({key})s' for key in data_dictionary])
    my_sql_command = f"INSERT INTO {table_name} ({insert_names}) VALUES ({insert_values})"
    curs.execute(my_sql_command, data_dictionary)

def get_data(curs, table_name, column_dictionary=None, order_by=None,order_by_asc_desc='ASC', limit_offset=0, limit_row_count=0):
    """
        Returns data into a table in the database

        Args:
            curs: a MySQLConnection cursor instance
            table_name: str
            column_dictionary: dictionary with columnname-columnvale mapping, e.g { "ID": "1", "Data1": "ABC" } for SQL lookup
            order_by: a list of column values to order by. None is default for no ordering.
            order_by_asc_desc: Whether to order by ascending ('ASC') or descending ('DESC'). 
        
        Returns:
            a tuple of data to be inserted into the database

        Raises:
            Any errors that occured from MySQLConnection
    """
    if column_dictionary:
        skip_none_dictionary(column_dictionary)
        WHERE_LOOK = column_dictionary_to_sql_and_join(column_dictionary)  # Join into an AND list
        my_sql_command = f"SELECT * FROM {table_name} WHERE {WHERE_LOOK}"
    else:
        my_sql_command = f"SELECT * FROM {table_name}"

    if order_by:
        order_by_string = ', '.join([str(v) for v in order_by])
        order_by_string = f' ORDER BY ' + order_by_string + ' ' + order_by_asc_desc
        my_sql_command += order_by_string

    if limit_row_count > 0:
        limit_string = f' LIMIT {limit_offset}, {limit_row_count}' 
        my_sql_command += limit_string

    curs.execute(my_sql_command, column_dictionary)
    return curs.fetchall()

def delete_data(curs, table_name, column_dictionary):
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
    skip_none_dictionary(column_dictionary)
    WHERE_LOOK = column_dictionary_to_sql_and_join(column_dictionary)  # Join into an AND list
    my_sql_command = f'DELETE FROM {table_name} WHERE ({WHERE_LOOK});'
    curs.execute(my_sql_command, column_dictionary)

def edit_data(curs, table_name, new_column_values, column_constraints):
    """
        Returns data into a table in the database

        Args:
            curs: a MySQLConnection cursor instance
            table_name: str
            new_column_values: column dictionary of new values
            column_constraints: column dictionary of look-up values in the database
        
        Returns:
            a tuple of data to be inserted into the database

        Raises:
            Any errors that occured from MySQLConnection
    """

    SET_VALUES = 'name=%(set_name)s, age=%(set_age)s'
    safe_query_list = [f'{key}=%(set_{key})s' for key in new_column_values]     # Safe query
    SET_VALUES = ', '.join(safe_query_list)          

    WHERE_LOOK = column_dictionary_to_sql_and_join(column_constraints, ', ')

    major_dictionary = {**column_constraints}
    for key in new_column_values:
        major_dictionary[f'set_{key}'] = new_column_values[key]
    my_sql_command = f'UPDATE {table_name} SET {SET_VALUES} WHERE ({WHERE_LOOK})'
    curs.execute(my_sql_command, major_dictionary)
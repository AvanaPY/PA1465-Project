

class Error(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TableDoesNotExistException(Error):
    def __init__(self, table_name):
        super().__init__(f'Table "{table_name}" does not exist')

class ColumnCountNotCorrectException(Error):
    def __init__(self, r):
        super().__init__(r)

class InvalidColumnNameException(Error):
    def __init__(self, name):
        super().__init__(f'Invalid column name: {name}')

class ColumnLengthsDifferException(Error):
    def __init__(self):
        super().__init__('Columns are not of equal length in data.')

class ColumnTypesNotSameException(Error):
    def __init__(self, key, data):
        super().__init__(f'One or more columns in the data contains values which are not of the same type: Column "{key}" of data "{data}"')

class ColumnTypesNotMatchingException(Error):
    def __init__(self, key, database_col_type, data_type):
        super().__init__(f'Column type does not match with the database\'s column type: Column "{key}" with type {database_col_type} against data type {data_type}.')
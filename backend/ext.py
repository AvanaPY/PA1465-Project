import backend.errors as backend_errors
_all_types_not_equal = object()

def sql_type_to_python_type(str_type : str):
    """ Converts a SQL type to a python type

        Converts a SQL type into a python type based on the string representation of the SQL type. 
        Used mainly to convert the column types of an SQL table into python types for easy type-checking.

        Args:
            str_type : str 

        Returns:
            type

        Raises:
            KeyError if unknown type
    """
    type_table = {
        'varchar': str,
        'char': str,
        'text': str,
        'int': int,
        'float': (float, int),
        'bit': int,
        'datetime':str
    }
    for t in type_table:
        if t in str_type.lower():
            return type_table[t]
    raise KeyError(f'Did not find a python type for SQL type "{str_type}".')

def all_type_equal_or_none(type_lst):
    """ Returns the type of data in the list or _all_types_not_equal if all data are not of the same type

        Iterates over the given lists and computes whether or not all types in the list are the same.
        If all the types are the same then the function returns the type, otherwise it returns _all_types_not_equal.

        Args:
            type_lst: lst[type]
        
        Returns:
            type or _all_types_not_equal

        Raises:
            Nothing
    """
    first_non_none_type = [a for a in type_lst if a is not type(None)][0]
    types = [(a == first_non_none_type or a is type(None)) for a in type_lst]
    all_same = all(types)
    if all_same:
        return first_non_none_type
    else:
        return _all_types_not_equal

def get_data_column_types(data):
    col_types = {}

    for key in data:
        types = [type(i) for i in data[key]]
        types = [i for i in types if i is not type(None)]
        t = all_type_equal_or_none(types)
        if t is not _all_types_not_equal:
            col_types[key] = t
        else:
            raise backend_errors.InvalidColumnTypeException(types)
    return col_types
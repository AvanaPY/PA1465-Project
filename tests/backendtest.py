from lib2to3.pytree import convert
import unittest
from backend import BackendBase
import backend.errors as berrors
import datetime
from configparser import ConfigParser
parser = ConfigParser()
parser.read('./config.ini')

b = BackendBase(confparser=parser, load_ai=False)
class BackendTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not b._my_db:
            raise unittest.SkipTest(f'No connected database: Cannot test Module')
    
    def tearDown(self):
        for table in b.get_tables():
            b.delete_table(table)

    def test_delete_table_null(self):
        with self.assertRaises(Exception):
            b.delete_table('')
            
    def test_delete_table_not_exist(self):
        with self.assertRaises(Exception):
            b.delete_table("not exist")
        
    def test_import_export_json(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        b.export_data_json('./tests/test_data/export.json', 't')
        
    def test_import_export_csv(self):    
        b.import_data_csv('./tests/test_data/base_csv.csv', 't')
        b.export_data_csv('./tests/test_data/export.csv', 't')

    def test_import_json_max_values(self): 
        b.import_data_json('./tests/test_data/base_json.json', 't', max_values=1)
        d = b.get_all_data('t', convert_datetime=True)
        self.assertEqual(d, [(1, '2021-05-18 11:19:00', None, 1, 4, 21, 0.0, 0.0, 0.0)])

    def test_prediction_column_name_pairs(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        pairs = b.get_sensor_prediction_column_name_pairs('t')
        self.assertEqual(pairs, [('sensor1', 'PREDICTIONsensor1'), 
                                 ('sensor2', 'PREDICTIONsensor2'), 
                                 ('sensor3', 'PREDICTIONsensor3')])
    
    def test_no_datetime_col(self):
        b.import_data_json('./tests/test_data/no_datetime_col.json', 't')
        data = b.get_all_data('t', convert_datetime=True)
        
        data = [
            (id, pred, s1, s2, s3, p1, p2, p3) for id, _, pred, s1, s2, s3, p1, p2, p3 in data
        ]
        
        self.assertEqual(data, [(1, None, 1, 4, 21, 0.0, 0.0, 0.0), 
                                (2, None, 2, 1, 7, 0.0, 0.0, 0.0), 
                                (3, None, 3, 3, -2, 0.0, 0.0, 0.0),
                                (4, None, 4, 7, 11, 0.0, 0.0, 0.0), 
                                (5, None, 5, 1, 21, 0.0, 0.0, 0.0), 
                                (6, None, 6, 3, 4, 0.0, 0.0, 0.0), 
                                (7, None, 7, 4, 11, 0.0, 0.0, 0.0)])

    def test_sensor_column_names(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        sensors = b.get_sensor_column_names('t')
        self.assertEqual(sensors, ['sensor1', 'sensor2', 'sensor3'])
        
    def test_compat_check_invalid_table_name(self):
        compatible = b._compatability_check({}, 'a')
        self.assertFalse(compatible)
        
    def test_compat_invalid_col_count(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        with self.assertRaises(berrors.ColumnCountNotCorrectException):
            b.import_data_json('./tests/test_data/invalid_col_count.json', 't')

    def test_compat_invalid_col_name(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        with self.assertRaises(berrors.InvalidColumnNameException):
            b.import_data_json('./tests/test_data/invalid_col_name.json', 't')
            
    def test_compat_invalid_col_length(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        with self.assertRaises(berrors.ColumnLengthsDifferException):
            b.import_data_json('./tests/test_data/invalid_col_length.json', 't')
            
    def test_compat_invalid_col_match(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        with self.assertRaises(berrors.ColumnTypesNotSameException):
            b.import_data_json('./tests/test_data/invalid_col_type.json', 't')
            
    def test_compat_invalid_col_type(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        with self.assertRaises(berrors.ColumnTypesNotMatchingException):
            b.import_data_json('./tests/test_data/invalid_col_type_match.json', 't')
            
    def test_classifications_no_pred_col(self):
        b.import_data_json('./tests/test_data/classification_json.json', 't')
        d = b.get_all_data('t', convert_datetime=True)
        self.assertEqual(d, [(1, '2021-05-18 11:19:00', 1, 1, 0.0), (2, '2021-05-18 11:19:10', 1, 2, 0.0)])
    
    def test_delete_data(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        b._delete_data_point('t', 1)
        data = b.get_all_data('t', convert_datetime=True)
        
        self.assertEqual(data, [(2, '2021-05-18 11:19:10', None, 2, 1, 7, 0.0, 0.0, 0.0), 
                                (3, '2021-05-18 11:19:20', None, 3, 3, -2, 0.0, 0.0, 0.0), 
                                (4, '2021-05-18 11:19:30', None, 4, 7, 11, 0.0, 0.0, 0.0), 
                                (5, '2021-05-18 11:19:40', None, 5, 1, 21, 0.0, 0.0, 0.0), 
                                (6, '2021-05-18 11:19:50', None, 6, 3, 4, 0.0, 0.0, 0.0), 
                                (7, '2021-05-18 11:19:55', None, 7, 4, 11, 0.0, 0.0, 0.0)])
    
    def test_all_non_classified(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        d = b._get_all_non_classified('t', convert_datetime=True)
        self.assertEqual(d, [(1, '2021-05-18 11:19:00', None, 1, 4, 21, 0.0, 0.0, 0.0), 
                                (2, '2021-05-18 11:19:10', None, 2, 1, 7, 0.0, 0.0, 0.0), 
                                (3, '2021-05-18 11:19:20', None, 3, 3, -2, 0.0, 0.0, 0.0), 
                                (4, '2021-05-18 11:19:30', None, 4, 7, 11, 0.0, 0.0, 0.0), 
                                (5, '2021-05-18 11:19:40', None, 5, 1, 21, 0.0, 0.0, 0.0), 
                                (6, '2021-05-18 11:19:50', None, 6, 3, 4, 0.0, 0.0, 0.0), 
                                (7, '2021-05-18 11:19:55', None, 7, 4, 11, 0.0, 0.0, 0.0)])
    
    def test_all_non_classified_not_convert_datetime(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        d = b._get_all_non_classified('t', convert_datetime=False)
        self.assertEqual(d, [(1, datetime.datetime(2021, 5, 18, 11, 19), None, 1, 4, 21, 0.0, 0.0, 0.0), 
                             (2, datetime.datetime(2021, 5, 18, 11, 19, 10), None, 2, 1, 7, 0.0, 0.0, 0.0), 
                             (3, datetime.datetime(2021, 5, 18, 11, 19, 20), None, 3, 3, -2, 0.0, 0.0, 0.0), 
                             (4, datetime.datetime(2021, 5, 18, 11, 19, 30), None, 4, 7, 11, 0.0, 0.0, 0.0), 
                             (5, datetime.datetime(2021, 5, 18, 11, 19, 40), None, 5, 1, 21, 0.0, 0.0, 0.0), 
                             (6, datetime.datetime(2021, 5, 18, 11, 19, 50), None, 6, 3, 4, 0.0, 0.0, 0.0), 
                             (7, datetime.datetime(2021, 5, 18, 11, 19, 55), None, 7, 4, 11, 0.0, 0.0, 0.0)])
    
    def test_get_anomalies(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        d = b._get_all_anomalies('t')
        self.assertEqual(d, [])
        
    def test_strip_columns(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        d = b.get_all_data('t', convert_datetime=True)
        b.strip_columns_from_data_rows('t', d, ['id', 'sensor1'])
        self.assertEqual(d, [['2021-05-18 11:19:00', None, 4, 21, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:10', None, 1, 7, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:20', None, 3, -2, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:30', None, 7, 11, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:40', None, 1, 21, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:50', None, 3, 4, 0.0, 0.0, 0.0], 
                             ['2021-05-18 11:19:55', None, 4, 11, 0.0, 0.0, 0.0]])
    
    def test_edit_classification(self):
        b.import_data_json('./tests/test_data/base_json.json', 't')
        b.edit_classification('t', 1, True)
        d = b.get_all_data('t', convert_datetime=True)
        self.assertEqual(d, [(1, '2021-05-18 11:19:00', 1, 1, 4, 21, 0.0, 0.0, 0.0), 
                            (2, '2021-05-18 11:19:10', None, 2, 1, 7, 0.0, 0.0, 0.0), 
                            (3, '2021-05-18 11:19:20', None, 3, 3, -2, 0.0, 0.0, 0.0), 
                            (4, '2021-05-18 11:19:30', None, 4, 7, 11, 0.0, 0.0, 0.0), 
                            (5, '2021-05-18 11:19:40', None, 5, 1, 21, 0.0, 0.0, 0.0), 
                            (6, '2021-05-18 11:19:50', None, 6, 3, 4, 0.0, 0.0, 0.0), 
                            (7, '2021-05-18 11:19:55', None, 7, 4, 11, 0.0, 0.0, 0.0)])
    
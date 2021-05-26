from mysql.connector.errors import DatabaseError
import backend
import unittest
import database
import backend.errors as backend_errors
from datetime import datetime

from configparser import ConfigParser
parser = ConfigParser()
parser.read('./config.ini')

b = backend.BackendBase(parser)
table_name_json = 'test_table_json'
table_name_csv  = 'test_table_csv'

try:
    b.delete_table(table_name_json)
except:
    pass

try:
    b.delete_table(table_name_csv)
except:
    pass

class BackendUnitTest(unittest.TestCase):
    def test_import_json(self):
        b.import_data_json('./test_files/base_json_file.json', table_name_json)
        try:
            b.import_data_json('./test_files/new_json_file.json', table_name_json)
        except Exception as e:
            self.assertFalse(True)
        b.delete_table(table_name_json)

    def test_import_csv(self):
        b.import_data_csv('./test_files/base_csv_file.csv', table_name_csv)
        try:
            b.import_data_csv('./test_files/new_csv_file.csv', table_name_csv)
        except Exception as e:
            self.assertFalse(True)
        b.delete_table(table_name_csv)

    def test_import_json_w_id_column(self):
        try:
            b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id', date_col='date')
            data = b.get_all_data(table_name_json, convert_datetime=True)
            self.assertTrue(data == [(1, '2021-05-18 11:19:00', None, 1, 4, 21, 0.0, 0.0, 0.0), 
                                     (2, '2021-05-18 11:19:10', None, 2, 1, 7, 0.0, 0.0, 0.0), 
                                     (3, '2021-05-18 11:19:20', None, 3, 3, -2, 0.0, 0.0, 0.0), 
                                     (4, '2021-05-18 11:19:30', None, 4, 7, 11, 0.0, 0.0, 0.0), 
                                     (5, '2021-05-18 11:19:40', None, 5, 1, 21, 0.0, 0.0, 0.0), 
                                     (6, '2021-05-18 11:19:50', None, 6, 3, 4, 0.0, 0.0, 0.0),
                                     (7, '2021-05-18 11:19:55', None, 7, 4, 11, 0.0, 0.0, 0.0)])

        except Exception as e:
            self.assertFalse(True)
        b.delete_table(table_name_json)

    def test_import_json_invalid_column_count(self):
        b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id')

        try:
            b.import_data_json('./test_files/json_invalid_column_count.json', table_name_json)
        except backend_errors.ColumnCountNotCorrectException:
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

        b.delete_table(table_name_json)

    def test_import_json_invalid_column_name(self):
        b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id')

        try:
            b.import_data_json('./test_files/json_invalid_column_name.json', table_name_json)
        except Exception as e:
            self.assertTrue(type(e) == backend_errors.InvalidColumnNameException)

        b.delete_table(table_name_json)

    def test_get_database_column_names(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json)

        try:
            col_names = b.get_database_column_names(table_name_json)
            self.assertTrue(col_names == ['id', 'date', 'classification', 'sensor1', 'sensor2', 'sensor3', 'PREDICTIONsensor1', 'PREDICTIONsensor2', 'PREDICTIONsensor3'])
        except:
            self.assertTrue(False)

        b.delete_table(table_name_json)

    def test_import_data_datetime(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json, date_col='date')

        try:
            data = b.get_all_data(table_name_json, convert_datetime=True)
            date = datetime.strptime(data[0][1], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(isinstance(date, datetime))
        except:
            self.assertTrue(False)
        b.delete_table(table_name_json)

    def test_get_tables(self):
        table_list = ["atable1", "atable2", "atable3", "atable4"]
        for table in table_list:
            database.create_table(b._curs, table, {
                'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
                'name':'VARCHAR(255)',
                'age':'INT(6)'
            })

        try:
            tables = b.get_tables()
            self.assertTrue([tables[0], tables[1], tables[2], tables[3]], table_list)
        except:
            self.assertTrue(False)
              
        for table in table_list:
            database.drop_table(b._curs, table)
    
    def test_get_all_data(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json, date_col='date')
        try:
            data = b.get_all_data(table_name_json, convert_datetime=True)
            self.assertTrue(data == [(1, '2021-05-18 11:19:00', None, 1, 4, 21, 0.0, 0.0, 0.0), 
                                     (2, '2021-05-18 11:19:10', None, 2, 1, 7, 0.0, 0.0, 0.0), 
                                     (3, '2021-05-18 11:19:20', None, 3, 3, -2, 0.0, 0.0, 0.0), 
                                     (4, '2021-05-18 11:19:30', None, 4, 7, 11, 0.0, 0.0, 0.0), 
                                     (5, '2021-05-18 11:19:40', None, 5, 1, 21, 0.0, 0.0, 0.0), 
                                     (6, '2021-05-18 11:19:50', None, 6, 3, 4, 0.0, 0.0, 0.0), 
                                     (7, '2021-05-18 11:19:55', None, 7, 4, 11, 0.0, 0.0, 0.0)])
        except:
            self.assertTrue(False)
        b.delete_table(table_name_json)
    
    # def test_kp_set_table(self):
    #     database.create_table(b._curs, table_name_json, {
    #         'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
    #         'name':'VARCHAR(255)',
    #         'age':'INT(6)'
    #     })
    #     test_inputs = [("fel_namn_1", True), 
    #                    (table_name_json, False), 
    #                    ("fel_namn_2", True),
    #                    ("tãble", True),
    #                    (None, True),
    #                    ("ö▲ü!", True)]
    #     for item in test_inputs :
    #         try :
    #             b.get_tables()
    #             b.set_current_table(item[0])
    #         except:
    #             self.assertTrue(item[1])
    #     b.delete_table(table_name_json)

    # def test_kp_get_data_points(self):
    #     database.create_table(b._curs, table_name_json, {
    #         'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
    #         'name':'VARCHAR(255)',
    #         'age':'INT(6)'
    #     })
    #     test_inputs = [(table_name_json, True, False),
    #                    ("", False, True), 
    #                    (None, False, True)]
    #     for item in test_inputs :
    #         try :
    #             b._get_all_non_classified(item[0])
    #             self.assertTrue(item[1])
    #         except : 
    #             self.assertTrue(item[2])
    #     b.delete_table(table_name_json)

    # def test_kp_edit_data_points(self):
    #     database.create_table(b._curs, table_name_json, {
    #         'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
    #         'name':'VARCHAR(255)',
    #         'age':'INT(6)'
    #     })
    #     b.set_current_table(table_name_json)
    #     test_inputs = [("e 1 true", False),
    #                    ("e 9 true", True),
    #                    ("p 1 false", True),
    #                    ("p 9 true", True),
    #                    ("r 7", False)]
    #     for item in test_inputs :
    #         edit_args = item[0].split(" ")
    #         if edit_args[0] == "e" :
    #             classification = False
    #             if edit_args[2] == "true" or edit_args[2] == "t" or edit_args[2] == "1" :
    #                 classification = True
    #             elif edit_args[2] == "false" or edit_args[2] == "f" or edit_args[2] == "0" :
    #                 classification = False
    #             else :
    #                 break
    #             try :
    #                 b._insert_classifications(int(edit_args[1]), classification)
    #             except :
    #                 self.assertTrue(item[1])
    #         elif edit_args[0] == "r" :
    #             try :
    #                 b._delete_data_point(int(edit_args[1]))
    #             except :
    #                 self.assertTrue(item[1])
    #     b.reset_current_table()
    #     b.delete_table(table_name_json)

    # TODO: Test cases to create
    def test_column_length_differ(self):
        try:
            b.import_data_json("./test_files/test_json_file_column_lengths_differ.json", table_name_json)
        except backend_errors.ColumnLengthsDifferException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_column_types_not_same(self):
        try:
            b.import_data_json("./test_files/test_json_file_column_types_differ.json", table_name_json)
        except backend_errors.ColumnTypesNotSameException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_column_types_not_matching(self):
        b.import_data_json("./test_files/base_json_file_id.json", 'random_json_table_name_please_work')
        try:
            b.import_data_json("./test_files/test_json_file_column_types_not_matching.json", 'random_json_table_name_please_work')
        except backend_errors.ColumnTypesNotMatchingException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)
        b.delete_table('random_json_table_name_please_work')

    def test_anomaly_alert(self):
        self.assertTrue(True)

    def test_insert_classification(self):
        self.assertTrue(True)

    def test_delete_data_point(self):
        self.assertTrue(True)

    def test_get_all_non_classified(self):
        b.delete_table('random_json_table_name_please_work3')
        b.import_data_json("./test_files/test_json_file_with_non_classified.json", 'random_json_table_name_please_work3', date_col='date')
        try:
            data = b._get_all_non_classified('random_json_table_name_please_work3', convert_datetime=True)
            self.assertTrue(data==[(3, '2021-01-22 00:00:02', None, 21, 32, 22, 0.0, 0.0, 0.0)])
        except Exception as e:
            self.assertTrue(False)
    
    def test_get_anomalies(self):
        self.assertTrue(True)
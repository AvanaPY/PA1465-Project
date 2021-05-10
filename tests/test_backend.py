import backend
import unittest
import database
import backend.errors as backend_errors
from datetime import datetime

b = backend.BackendBase()
table_name_json = 'test_table_json'
table_name_csv  = 'test_table_csv'

try:
    database.drop_table(b._curs, table_name_json)
except:
    pass

try:
    database.drop_table(b._curs, table_name_csv)
except:
    pass

class BackendUnitTest(unittest.TestCase):
    def test_import_json(self):
        try:
            b.import_data_json('./test_files/base_json_file.json', table_name_json)
            b.import_data_json('./test_files/new_json_file.json', table_name_json)


            database.drop_table(b._curs, table_name_json)
        except Exception as e:
            self.assertFalse(True)

    def test_import_csv(self):
        try:
            b.import_data_csv('./test_files/base_csv_file.csv', table_name_csv)
            b.import_data_csv('./test_files/new_csv_file.csv', table_name_csv)

            database.drop_table(b._curs, table_name_csv)
        except Exception as e:
            self.assertFalse(True)

    def test_import_json_w_id_column(self):
        try:
            b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id', date_col='date')
            data = b.get_all_data(table_name_json, convert_datetime=True)
            self.assertTrue(data == [(1, '2021-01-20 00:00:00', 21, 22, 23, 0, 0.0), (2, '2021-01-21 00:00:00', 22, 32, 32, 0, 0.0)])

            database.drop_table(b._curs, table_name_json)
        except Exception as e:
            self.assertFalse(True)

    def test_import_json_invalid_column_count(self):
        b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id')

        try:
            b.import_data_json('./test_files/json_invalid_column_count.json', table_name_json)
        except backend_errors.ColumnCountNotCorrectException:
            self.assertTrue(True)
        except Exception as e:
            self.assertTrue(False)

        database.drop_table(b._curs, table_name_json)

    def test_import_json_invalid_column_name(self):
        b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id')

        try:
            b.import_data_json('./test_files/json_invalid_column_name.json', table_name_json)
        except Exception as e:
            self.assertTrue(type(e) == backend_errors.InvalidColumnNameException)

        database.drop_table(b._curs, table_name_json)

    def test_get_database_column_names(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json)

        try:
            col_names = b.get_database_column_names(table_name_json)
            self.assertTrue(col_names == ['id', 'date', 'sensor1', 'sensor2', 'sensor3', 'classification', 'prediction'])
        except:
            self.assertTrue(False)

        database.drop_table(b._curs, table_name_json)

    def test_import_data_datetime(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json, date_col='date')

        try:
            data = b.get_all_data(table_name_json, convert_datetime=True)
            date = datetime.strptime(data[0][1], "%Y-%m-%d %H:%M:%S")
            self.assertTrue(isinstance(date, datetime))
        except:
            self.assertTrue(False)

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
    
    def test_set_reset_current_table(self):
        table_list = ["atable1", "atable2", "atable3", "atable4"]
        for table in table_list:
            database.create_table(b._curs, table, {
                'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
                'name':'VARCHAR(255)',
                'age':'INT(6)'
            })

        try:
            b.set_current_table("atable2")
            self.assertTrue(b._current_table == "atable2")

            b.set_current_table("atable1")
            self.assertTrue(b._current_table == "atable1")

            b.set_current_table("atable3")
            self.assertTrue(b._current_table == "atable3")

            b.set_current_table("atable4")
            self.assertTrue(b._current_table == "atable4")
            
            table = b.get_current_table()
            self.assertTrue(table == "atable4")

            b.reset_current_table()
            self.assertTrue(b._current_table == None)

        except:
            self.assertTrue(False)
              
        for table in table_list:
            database.drop_table(b._curs, table)
    
    def test_get_all_data(self):
        b.import_data_json("./test_files/base_json_file_id.json", table_name_json, date_col='date')
        try:
            data = b.get_all_data(table_name_json, convert_datetime=True)
            self.assertTrue(data == [(1, '2021-01-20 00:00:00', 21, 22, 23, 0, 0.0), (2, '2021-01-21 00:00:00', 22, 32, 32, 0, 0.0)])
        except:
            self.assertTrue(False)
        database.drop_table(b._curs, table_name_json)
    
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
    #     database.drop_table(b._curs, table_name_json)

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
    #     database.drop_table(b._curs, table_name_json)

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
    #     database.drop_table(b._curs, table_name_json)

    # TODO: Test cases to create
    def test_column_length_differ(self):
        try:
            b.import_data_json("./test_files/test_json_file_column_lengths_differ.json", table_name_json)
            database.drop_table(b._curs, table_name_json)
        except backend_errors.ColumnLengthsDifferException:
            self.assertTrue(True)
        except:
            self.assertTrue(False)

    def test_column_types_not_same(self):
        self.assertTrue(True)

    def test_column_types_not_matching(self):
        self.assertTrue(True)

    def test_anomaly_alert(self):
        self.assertTrue(True)

    def test_insert_classification(self):
        self.assertTrue(True)

    def test_delete_data_point(self):
        self.assertTrue(True)

    def test_get_all_non_classified(self):
        self.assertTrue(True)
    
    def test_get_anomalies(self):
        self.assertTrue(True)
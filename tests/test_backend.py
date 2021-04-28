import backend
import unittest
import database
import backend.errors as backend_errors

b = backend.BackendBase()
table_name_json = 'test_table_json'
table_name_csv  = 'test_table_csv'

try:
    database.drop_table(b._curs, table_name_json)
    print(f'Dropped table {table_name_json}')
except:
    pass

try:
    database.drop_table(b._curs, table_name_csv)
    print(f'Dropped table {table_name_csv}')
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
            b.import_data_json('./test_files/base_json_file_id.json', table_name_json, id_colum_name='id')
            data = database.get_data(b._curs, table_name_json)
            self.assertTrue(data == [(1, '2021-01-20', 21, 22, 23), (2, '2021-01-21', 22, 32, 32)])

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
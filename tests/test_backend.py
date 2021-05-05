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
            self.assertTrue(data == [(1, '2021-01-20', 21, 22, 23, 0), (2, '2021-01-21', 22, 32, 32, 0)])

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

    def test_kp_set_table(self) :
        test_inputs = [("fel_namn_1", True), 
                       ("atable", False), 
                       ("fel_namn_2", True),
                       ("tãble", True),
                       (None, True),
                       ("ö▲ü!", True)]
        for item in test_inputs :
            try :
                b.get_tables()
                b.set_current_table(item[0])
            except:
                self.assertTrue(item[1])

    def test_kp_get_data_points(self) :
        test_inputs = [("atable", True, False),
                       ("", False, True), 
                       (None, False, True)]
        for item in test_inputs :
            try :
                b._get_all_non_classified(item[0])
                self.assertTrue(item[1])
            except : 
                self.assertTrue(item[2])

    def test_kp_edit_data_points(self) :
        b.set_current_table("atable")
        test_inputs = [("e 1 true", False),
                       ("e 9 true", True),
                       ("p 1 false", True),
                       ("p 9 true", True),
                       ("r 7", False)]
        for item in test_inputs :
            edit_args = item[0].split(" ")
            if edit_args[0] == "e" :
                classification = False
                if edit_args[2] == "true" or edit_args[2] == "t" or edit_args[2] == "1" :
                    classification = True
                elif edit_args[2] == "false" or edit_args[2] == "f" or edit_args[2] == "0" :
                    classification = False
                else :
                    break
                try :
                    b._insert_classifications(int(edit_args[1]), classification)
                except :
                    self.assertTrue(item[1])
            elif edit_args[0] == "r" :
                try :
                    b._delete_data_point(int(edit_args[1]))
                except :
                    self.assertTrue(item[1])
        b.reset_current_table()

    def test_kp_get_table(self) :
        print(b.get_current_table())
        test_inputs = [None, "atable", "temptbl"]
        for item in test_inputs :
            try: 
                b.set_current_table(item)
            except:
                pass
            result = b.get_current_table()
            try :
                print(f"{result} == {item}")
                if (result != item) :
                    raise backend_errors.TableDoesNotExistException(item)
            except :
                self.assertFalse(True)
        b.reset_current_table()
try:
    from ..database import *
except:
    from database import *
import unittest

my_db, _ = create_sql_connection()
curs = my_db.cursor()

try:
    drop_table(curs, 'testing_table')
except Exception as e:
    pass
    #print(f'Could not drop table: {e}')

class DatabaseUnitTest(unittest.TestCase):
    def test_create_drop_table(self):
        create_table(curs, 'testing_table', {
            'id': 'INT(6) PRIMARY KEY AUTO_INCREMENT',
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        drop_table(curs, 'testing_table')
    def test_create_insert_4_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        insert_data(curs, 'testing_table', {
            'name':'samuel',
            'age':1
        })
        insert_data(curs, 'testing_table', {
            'name':'jonathan',
            'age':69
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':20
        })
        drop_table(curs, 'testing_table')
    def test_create_insert_edit_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        edit_data(curs, 'testing_table', {
            'name':'samuel',
            'age':1
        }, {
            'name':'emil'
        })
        data = get_data(curs, 'testing_table', {
            'name':'samuel'
        })
        self.assertEqual(data, [('samuel', 1)])
        drop_table(curs, 'testing_table')
    def test_create_insert_edit_get_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        edit_data(curs, 'testing_table', {
            'name':'samuel',
            'age':1
        }, {
            'name':'emil'
        })
        data = get_data(curs, 'testing_table', {
            'name':'emil'
        })
        self.assertNotEqual(data, [('emil', 4)])
        drop_table(curs, 'testing_table')
    def test_create_insert_delete_get_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        insert_data(curs, 'testing_table', {
            'name':'samuel',
            'age':20
        })
        delete_data(curs, 'testing_table',{
            'name':'emil'
        })
        data = get_data(curs, 'testing_table')
        self.assertNotEqual(data, [('samuel', 20), ('emil', 4)])
        self.assertEqual(data, [('samuel', 20)])
        drop_table(curs, 'testing_table')
    def test_create_insert_with_none_get_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':None
        })
        data = get_data(curs, 'testing_table')
        self.assertEqual(data, [('emil', None)])
        drop_table(curs, 'testing_table')
    def test_create_insert_with_null_get_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
        })
        data = get_data(curs, 'testing_table')
        self.assertEqual(data, [('emil', None)])
        drop_table(curs, 'testing_table')
    def test_create_insert_order_by_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'testing_table', order_by=['age'])
        drop_table(curs, 'testing_table')
    def test_create_insert_limit_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'testing_table', limit_row_count=2)
        self.assertTrue(len(data) <= 2)
        drop_table(curs, 'testing_table')
    def test_create_insert_limit_drop2(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'testing_table', limit_row_count=2)
        self.assertFalse(len(data) > 2)
        drop_table(curs, 'testing_table')
    def test_create_insert_limit_order_by_drop3(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'testing_table', order_by=['age'], limit_row_count=2)
        self.assertTrue(data == [('emil', 4), ('emil', 43)])
        drop_table(curs, 'testing_table')  
    def test_create_insert_offset_limit_order_by_drop(self):
        create_table(curs, 'testing_table', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'testing_table', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'testing_table', order_by=['age'], limit_offset=1, limit_row_count=2)
        self.assertTrue(data == [('emil', 43), ('emil', 72)])
        drop_table(curs, 'testing_table')
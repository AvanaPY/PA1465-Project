try:
    from ..database import *
except:
    from database import *
import unittest

my_db, _ = create_sql_connection()
curs = my_db.cursor()

class DatabaseUnitTest(unittest.TestCase):
    def test_create_drop_table(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        drop_table(curs, 'customers')
    def test_create_insert_4_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':4
        })
        insert_data(curs, 'customers', {
            'name':'samuel',
            'age':1
        })
        insert_data(curs, 'customers', {
            'name':'jonathan',
            'age':69
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':20
        })
        drop_table(curs, 'customers')
    def test_create_insert_edit_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':4
        })
        edit_data(curs, 'customers', {
            'name':'samuel',
            'age':1
        }, {
            'name':'emil'
        })
        data = get_data(curs, 'customers', {
            'name':'samuel'
        })
        self.assertEqual(data, [('samuel', 1)])
        drop_table(curs, 'customers')
    def test_create_insert_edit_get_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':4
        })
        edit_data(curs, 'customers', {
            'name':'samuel',
            'age':1
        }, {
            'name':'emil'
        })
        data = get_data(curs, 'customers', {
            'name':'emil'
        })
        self.assertNotEqual(data, [('emil', 4)])
        drop_table(curs, 'customers')
    def test_create_insert_delete_get_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':4
        })
        insert_data(curs, 'customers', {
            'name':'samuel',
            'age':20
        })
        delete_data(curs, 'customers',{
            'name':'emil'
        })
        data = get_data(curs, 'customers')
        self.assertNotEqual(data, [('samuel', 20), ('emil', 4)])
        self.assertEqual(data, [('samuel', 20)])
        drop_table(curs, 'customers')
    def test_create_insert_with_none_get_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
            'age':None
        })
        data = get_data(curs, 'customers')
        self.assertEqual(data, [('emil', None)])
        drop_table(curs, 'customers')
    def test_create_insert_with_null_get_drop(self):
        create_table(curs, 'customers', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'customers', {
            'name':'emil',
        })
        data = get_data(curs, 'customers')
        self.assertEqual(data, [('emil', None)])
        drop_table(curs, 'customers')
    def test_create_insert_order_by_drop(self):
        create_table(curs, 'test_insert_order_by_drop', {
            'name':'VARCHAR(255)',
            'age':'INT(6)'
        })
        insert_data(curs, 'test_insert_order_by_drop', {
            'name':'emil',
            'age':72
        })
        insert_data(curs, 'test_insert_order_by_drop', {
            'name':'emil',
            'age':43
        })
        insert_data(curs, 'test_insert_order_by_drop', {
            'name':'emil',
            'age':98
        })
        insert_data(curs, 'test_insert_order_by_drop', {
            'name':'emil',
            'age':4
        })
        data = get_data(curs, 'test_insert_order_by_drop', order_by=['age'])
        drop_table(curs, 'test_insert_order_by_drop')
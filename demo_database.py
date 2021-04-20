from database import *

my_db, config = create_sql_connection()
cursor = my_db.cursor()

table_name = 'mtable'
try:
    drop_table(cursor, table_name)
except:
    pass

def my_help_function(data):
    insert_data(cursor, table_name, data)
    data = get_data(cursor, table_name)
    print(data)
    
create_table(cursor, table_name, {
    'id':'INT NOT NULL PRIMARY KEY AUTO_INCREMENT',
    'name':'VARCHAR(255) NOT NULL',
    'age':'INT NOT NULL'
})
data = get_data(cursor, table_name)
print(data)

my_help_function({
    'name':'Emil',
    'age':20
})

my_help_function({
    'name':'Samuel',
    'age':21
})

my_help_function({
    'name':'Gustaf',
    'age':11
})

my_help_function({
    'name':'Per',
    'age':60
})

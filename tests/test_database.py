try:
    from ..database import *
except:
    from database import *

def test_database():
    try:
        my_db, _ = create_sql_connection()
        curs = my_db.cursor()

        try:
            drop_table(curs, 'customers')
        except Exception as e:
            print('Could not drop table: ', str(e))

        create_table(curs, 'customers', {
            "name": "VARCHAR(255)",
            'age':"INTEGER(6)"
        })

        insert_data(curs, 'customers',{
            'name':'emil',
            'age':20
        })

        delete_data(curs, 'customers', {
            'name':'emil',
            'age':20
        })
        
        insert_data(curs, 'customers',{
            'name':'jonathan',
            'age':69
        })
        
        insert_data(curs, 'customers',{
            'name':'emil',
            'age':420
        })

        insert_data(curs, 'customers', {
            'name':'alex',
            'age':20
        })

        edit_data(curs, 'customers', {'name':'samuel','age':420}, {'name':'emil'})

        data = get_data(curs, 'customers', {'name':'samuel'})
        print(data)
        print(f'Succesfully connected to database')
    except Exception as e:
        print(str(e))
        raise
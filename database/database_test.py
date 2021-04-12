try:
    from .database import *
except:
    from database import *

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
    
    insert_data(curs, 'customers',{
        'name':'jonathan',
        'age':69
    })
    
    insert_data(curs, 'customers',{
        'name':'emil',
        'age':None
    })
    insert_data(curs, 'customers', {
        'name':'alex',
        'age':20
    })

    delete_data(curs, 'customers', {
        'name':'emil',
        'age':20
    })

    data = get_data(curs, 'customers', {
        'name':'emil'
    })

    print(data)

    print(f'Succesfully connected to database')
except Exception as e:
    print(str(e))
    raise
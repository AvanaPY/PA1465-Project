try:
    from .database import *
except:
    from database import *

try:
    my_db, _ = create_sql_connection()
    curs = my_db.cursor()

    drop_table(curs, 'customers')
    create_table(curs, 'customers', {
        "name": "VARCHAR(255)",
    })

    print(f'Succesfully connected to database')
except Exception as e:
    print(str(e))
    raise
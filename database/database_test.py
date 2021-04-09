try:
    from .database import *
except:
    from database import *

try:
    my_db, _ = create_sql_connection()
    curs = my_db.cursor()

    create_table(curs, 'table')



    print(f'Succesfully connected to database')
except Exception as e:
    print(str(e))
    raise
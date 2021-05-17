from pandas.core.indexing import convert_to_index_sliceable
from cogitel_flask_app import init_app

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app')

if __name__ == '__main__':
    #app._backend.delete_table('atable')
    #app.run()
    # Either or
    #backend_app.console_program(args.ip, args.port)
    
    #app._backend.import_data_json('./test_files/base_json_file_id.json', 'atable')
    #app._backend.train_ai('atable')
    app._backend.import_data_json('./t.json', 'atable')
    preds, clas = app._backend.classify_datapoints('atable', [(32, 32, 32), (11, 11, 11), (100, -100, -100)])
    print(preds)
    print(clas)

    # data = app._backend.get_all_data('atable', convert_datetime=True)
    # cols = app._backend.get_database_column_names('atable')

    # print(cols)
    # for d in data:
    #     print(d)

    # app._backend.edit_classification('atable', 1, 1)
    
    # data = app._backend.get_all_data('atable', convert_datetime=True)
    # print(data)

    # import numpy as np
    # import json
    # n = 10_000
    # print(f'Creating data....')
    # data = {
    #     'date': ["2021-01-20"] * n,
    #     'sensor1': np.random.normal(loc=50, scale=5, size=n).astype(float).tolist(),
    #     'sensor2': np.random.normal(loc=50, scale=5, size=n).astype(float).tolist(),
    #     'sensor3': np.random.normal(loc=50, scale=5, size=n).astype(float).tolist(),
    # }
    # with open('t.json', 'w') as f:
    #     json.dump(data, f)
    
    # print(f'Importing')
    # app._backend.import_data_json('./t.json', 'atable')
    # app._backend.train_ai('atable')
    # data = app._backend.get_all_data('atable', convert_datetime=True)


    # preds, clas = app._backend.classify_datapoints('atable', [(32, 32, 32), (11, 11, 11), (1000, -100, -100)])
    # print(preds)
    # print(clas)

    # data = app._backend.get_all_data('atable', convert_datetime=True)
    # cols = app._backend.get_database_column_names('atable')

    # print(cols)
    # for d in data:
    #     print(d)
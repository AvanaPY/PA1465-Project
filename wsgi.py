from logging import fatal
from create_data import create
from cogitel_flask_app import init_app, App

from configparser import ConfigParser

import json

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app', load_ai=True)

if __name__ == '__main__':
    #create('t2.json', n=10000)
    
    #app._backend.delete_table('atable')
    # app._backend.import_data_json('./t2.json', 'atable', max_values=10000, classify_if_not_exist=True)
    #app._backend.import_data_json('./t2.json', 'atable', max_values=10000, classify_if_not_exist=True)
    #app._backend.train_ai('atable', label_columns=['sensor1', 'sensor2', 'sensor3'], 
    #                        save_ai=True, input_width=3, max_epochs=100, patience=10)

    #app._backend.import_data_json('t3.json', 'atable', classify_if_not_exist=True)
    #app._backend.train_ai('atable', app._backend.get_sensor_column_names('atable'), save_ai=True, max_epochs=100, patience=5, input_width=5, label_width=1)
    
    tabs = app._backend.get_tables()
    print(tabs)
    app.run(debug=True)
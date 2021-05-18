from create_data import create
from cogitel_flask_app import init_app, App

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app')

if __name__ == '__main__':

    # create('t.json', n=1000)
        
    # app._backend.delete_table('atable')
    # app._backend.import_data_json('./t.json', 'atable', max_values=1000, classify_if_not_exist=False)
    # app._backend.train_ai('atable', label_columns=app._backend.get_sensor_column_names('atable'), save_ai=True, max_epochs=100, patience=10)
    
    # create('t2.json', n=1000)
    
    app._backend.delete_table('atable')
    # app._backend.import_data_json('./t2.json', 'atable', max_values=1000, classify_if_not_exist=True)
    
    app.run(debug=True)
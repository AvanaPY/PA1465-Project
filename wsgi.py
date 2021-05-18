from pandas.core.indexing import convert_to_index_sliceable
from cogitel_flask_app import init_app, App

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app')
n = 10_000

if __name__ == '__main__':

    import numpy as np
    import json
    xs = np.linspace(-np.pi, np.pi, n)
    data = {
        'date': ["2021-01-20"] * n,
        'sensor1': [np.float32(i).item() + np.random.normal(loc=0, scale=0.01) for i in (np.sin(xs) + np.pi/4)],
        'sensor2': [np.float32(i).item() + np.random.normal(loc=0, scale=0.01) for i in (np.sin(xs) + np.pi/2)],
        'sensor3': [np.float32(i).item() + np.random.normal(loc=0, scale=0.01) for i in (np.sin(xs) - np.pi/4)],
    }
    with open('t.json', 'w') as f:
        json.dump(data, f)
        
    app._backend.delete_table('atable')
    app._backend.import_data_json('./t.json', 'atable', max_values=n)
    #app._backend.train_ai('atable', save_ai=True, max_epochs=100, patience=5)
    
    app.run()
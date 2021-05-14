from cogitel_flask_app import init_app

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app')

if __name__ == '__main__':
    app._backend.delete_table('atable')
    app.run()
    # Either or
    #backend_app.console_program(args.ip, args.port)
    
    #app._backend.import_data_json('./test_files/base_json_file_id.json', 'atable')
    # data = {
    #     'date': ["2021-01-20"] * 10_000,
    #     'sensor1': np.random.normal(loc=50, scale=5, size=10_000).astype(float).tolist(),
    #     'sensor2': np.random.normal(loc=50, scale=5, size=10_000).astype(float).tolist(),
    #     'sensor3': np.random.normal(loc=50, scale=5, size=10_000).astype(float).tolist(),
    # }
    # with open('t.json', 'w') as f:
    #     json.dump(data, f)
    
    # app._backend.import_data_json('./t.json', 'atable')
    # data = app._backend.get_all_data('atable', convert_datetime=True)
    # print(data)

    #app._backend.train_ai('atable')
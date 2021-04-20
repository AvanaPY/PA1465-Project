import argparse
from backend import create_app, import_data_csv, import_data_json

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--ip', type=str, required=True,
                help='The ip to run the Flask server on')
parser.add_argument('--port', type=int, required=True,
                help='The port to run the Flask server on')
args = parser.parse_args()

if __name__ == '__main__':
    app = create_app(args.ip, args.port)
    import_data_csv("test_files/bla.csv")
    #import_data_json("test_files/bla.json")
    app.run()
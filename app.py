import argparse
from backend import create_app
from backend import backend_app

# parser = argparse.ArgumentParser(description='Process some integers.')
# parser.add_argument('--ip', type=str, required=True,
#                 help='The ip to run the Flask server on')
# parser.add_argument('--port', type=int, required=True,
#                 help='The port to run the Flask server on')
# args = parser.parse_args()

from configparser import ConfigParser

parser = ConfigParser()
parser.read('./config.ini')

if __name__ == '__main__':
    app = create_app(confparser=parser, section='app')
    app.run()
    # Either or
    #backend_app.console_program(args.ip, args.port)
    
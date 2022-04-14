from logging import fatal
from create_data import create
from cogitel_flask_app import init_app, App

import os
import json

import json

from configparser import ConfigParser
parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app', load_ai=False)

if __name__ == '__main__':
    debug = os.environ.get('FLASK_APP_DEBUG', False)
    app.run(debug=debug)
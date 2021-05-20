from logging import fatal
from create_data import create
from cogitel_flask_app import init_app, App

from configparser import ConfigParser

import json

parser = ConfigParser()
parser.read('./config.ini')

app = init_app(confparser=parser, section='app', load_ai=False)

if __name__ == '__main__':
    create('t4.json', n=1000)
    app.run(debug=True)
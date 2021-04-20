import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import jsonify

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

def create_app(host, port):
    app = App(host=host, port=port)
    
    @app.route('/')
    def _home():
        return render_template("home.html")

    return app

class App(Flask):
    def __init__(self, host, port):
        super().__init__(__name__)
        self._host = host
        self._port = port
    
    def run(self):
        super().run(host=self._host, port=self._port)
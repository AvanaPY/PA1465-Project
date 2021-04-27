import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import jsonify
from flask import request
from .backend import BackendBase

import pandas.errors as pandas_errors
import backend.errors as backend_errors

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

def create_app(host, port):
    app = App(host=host, port=port)
    app.debug = True
    @app.route('/')
    def _home():
        return render_template("home.html")
    
    @app.route('/upload/dataset', methods=['POST'])
    def upload_dataset():
        ok = True

        body = request.files['file']
        filename = body.filename
        upload_dir_path = os.path.join(BASE_DIR, 'web/uploads')
        file_path = os.path.join(upload_dir_path, filename)
        if not os.path.exists(upload_dir_path):
            os.makedirs(upload_dir_path)
        with open(file_path, 'wb') as f:
            f.write(body.read())

        try:
            if filename.endswith('.json'):
                app._backend.import_data_json(file_path, 'atable')
            elif filename.endswith('.csv'):
                app._backend.import_data_csv(file_path, 'atable')
            else:
                raise Exception('Unknown extension bitch :tboof:')
        except Exception as e:
            status = 'error'
            message = str(e)
        else:
            status = 'ok'
            message = 'Dataset has been received'
        
        os.remove(file_path)

        return jsonify({
            "status": status,
            "message": message
            })

    return app

class App(Flask):
    def __init__(self, host, port):
        super().__init__(__name__)
        self._host = host
        self._port = port
        self._backend = BackendBase()

    def run(self):
        super().run(host=self._host, port=self._port)
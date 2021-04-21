import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import jsonify
from flask import request
from .backend import BackendBase

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
        try:
            body = request.files['file']
            filename = body.filename
            upload_dir_path = os.path.join(BASE_DIR, 'web/uploads')
            file_path = os.path.join(upload_dir_path, filename)
            
            if not os.path.exists(upload_dir_path):
                os.makedirs(upload_dir_path)
            
            with open(file_path, 'wb') as f:
                f.write(body.read())

            app._backend.import_data_csv(file_path, 'atable')

            os.remove(file_path)
        except Exception as e:
            print(e)

        return jsonify({
            "status": "ok",
            "message": "Dataset has been received"
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
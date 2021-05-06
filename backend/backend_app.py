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
                app._backend.import_data_json(file_path, 'atable2')
            elif filename.endswith('.csv'):
                app._backend.import_data_csv(file_path, 'atable2')
            else:
                raise Exception('Unknown extension bitch :tboof:')
        except Exception as e:
            status = 'error'
            message = str(e)
        else:
            status = 'ok'
            message = 'Dataset has been received'
        
        os.remove(file_path)

        #app._backend.helo()

        return jsonify({
            "status": status,
            "message": message
            })

    return app

def console_program(host, port):
    app = App(host=host, port=port)
    app.debug = True 
    run = True
    while (run) :
        print("What do you want to do?")
        print("1. Choose a device to manage.")
        print("2. Get device data points.")
        print("3. Edit device data point.")
        print("4. Show current device.")
        print("5. Show anomalies")
        print("6. Exit program.")
        menuDecision = int(input("Input number: "))
        if menuDecision == 1 :
            app._backend.get_tables()
            table_name = input("Input table name: ")
            try:
                app._backend.set_current_table(table_name)
            except backend_errors.TableDoesNotExistException :
                print("The table you selected was not found. Try again.")
        elif menuDecision == 2 :
            data_points = app._backend._get_all_non_classified()
            i = 1
            for item in data_points :
                print(f"{i}. {item}")
                i += 1
        elif menuDecision == 3 :
            print("Select data point to edit.")
            print("To edit classification: e {id} {true/false}")
            print("To remove: r {id}")
            edit_command = input("Input: ")
            edit_args = edit_command.split(" ")
            if edit_args[0] == "e" :
                classification = False
                if edit_args[2] == "true" or edit_args[2] == "t" or edit_args[2] == "1" :
                    classification = True
                elif edit_args[2] == "false" or edit_args[2] == "f" or edit_args[2] == "0" :
                    classification = False
                else :
                    break
                app._backend._insert_classifications(int(edit_args[1]), classification)
            elif edit_args[0] == "r" :
                app._backend._delete_data_point(int(edit_args[1]))
        elif menuDecision == 4 :
            print(f"Current device: {app._backend.get_current_table()}")
        elif menuDecision == 5 :
            anomalies = app._backend._get_all_anomalies()
            if len(anomalies) == 0 :
                print("No anomlies found.")
            else :
                for anomaly in anomalies :
                    print(anomaly)
        elif menuDecision == 6 :
            exit = input("Exit? (y/n)")
            if (exit == "y") :
                run = False

class App(Flask):
    def __init__(self, host, port):
        super().__init__(__name__)
        self._host = host
        self._port = port
        self._backend = BackendBase()

    def run(self):
        super().run(host=self._host, port=self._port)
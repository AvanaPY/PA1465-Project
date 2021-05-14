from cogitel_flask_app import app

from flask import render_template, request, jsonify
import os

BASE_DIR = os.path.dirname(__file__)

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
            app._backend.import_data_json(file_path, 'atable', use_historical=False)
        elif filename.endswith('.csv'):
            app._backend.import_data_csv(file_path, 'atable', use_historical=False)
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
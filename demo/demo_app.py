import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import sys
import signal
import time

from demo_ai import get_ai_2 as get_ai, train_ai, load_ai, map

from flask import jsonify, request
from web.app import get_app
app = get_app()

from threading import Thread

BASE_DIR = os.path.dirname(__file__)
FILE_UPLOAD_ALLOWED_EXTENSION = 'csv' # Only allow .csv files for now

RETRAINING_MODEL_ACTIVE = False 

AI_MIN_OK = 22
AI_MAX_OK = 28
AI_LOC = 25
AI_SCL = 2.2

def exit_handler():
    print(f'Stopping server.')
    sys.exit()

AI_PRE_WEIGHTS_PATH = os.path.join(BASE_DIR, "ai_data/weights_prel.h5")
AI_ACT_WEIGHTS_PATH = os.path.join(BASE_DIR, "ai_data/weights.h5")

@app.route('/api/predict/<value>')
def api_predict(value):
    try:
        value = float(value)
        mapped = map(value, AI_MIN_OK, AI_MAX_OK, 0, 1)

        pred = ai_model.predict([[mapped]])[0]

        ok = pred[0] > pred[1]
        confidence = max(pred[0], pred[1])

        result = "ok" if ok else "not ok"
        return jsonify({ 
            "status": "ok", 
            "result": result, 
            "confidence": f'{(confidence * 100):2.0f}%'
        })

    except Exception as e:
        print(str(e))
        return jsonify({ "status": "error", "message": "Internal server error" })

@app.route('/api/retrain', methods=['POST'])
def api_retrain():
    print("Training AI")
    global RETRAINING_MODEL_ACTIVE
    if RETRAINING_MODEL_ACTIVE:
        return jsonify({"status": "error", "message": "The model is busy already retraining the model."})
    RETRAINING_MODEL_ACTIVE = True
    _train_ai()
    _save_ai(complete=True)
    RETRAINING_MODEL_ACTIVE = False
    return jsonify({"status": "ok", "message": "Retrained the model."})
    
@app.route('/upload/dataset', methods=['POST'])
def upload_dataset():
    body = request.files['file']
    with open(os.path.join(BASE_DIR, 'web/uploads/tmp.txt'), 'wb+') as f:
        f.write(body.read())

    return jsonify({
        "status": "ok",
        "message": "Dataset has been received"
    })

def _train_ai():
    global ai_model
    ai_model = get_ai()
    train_ai(ai_model, AI_MIN_OK, AI_MAX_OK, AI_LOC, AI_SCL, batch_size=32, epochs=25)

def _save_ai(complete=False):
    if complete:
        ai_model.save_weights(AI_ACT_WEIGHTS_PATH)
    else:
        ai_model.save_weights(AI_PRE_WEIGHTS_PATH)

ai_model = get_ai()
if os.path.exists(AI_ACT_WEIGHTS_PATH):
    print(f'Found previous weights, loading weights...')
    try:
        load_ai(ai_model, AI_ACT_WEIGHTS_PATH)
    except Exception as e:
        print(f'Exception "{e}" occured during loading of AI weights, exiting program.')
        exit()
else:
    print(f'Found no previous weights, retraining model...')
    try:
        _train_ai()
        _save_ai()
        print(f'Saved weights at "{AI_PRE_WEIGHTS_PATH}". Remember to rename to "{AI_ACT_WEIGHTS_PATH}" to load them for next start.')
    except KeyboardInterrupt:
        print('Received keyboard interrupt')
        exit_handler()
    except Exception as e:
        print(f'Unknown error "{e}" occured, exiting program.')
        exit()

server = Thread(target=app.run)
server.daemon = True
server.start()
while server.is_alive():
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        exit_handler()
    except:
        raise
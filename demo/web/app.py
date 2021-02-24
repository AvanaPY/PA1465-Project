import os
from flask import Flask
from flask import render_template
from flask import url_for
from flask import jsonify

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

def get_app():
    return app
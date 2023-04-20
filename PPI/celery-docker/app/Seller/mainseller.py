from flask import Flask, request, jsonify
from celery import Celery
from app.Seller.tasks import beginPSI, sign_blinds, send_ore

import os
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']



def make_celery(app=None):

    app = app or create_app()
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'],include='app.Seller.tasks')
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']

    return app


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/begin', methods=['GET', 'POST'])
def index():

    print("obtained request")
    try:
        data = request.get_json()
    except():
        data = None
    print("import success")
    beginPSI.delay()
    result = dict()
    result['result'] = 'success'
    result['data'] = data
    return jsonify(result)


@app.route('/blinded_set', methods=['GET', 'POST'])
def blinded_set():
    try:
        data = request.get_json()
    except():
        data = None
    sign_blinds.delay(data)
    return "Ok"


@app.route('/request_ore', methods=['POST'])
def req_ore():
    try:
        data = request.get_json()
    except():
        data = None
    send_ore.delay(data)
    return "Ok"

#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['SELLER_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

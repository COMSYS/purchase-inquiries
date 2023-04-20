from flask import Flask, request, jsonify
from celery import Celery
from app.ThirdParty.tasks import handle_buyer, handle_seller

import os
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']



def make_celery(app=None):

    app = app or create_app()
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'],include='app.ThirdParty.tasks')
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']

    return app


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/start_ore', methods=['GET', 'POST'])
def index():

    print("obtained request")
    try:
        data = request.get_json()
    except():
        data = None
    print("import success")
    handle_buyer.delay(data)
    result = dict()
    result['result'] = 'success'
    result['data'] = data
    return jsonify(result)


@app.route('/sender_input', methods=['GET', 'POST'])
def handler_sender_input():
    print("obtained request")
    try:
        data = request.get_json()
    except():
        data = None
    print("import success")
    handle_seller.delay(data)
    result = dict()
    result['result'] = 'success'
    result['data'] = data
    return jsonify(result)


#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['THIRDPARTY_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

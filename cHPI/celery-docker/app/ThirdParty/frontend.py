from flask import Flask, request, jsonify
from celery import Celery
from app.ThirdParty.tasks import store_seller_data, store_buyer_data
import json

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


@app.route('/seller_values', methods=['GET', 'POST'])
def store_seller_input():
    with open("test_seller.txt", 'w+') as f:
        f.write(request.get_json())
    store_seller_data.delay()
    return 'Ok'


@app.route('/buyer_values', methods=['GET', 'POST'])
def store_buyer_input():
    with open("test_buyer.txt", 'w+') as f:
        json.dump(json.loads(request.get_json()), f)
    store_buyer_data.delay()
    return 'Ok'

#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['THIRDPARTY_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

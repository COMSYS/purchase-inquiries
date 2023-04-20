from flask import Flask, request, jsonify
from celery import Celery
from app.Seller.tasks import beginPaillier, store_buyervalues, deblind_result
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


@app.route('/start_paillier', methods=['GET', 'POST'])
def start_paillier():
    data = request.get_json()
    beginPaillier.delay(data)
    return 'OK'


@app.route('/buyer_data', methods=['GET', 'POST'])
def store_buyer():
    data = request.get_json()
    store_buyervalues.delay(data)
    return 'Ok'


@app.route('/calculation_result', methods=['GET', 'POST'])
def remove_blinds():
    data = request.get_json()
    deblind_result.delay(data)
    return 'Ok'


#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['SELLER_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

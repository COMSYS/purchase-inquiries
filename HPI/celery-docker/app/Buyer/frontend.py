from flask import Flask, request, jsonify
from celery import Celery
from app.Buyer.tasks import distribute_encryption, evaluate_result
import simplejson as json
import os
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']



def make_celery(app=None):

    app = app or create_app()
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'],include='app.Buyer.tasks')
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']

    return app

@app.route('/encrypt', methods=['GET','POST'])
def encrypt():
    data = request.get_json()
    distribute_encryption.delay(data)
    return 'Ok'


@app.route('/final_result', methods=['GET', 'POST'])
def final_result():
    data = request.get_json()
    evaluate_result.delay(data)
    return 'Ok'


#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['BUYER_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

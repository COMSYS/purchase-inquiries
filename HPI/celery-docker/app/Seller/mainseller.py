from flask import Flask, request, jsonify
from celery import Celery
from app.Seller.tasks import  store_buyervalues
import simplejson as json
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





@app.route('/buyer_data', methods=['GET', 'POST'])
def store_buyer():
    with open("buyer_data.txt", 'w+') as f:
        json.dump(json.loads(request.get_json()), f)
    store_buyervalues.delay()
    return 'Ok'



#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['SELLER_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

from flask import Flask, request, jsonify
from celery import Celery
from app.Buyer.tasks import construct_blinds, checkcontainment
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


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/startClient', methods=['GET', 'POST'])
def index():

    print("obtained start request")
    try:
        data = request.get_json()
    except():
        data = None
    construct_blinds.delay(data)
    result = dict()
    result['result'] = 'success'
    result['data'] = data
    return jsonify(result)

@app.route('/signedblinds', methods=['GET', 'POST'])
def signedblinds():
    try:
        data = request.get_json()
    except:
        data = None

    checkcontainment.delay(data)
    return 'OK'


@app.route('/return_ore', methods=['GET', 'POST'])
def finalresult():
    try:
        data = request.get_json()
    except:
        data = None
    parsed = json.loads(data)
    if parsed['response'] == True:
        print("seller is viable")
    else:
        print("seller not viable")
    with open('finished.txt', 'w+'):
        pass
    return "Ok"


#app.config['CELERY_BROKER_URL'] = os.environ['CELERY_BROKER_URL']
port = os.environ['BUYER_FRONTEND_PORT']
#port = 800


make_celery(app)
app.run(host='0.0.0.0', port=port, debug=False)

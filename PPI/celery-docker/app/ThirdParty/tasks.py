import simplejson as json
import sys
from base64 import b64encode

import celery
import pickle
import os
import requests
from app.ORE.OrderRevealingEncryption.ore import ore_comp
from app.Evaluator import performancedecorator, post


def store_buyer(pricedict):
    try:
        os.remove("ThirdParty/buyerdata.pkl")
    except FileNotFoundError:
        pass
    a_file = open("ThirdParty/buyerdata.pkl", "wb")
    pickle.dump(pricedict, a_file)
    a_file.close()

def request_seller(ids):
    payload = dict()
    payload['ids'] = ids
    try:
        post('http://'+os.environ['SELLER_ADDRESS']+':'+os.environ['SELLER_FRONTEND_PORT']+'/request_ore', json=json.dumps(payload))
    except(requests.exceptions.ConnectionError):
        print("connection failed")


@celery.shared_task(name='handle_buyer')
@performancedecorator
def handle_buyer(data):
    if data is None:
        return
    try:
        parsed = json.loads(data)
    except():
        print("Unexpected error when parsing:", sys.exc_info()[0])
        raise

    # store buyers values
    store_buyer(parsed)

    # get list of ids
    ids = [*parsed.keys()]

    # request values from seller
    request_seller(ids)
    return


def send_final_response(answer):
    payload = dict()
    payload['response'] = answer
    try:
        post(
            'http://' + os.environ['BUYER_ADDRESS'] + ':' + os.environ['BUYER_FRONTEND_PORT'] + '/return_ore',
            json=json.dumps(payload))
    except requests.exceptions.ConnectionError:
        print("connection failed")


def load_buyer_data():
    try:
        a_file = open("ThirdParty/buyerdata.pkl", "rb")
        buyerdict = pickle.load(a_file)
    except:
        raise
    finally:
        a_file.close()
    return buyerdict


@celery.shared_task(name='handle_seller')
@performancedecorator
def handle_seller(data, testing=False):
    if data is None:
        # comparison failed
        send_final_response(False)
        return False
    # parse seller data
    try:
        sellerdict = json.loads(data)
    except():
        print("Unexpected error when parsing:", sys.exc_info()[0])
        raise
    # try to load buyer data
    buyerdict = load_buyer_data()

    # make sure both contain same keys
    if not (sellerdict.keys() == buyerdict.keys()):
        return False
    # compare key wise buyer should be smaller
    for k in buyerdict.keys():
        if ore_comp(buyerdict[k], sellerdict[k]) == -1:
            # buyer threshold is above seller
            send_final_response(False)
            return False

    send_final_response(True)
    if testing:
        return True
    else:
        return True

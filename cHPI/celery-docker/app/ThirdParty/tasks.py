import simplejson as json
import sys
from base64 import b64encode

from app.Evaluator import performancedecorator, post
from app.paillier.phe.paillier import EncryptedNumber, PaillierPublicKey
import celery
import pickle
import os
import requests
from app.create_values import testmode
from app.Testmode import Testmode as tm
from app import Testmode
import time


def store_list(itemlist, filename):
    with open(filename, 'w+') as f:
        for i in itemlist:
            f.write('%s\n' % i)


def store_single_val(item, filename):
    with open(filename, 'w+') as f:
        f.write('%s\n' % item)


def store(item, filename):
    if isinstance(item, list):
        store_list(item, filename)

    elif isinstance(item, int):
        store_single_val(item, filename)

    elif isinstance(item, bool):
        store_single_val(item, filename)


def load_bool(filename):
    try:
        with open(filename, 'r') as f:
            res = bool(f.readline()[:-1])
        return res
    except:
        return False


def load_pubkey(filename):
    try:
        with open(filename, 'r') as f:
            key = PaillierPublicKey(int(f.readline()[:-1]))
        return key
    except:
        return None


def load_encrypted_value_list(filename):
    try:
        res = []
        pubkey = load('pubkey')
        with open(filename, 'r') as f:
            for l in f:
                res.append(EncryptedNumber(pubkey, int(l[:-1])))
        return res
    except:
        return None


def load_number_list(filename):
    try:
        res = []
        with open(filename, 'r') as f:
            for l in f:
                res.append(int(l[:-1]))
        return res
    except:
        return None


def load(name):
    """
    Loads contents of specified file and parses it accordingly
    :param name: name of parameter
    :return:
    """
    if name == 'seller_completion':
        return load_bool('ThirdParty/seller_completion.txt')
    elif name == 'buyer_values':
        return load_encrypted_value_list('ThirdParty/buyer_vals.txt')

    elif name == 'pubkey':
        return load_pubkey('ThirdParty/pubkey.txt')
    elif name == 'seller_values':
        return load_number_list('ThirdParty/seller_vals.txt')


@celery.shared_task(name='store_seller_data')
@performancedecorator
def store_seller_data(data=None):
    """ obtain list blinded prices from seller
        v_i = r1*seller price + blind_i
    """

    # try parsing data
    try:
        with open("test_seller.txt", 'r') as f:
            parsed_list = json.load(f)['blinded_vals']
    except:
        print("Failed to parse")
    print("storing seller data")
    store(parsed_list, 'ThirdParty/seller_vals.txt')
    store(True, 'ThirdParty/seller_completion.txt')


def send_res_to_seller(result):
    data = dict()
    data['res'] = result
    try:

        response = post(
            'http://' + os.environ['SELLER_FRONTEND_ADDRESS'] + ':' + os.environ['SELLER_FRONTEND_PORT'] + '/calculation_result',
            json=json.dumps(data))

    except:
        print("Sending failed")


def start_calculation():
    """
    check if all values (buyer and seller values) are present
    start calculation of r1*[SellerPrices]*[BuyerConfig]
    :return:
    """
    # buyer values are present or else function would not have been called
    # check if seller values are available
    seller_completion = load('seller_completion')
    if seller_completion:
        # can load all values and start calculation

        # load encrypted buyer values
        buyer_vals = load('buyer_values')
        if buyer_vals is None:
            raise Exception
        # load seller_vals
        seller_vals = load('seller_values')
        if seller_vals is None:
            raise Exception

        # calculate result
        res = sum([v*u for v, u in zip(buyer_vals, seller_vals)])

        # return result to seller
        send_res_to_seller(res.ciphertext())
        return res
    else:
        # throw exception for now
        raise Exception


@celery.shared_task(name='store_buyer_data')
@performancedecorator
def store_buyer_data(data=None):
    """
    Obtain buyer data and store it. Start calculation.
    :param data: dict
            data['pubkey'] contains modulus n of public key
            data['encryptedVals'] contains list of ciphertexts of encrypted values
    :return:
    """

    # try parsing data
    try:
        with open("test_buyer.txt", encoding='utf-8') as f:
            parsed = json.load(f)
    except:
        print("Failed to parse")
        raise


    store(parsed['pubkey'], 'ThirdParty/pubkey.txt')
    store(parsed['encryptedVals'], 'ThirdParty/buyer_vals.txt')

    start_calculation()


import simplejson as json
from base64 import b64encode
import sys
import celery

from app.Testmode import Testmode
from app.create_values import getMaxNumItems
from app.paillier.phe.paillier import PaillierPublicKey, EncryptedNumber
from app.paillier.phe.encoding import EncodedNumber
import pickle
import os
from hashlib import sha256
import requests
import random
import time
from app.create_values import testmode
from app.Evaluator import performancedecorator, post
import time

from memory_profiler import profile

stop_threads = False



def load_products():
    productprices = []
    with open('Seller/prices.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            productprices.append(int(currentPlace))

    return productprices


def store_list(values, filename):
    with open(filename, 'w+') as filehandle:
        for listitem in values:
            filehandle.write('%s\n' % listitem)


def send(data, page, address, port):
    try:
        response = post(
            'http://' + os.environ[address] + ':' + os.environ[port] + page,
            json=json.dumps(data))
        return response
    except:
        print("Sending failed")
        raise


def send_randoms_to_buyer(randoms):
    data = dict()
    data['blinds'] = randoms

    response = send(data, '/encrypt', 'BUYER_FRONTEND_ADDRESS', 'BUYER_FRONTEND_PORT')


def send_blinded_vals_to_thirdparty(blinded_vals):
    data = dict()
    data['blinded_vals'] = blinded_vals
    response = send(data, '/seller_values', 'THIRDPARTY_FRONTEND_ADDRESS', 'THIRDPARTY_FRONTEND_PORT')



def send_res_to_buyer(res):
    data = dict()
    data['res'] = res

    response = send(data, '/final_result', 'BUYER_FRONTEND_ADDRESS', 'BUYER_FRONTEND_PORT')





@celery.shared_task(name='beginPaillier')
@performancedecorator
def beginPaillier(data):
    # create blinded set
    productprices = load_products()
    # create random blinds of size len

    max_num_items = len(productprices)
    randoms = [random.randrange(2**8,2**20) for i in range(max_num_items)]
    # store randoms
    store_list(randoms, 'Seller/randoms.txt')
    assert(len(randoms) == len(productprices))
    # random one
    r1 = random.randrange(2**8, 2**12)
    blinded_prices = [r1*p+ran for p, ran in zip(productprices, randoms)]
    store_list(blinded_prices, 'Seller/blindedprices.txt')
    store_list([r1], 'Seller/random1.txt')

    # send blinded vals to seller
    send_blinded_vals_to_thirdparty(blinded_prices)
    # send randoms to buyer
    send_randoms_to_buyer(randoms)


def store(data, filename):
    with open(filename, 'w+') as f:
        f.write('%s\n' % data)


def load_pubkey():
    try:
        with open('Seller/pubkey.txt', 'r') as f:
            pubkey = PaillierPublicKey(int(f.readline()[:-1]))
    except:
        pubkey = None
    return pubkey


def load_encryptedNumber(filename):
    pubkey = load_pubkey()
    if pubkey is None:
        return None
    try:
        with open(filename, 'r') as f:
            line = int(f.readline()[:-1])
            encNum = EncryptedNumber(pubkey, line)

    except:
        return None
    return encNum


def load_number(filename):
    try:
        with open(filename, 'r') as f:
            num = int(f.readline()[:-1])
            return num
    except:
        return None


@celery.shared_task(name='store_buyervalues')
@performancedecorator
def store_buyervalues(data):
    """ store threshold and sum of blinded encrypted buyer configuration
    """

    # parse the data
    try:
        parsed = json.loads(data)
    except:
        print("Parsing failed")

    # store encrypted threshold
    store(parsed['threshold'], 'Seller/threshold.txt')

    # store public key

    store(parsed['pubkey'], 'Seller/pubkey.txt')

    # store encrypted sum
    store(parsed['blind_enc_sum'], 'Seller/enc_sum.txt')


@celery.shared_task(name='deblind_result')
@performancedecorator
def deblind_result(data, testing=False):
    """ obtain result form thirdparty
    remove blinds """
    # parse result
    try:
        blinded_res = json.loads(data)['res']
    except:
        print("Parsing failed")


    # load r1
    r1 = load_number('Seller/random1.txt')

    # load threshold
    T = load_encryptedNumber('Seller/threshold.txt')

    # load pubkey
    pubkey = load_pubkey()

    # load encrypted sum
    enc_sum = load_encryptedNumber('Seller/enc_sum.txt')

    if r1 is None or T is None or pubkey is None or enc_sum is None:
        print("Failed to load stored data")
        return None
    # transform ciphertext to encrypted number
    enc_blinded_res = EncryptedNumber(pubkey, blinded_res)

    # remove (sum(ui*ri)) the sum of buyers values * randoms
    removed_blinds = enc_blinded_res -enc_sum

    res = removed_blinds - (r1*T) + pubkey.encrypt(random.randrange(1, r1-1))

    # send res to buyer
    send_res_to_buyer(res.ciphertext())
    return res



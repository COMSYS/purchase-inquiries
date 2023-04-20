import simplejson as json
from base64 import b64encode

import celery

from app.Testmode import Testmode

from app.paillier.phe.paillier import PaillierPublicKey, EncryptedNumber
from app.paillier.phe.encoding import EncodedNumber
import pickle
import os
from hashlib import sha256
import requests
import random
import time
from app.Evaluator import performancedecorator, post

def load_products():
    productprices = []
    with open('Seller/prices.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            productprices.append(int(currentPlace))

    return productprices

def load_blinded_prices():
    productprices = []
    with open('Seller/blinded_prices.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            productprices.append(int(currentPlace))
    return productprices

def load_random_num():
    with open('Seller/random1.txt', 'r') as f:
        num = int(f.readline()[:-1])
        return num

def store_list(values, filename):
    with open(filename, 'w+') as filehandle:
        for listitem in values:
            filehandle.write('%s\n' % listitem)


def send(data, page, address, port):

    try:
        post(
            'http://' + os.environ[address] + ':' + os.environ[port] + page,
            json=json.dumps(data))
    except:
        print("Sending failed")


def send_randoms_to_buyer(randoms):
    data = dict()
    data['blinds'] = randoms
    send(data, '/encrypt', 'BUYER_FRONTEND_ADDRESS', 'BUYER_FRONTEND_PORT')




def send_res_to_buyer(res):
    data = dict()
    data['res'] = res
    send(data, '/final_result', 'BUYER_FRONTEND_ADDRESS', 'BUYER_FRONTEND_PORT')







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


def calculate_result(buyer_ciphertexts, modulus, threshold_cipher, rand, blinded_prices):

    pubkey = PaillierPublicKey(modulus)
    buyer_enc = [EncryptedNumber(pubkey, c) for c in buyer_ciphertexts]
    threshold = EncryptedNumber(pubkey, threshold_cipher)
    mult = sum([v*u for v, u in zip(buyer_enc, blinded_prices)])
    r1 = rand
    r2 = random.randrange(1, r1-1)
    res = mult-(r1*threshold) + pubkey.encrypt(r2)
    # send res to buyer
    send_res_to_buyer(res.ciphertext())

    return res


@celery.shared_task(name='store_buyervalues')
@performancedecorator
def store_buyervalues():
    """
    create two random numbers
    calculate (r1(U*V)-(r1*T))+r2

    """
    # create blinded set
    productprices = load_products()
    r1 = random.randrange(2 ** 8, 2 ** 12)
    blinded_prices = [r1 * p for p in productprices]
    store_list(blinded_prices, 'Seller/blindedprices.txt')
    store_list([r1], 'Seller/random1.txt')
    # parse the data
    try:
        with open("buyer_data.txt", 'r') as f:
            parsed = json.load(f)
    except:
        print("Parsing failed")

    # store encrypted threshold
    store(parsed['threshold'], 'Seller/threshold.txt')

    # store public key

    store(parsed['pubkey'], 'Seller/pubkey.txt')

    # store encrypted sum
    store_list(parsed['ciphertexts'], 'Seller/buyer_ciphertexts.txt')

    # calc result
    res = calculate_result( parsed['ciphertexts'], parsed['pubkey'], parsed['threshold'], r1, blinded_prices)
    return res






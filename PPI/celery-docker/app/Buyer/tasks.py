import simplejson as json
from base64 import b64encode

import celery
import app.PyPSI.psi.protocol.rsa as rsa
from app.PyPSI.psi.datastructure import bloom_filter
from app.utils import DictX
from app.ORE.OrderRevealingEncryption.ore import ore_enc
from app.Evaluator import performancedecorator, post
import pickle
import os
from hashlib import sha256
from Crypto.PublicKey import RSA
import requests


def init_client(pubkey):
    global client
    client = rsa.Client(pubkey)
    return client


bf = bloom_filter.BloomFilter(1)
client = rsa.Client(None)



def store_bloom_filter(data):
    f = open('Buyer/bloom.pkl', 'wb')
    pickle.dump(data, f)
    f.close()

def load_bloom_data():
    f = open('Buyer/bloom.pkl', 'rb')
    data = pickle.load(f)
    f.close()
    return data


def reconstruct_bloom_filter(data):
    bits = bloom_filter.deserialize(data['bloomarray'])
    global bf
    bf = bloom_filter.BloomFilter(data['bloomcapacity'], data['bloomfpprob'], bits=bits, count=data['bloomcount'])
    return bf


def blind_input(input, client):

    random_factors = client.random_factors(len(input))
    a_file = open("Buyer/random_factors.pkl", "wb")
    pickle.dump(random_factors, a_file)
    a_file.close()

    # blind input with randoms
    blinded_input = client.blind_set(input, random_factors)
    return blinded_input, random_factors

def store_pubkey(data):
    with open('Buyer/pubkey.txt', 'w+') as f:
        f.write('%s\n' % str(data['pubkeyN']))
        f.write('%s\n' % str(data['pubkeyE']))

@celery.shared_task(name='construct_blinds')
@performancedecorator
def construct_blinds(data, testing=False):
    if data is None:
        raise Exception
    data = json.loads(data)
    # construct public key
    pubkey = DictX
    pubkey.n = data['pubkeyN']
    pubkey.e = data['pubkeyE']
    client = init_client(pubkey)

    # store public key
    store_pubkey(data)


    # reconstruct and store bloomfilter
    store_bloom_filter(data)

    # load client set
    input = []
    with open('Buyer/input.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            input.append(int(currentPlace))
    blinded_input, _ = blind_input(input, client)

    blinded_input_to_int = []
    for i in blinded_input:
        blinded_input_to_int.append(int(i))
    payload = dict()
    payload['blinded_set'] = blinded_input_to_int
    # return blinded set to server but first store it
    post('http://'+os.environ['SELLER_ADDRESS']+':'+os.environ['SELLER_FRONTEND_PORT']+'/blinded_set', json=json.dumps(payload))
    if testing:
        return payload, json.dumps(payload)
    else:
        return


def start_ore():
    # load thresholds
    try:
        a_file = open("Buyer/prices.pkl", "rb")
        buyerdict = pickle.load(a_file)
        a_file.close()
    except:
        raise
    finally:
        a_file.close()

    # encrypt thresholds
    enc = dict()
    for k in buyerdict:
        h_val = int(sha256((str(k) + str(client.public_key.e)).encode('utf-8')).hexdigest(), 16)

        enc[h_val] = ore_enc(bin(buyerdict[k])[2:], str(client.public_key.e))

    # send values to thirdparty
    post('http://'+os.environ['THIRDPARTY_ADDRESS']+':'+os.environ['THIRDPARTY_FRONTEND_PORT']+'/start_ore', json=json.dumps(enc))


def load_pubkey():
    pubkey = DictX
    with open('Buyer/pubkey.txt', 'r') as f:
        pubkey.n = int(f.readline()[:-1])
        pubkey.e = int(f.readline()[:-1])
    return pubkey


def restore_client():
    pubkey = load_pubkey()
    client = init_client(pubkey)
    return client


@celery.shared_task(name='checkcontainment')
@performancedecorator
def checkcontainment(data):
    if data is None:
        raise Exception
    # unblind set
    signed_set = json.loads(data)['signedblinds']
    # reconstruct random factors
    a_file = open("Buyer/random_factors.pkl", "rb")
    random_factors = pickle.load(a_file)
    a_file.close()

    # create client from stored pubkey
    client = restore_client()
    unblinded_set = client.unblind_set(signed_set, random_factors)
    encoded_set = [str(ucs).encode() for ucs in unblinded_set]
    input = []
    with open('Buyer/input.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            input.append(int(currentPlace))
    bloom_data = load_bloom_data()
    bf = reconstruct_bloom_filter(bloom_data)
    intr = client.intersect(input, encoded_set, bf)

    for y, b in zip(input, encoded_set):
        if not b in bf:
            # seller does not offer all required parts so abort
            return
    # seller has all parts so start ORE here
    start_ore()

    return

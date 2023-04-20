import simplejson as json
from base64 import b64encode

import celery
import app.PyPSI.psi.protocol.rsa as rsa
from app.PyPSI.psi.datastructure import bloom_filter
from app.ORE.OrderRevealingEncryption.ore import ore_enc
from app.Evaluator import performancedecorator, post
import pickle
import os
from hashlib import sha256
from Crypto.PublicKey import RSA
import requests


def init_server():
    # check if file exists then load priv key from there
    if(os.path.exists('Seller/privkey.pem')):
        with open('Seller/privkey.pem', 'r') as f:
            privkey = RSA.import_key(f.read())
            server = rsa.Server(private_key=privkey)

    #else create new server and store to file
    else:
        server = rsa.Server()
        privkey = server.private_key
        with open('Seller/privkey.pem', 'wb') as f:
            f.write(privkey.export_key('PEM'))

    return server


def load_input_and_sign():
    # load servers input list
    input = []
    with open('Seller/input.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            input.append(int(currentPlace))
    signed_set = server.sign_set(input)
    # store signed set
    with open('Seller/signed_set.txt', 'w+') as filehandle:
        for listitem in signed_set:
            filehandle.write('%s\n' % listitem)

    return signed_set


def load_signed_set():
    signed_set = []
    with open('Seller/signed_set.txt', 'r') as filehandle:
        for line in filehandle:

            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            signed_set.append(int(currentPlace))

    return signed_set


def build_bloom(signed_set):
    signed_server_set = [str(sss).encode() for sss in signed_set]
    fp_prob = 0.00001
    bf = bloom_filter.build_from(signed_server_set, fp_prob=fp_prob)
    return bf, fp_prob


@celery.shared_task(name='beginPSI')
@performancedecorator
def beginPSI(preCalc=False, testing=False):

    #get public key
    pubkey = server.public_key
    signed_set = []
    if not preCalc:
        signed_set = load_input_and_sign()
    else:
        # load signed set
        signed_set = load_signed_set()


    #build bloom filter
    bf, fp_prob = build_bloom(signed_set)

    # return bloom_filter and public key to client

    payload = dict()
    badict = dict()
    ba = bf._bitarray
    badict['endian'] = ba.endian()
    badict['bytes'] = b64encode(ba.tobytes())
    badict['len'] = len(ba)

    payload['bloomarray'] = badict
    payload['bloomcount'] = bf.count
    payload['bloomcapacity'] = bf.max_capacity
    payload['bloomfpprob'] = fp_prob
    payload['pubkeyE'] = pubkey.e
    payload['pubkeyN'] = pubkey.n

    test = bloom_filter.deserialize(json.loads(bloom_filter.serialize(ba)))
    assert(ba == test)
    assert(ba.tobytes() == test.tobytes())

    if testing:
        return payload, json.dumps(payload)
    else:
        try:
            post(
                'http://' + os.environ['BUYER_ADDRESS'] + ':' + os.environ['BUYER_FRONTEND_PORT'] + '/startClient',
                json=json.dumps(payload))
        except(requests.exceptions.ConnectionError):
            print("connection failed")
        return


@celery.shared_task(name='sign_blinds')
@performancedecorator
def sign_blinds(data, testing=False):
    # sign set
    set = json.loads(data)
    signed_set = server.sign_set(set['blinded_set'])
    signed_set_ints = []
    for s in signed_set:
        signed_set_ints.append(int(s))
    # return set
    payload = dict()
    payload['signedblinds'] = signed_set_ints

    if testing:
        return payload, json.dumps(payload)
    else:
        try:
            post(
                'http://' + os.environ['BUYER_ADDRESS'] + ':' + os.environ['BUYER_FRONTEND_PORT'] + '/signedblinds',
                json=json.dumps(payload))
        except(requests.exceptions.ConnectionError):
            print("connection failed")
        return

def send_failed_ore_conversion():
    try:
        post('http://'+os.environ['THIRDPARTY_ADDRESS']+':'+os.environ['THIRDPARTY_FRONTEND_PORT']+'/sender_input')
    except(requests.exceptions.ConnectionError):
        print("connection failed")


def send_successful_ore_conversion(enc):
    try:
        post('http://'+os.environ['THIRDPARTY_ADDRESS']+':'+os.environ['THIRDPARTY_FRONTEND_PORT']+'/sender_input', json=json.dumps(enc))
    except(requests.exceptions.ConnectionError):
        print("connection failed")


def create_reverse_mapping(prices):
    result = dict()
    for p in prices:
        h_val = int(sha256((str(p) + str(server.public_key.e)).encode('utf-8')).hexdigest(), 16)
        result[str(h_val)] = p
    return result


@celery.shared_task(name='send_ore')
@performancedecorator
def send_ore(data, testing=False):
    try:
        parsed = json.loads(data)
    except:
        # unable to parse list comparison failed
        print("unable to parse list comparison failed")

        if testing:
            return False
        else:
            send_failed_ore_conversion()
            return
    # load prices
    try:
        a_file = open("Seller/prices.pkl", "rb")
        prices = pickle.load(a_file)
    except:
        prices = dict()
    finally:
        a_file.close()


    # create reverse mapping
    reverse_mapping = create_reverse_mapping(prices)
    # create enc values
    enc = dict()
    for k in parsed['ids']:
        if(k in reverse_mapping):
            # find corresponding price
            corresponding_price = prices[reverse_mapping[k]]

            enc[k] = ore_enc(bin(corresponding_price)[2:], str(server.public_key.e))
        else:
            # some item has no price comparison failed
            print("comparison failed item has no price")

            if testing:
                return False
            else:
                send_failed_ore_conversion()
                return

    # conversion successful

    if testing:
        return True
    else:
        send_successful_ore_conversion(enc)
        return


server = init_server()

import simplejson as json
from base64 import b64encode

import celery
import app.paillier.phe.paillier as paillier
import app.paillier.phe.encoding
import pickle
import os
from hashlib import sha256
from Crypto.PublicKey import RSA
import requests
import time
import copy
import numpy.random
from app.Evaluator import performancedecorator, post
from app.Testmode import Testmode
from app.create_values import testmode


def send_blinds_to_seller(modulus, blind_enc_sum, threshold, testing=False):
    # make encrypted value serializable
    sum_value = blind_enc_sum.ciphertext()
    data = dict()
    data['pubkey'] = modulus
    data['blind_enc_sum'] = sum_value
    data['threshold'] = threshold.ciphertext()
    try:

        response = post(
            'http://' + os.environ['SELLER_FRONTEND_ADDRESS'] + ':' + os.environ['SELLER_FRONTEND_PORT'] + '/buyer_data',
            json=json.dumps(data))

    except:
        print("Sending failed")

    if testing:
        return data, json.dumps(data)


def send_encryptions_to_thirdparty(modulus, encryptedvals, testing=False):
    # make encrypted value serializable
    serial_s = time.time()
    serializableVals = []
    for v in encryptedvals:
        serializableVals.append(v.ciphertext(be_secure=False))
    serial_time = time.time()-serial_s
    print('SerialTime %f' % serial_time)
    data = dict()
    data['pubkey'] = modulus
    data['encryptedVals'] = serializableVals
    try:
        response = post(
            'http://' + os.environ['THIRDPARTY_FRONTEND_ADDRESS'] + ':' + os.environ['THIRDPARTY_FRONTEND_PORT'] + '/buyer_values',
            json=json.dumps(data))

    except:
        print("Sending failed")

    if testing:
        return data, json.dumps(data)


def store_encrypted_vals(encryptions):
    with open('Buyer/encryptions.txt', 'w+') as f:
        for e in encryptions:
            f.write('%s\n' % e.ciphertext())


def load_encryptions(pubkey):
    try:
        encryptions = []
        with open('Buyer/encryptions.txt', 'r') as f:
            for l in f:
                encryptions.append(paillier.EncryptedNumber(pubkey,int(l[:-1])))
        return encryptions
    except FileNotFoundError:
        print('no encryptions available')
        return None

def store_public_key(pubkey):
    filename = 'Buyer/pubkey.txt'
    with open(filename, 'w+') as filehandle:
        filehandle.write('%s\n' % pubkey.n)


def store_private_key(privkey):
    filename = 'Buyer/privkey.txt'
    with open(filename, 'w+') as filehandle:
        filehandle.write('%s\n' % privkey.p)
        filehandle.write('%s\n' % privkey.q)


def load_public_key():
    filename = 'Buyer/pubkey.txt'
    with open(filename, 'r') as f:
        for line in f:
            n = int(line[:-1])
    pubkey = paillier.PaillierPublicKey(n)
    return pubkey


def load_private_key():
    pubkey = load_public_key()
    filename = 'Buyer/privkey.txt'
    with open(filename, 'r') as f:
        p = int(f.readline()[:-1])
        q = int(f.readline()[:-1])
    privkey = paillier.PaillierPrivateKey(pubkey,p, q)
    return privkey


@celery.shared_task(name='distribute_encryption')
@performancedecorator
def distribute_encryption(data, preCalc=False, testing=False):
    """ Obtain list of randoms for blinding
        send public key and encrypted values to third party
        send public key and sum of blinded encrypted values to seller
        """

    try:
        parsed = json.loads(data)
    except:
        print("Failed to parse Randoms")

    # load config
    config = []
    try:
        with open('Buyer/config.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]

                # add item to the list
                config.append(int(currentPlace))
    except FileNotFoundError:
        print("No Config available")
        raise
    config_enc = []
    # either load encrypted values or create fresh encryption. only allow loading if encryptions and both keys are present

    if(preCalc and os.path.exists('Buyer/encryptions.txt') and os.path.exists('Buyer/pubkey.txt') and os.path.exists('Buyer/privkey.txt')):
        print('Loading encrypted values')
        start = time.time()
        pubkey = load_public_key()
        privkey = load_private_key()
        config_enc = load_encryptions(pubkey)
        end = time.time()-start
        print('Loading took %f' % end)
    # else calculate fresh values
    if (not preCalc or not config_enc):
        # create public and private key
        print('Failed to load encryptions')
        start = time.time()
        pubkey, privkey = paillier.generate_paillier_keypair()
        # store keys
        store_public_key(pubkey)
        store_private_key(privkey)
        s = time.time()
        randoms = numpy.random.randint(min(pubkey.n, 2**63-2), size=len(config)).tolist()
        end = time.time() - s
        print("fast %f" % end)
        enc_zero = pubkey.encrypt(0)
        enc_one = pubkey.encrypt(1)
        # config_enc_fast = [copy.deepcopy(enc_zero).obfuscate_new(int(r)) if v == 0 else copy.deepcopy(enc_one).obfuscate_new(int(r)) for v, r in zip(config, randoms)]

        s = time.time()
        config_enc = [pubkey.encrypt(v) for v in config]
        end = time.time() - s
        print("slow (original) %f" % end)
        end = time.time() - start
        print('encrypting took %f' % end)
        store_encrypted_vals(config_enc)
    # calc sum of encrypted blinded inputs
    sum_enc_s = time.time()
    sum_config_blind_enc = pubkey.encrypt(sum([v*b for v, b in zip(config, parsed['blinds'])]))
    sum_enc_time = time.time()-sum_enc_s
    print('Time for sum enc %f' % sum_enc_time)
    # load and encrypt threshold
    try:
        with open('Buyer/threshold.txt', 'r') as f:
            for line in f:
                threshold = int(line[:-1])
    except FileNotFoundError:
        print("No Threshold available")
        raise
    enc_thresh = pubkey.encrypt(threshold)
    send_encryptions_to_thirdparty(pubkey.n, config_enc)
    send_blinds_to_seller(pubkey.n, sum_config_blind_enc, enc_thresh)



@celery.shared_task(name='evaluate_result')
@performancedecorator
def evaluate_result(data, testing=False):
    """ Decrypt the obtained result.
        If result < 0 Seller is viable
        else seller is not viable
    """

    # parse result
    try:
        parsed = json.loads(data)
    except:
        print("Invalid input")

    # load private key
    pub_key = load_public_key()
    priv_key = load_private_key()

    #decrypt
    try:
        result = priv_key.decrypt(paillier.EncryptedNumber(pub_key, parsed['res']))
    except:
        print('decryption error')
        raise
    if result < 0:
        print("seller is vialbe")
    else:
        print("seller is not viable")

    with open('finished.txt', 'w+') as f:
        pass

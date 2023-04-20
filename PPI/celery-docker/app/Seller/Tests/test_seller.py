import unittest
from base64 import b64decode

from app.Seller.tasks import server, beginPSI, sign_blinds, init_server, load_input_and_sign, build_bloom, send_ore, load_signed_set, create_reverse_mapping
from app.PyPSI.psi.protocol.rsa.utils import decrypt, encrypt, sign
from app.PyPSI.psi.datastructure.bloom_filter import deserialize
from app.create_values import max_num_items
from bitarray import bitarray
from hashlib import sha256
import simplejson as json
import gmpy2

class TestSeller(unittest.TestCase):

    def test_init_server(self):
        loaded_server = init_server()
        self.assertEqual(loaded_server.public_key, server.public_key)
        self.assertEqual(loaded_server.private_key, server.private_key)

    def test_load_input_and_sign(self):
        signed_set = load_input_and_sign()
        input = []
        pubkey = server.public_key
        with open('Seller/input.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]

                # add item to the list
                input.append(int(currentPlace))
        for i,s in zip(input, signed_set):
            'check signature'
            decr = encrypt(server.public_key, s)
            self.assertEqual(i, decr)

    def test_build_bloom(self):
        input = [1,2,3,4,5,6]
        bf, _ = build_bloom(input)
        encoded_input = [str(i).encode() for i in input]
        for i in encoded_input:
            self.assertTrue(bf.check(i))

    def test_beginPSI(self):
        self.maxDiff = None
        original_payload, payload = beginPSI(testing=True)
        # payload parsed correctly
        parsed = json.loads(payload)
        self.assertEqual(original_payload['bloomcount'], parsed['bloomcount'])
        self.assertEqual(original_payload['pubkeyE'], parsed['pubkeyE'])
        self.assertEqual(original_payload['pubkeyN'], parsed['pubkeyN'])
        bloomarray = deserialize(parsed['bloomarray'])
        original_bloomarray = bitarray(endian=original_payload['bloomarray']["endian"])
        original_bloomarray.frombytes(b64decode(original_payload['bloomarray']["bytes"]))
        original_bloomarray[:original_payload['bloomarray']["len"]]
        self.assertEqual(bloomarray, original_bloomarray)

    def test_preCalc(self):
        # get signed set
        mpz_ss = load_input_and_sign()
        precalculated = load_signed_set()
        self.assertEqual(mpz_ss, precalculated)

    def test_sign_blinds(self):

        input = [1,2,3,4]
        data = dict()
        data['blinded_set'] = input
        original, dump = sign_blinds(json.dumps(data), testing=True)
        self.assertEqual(original['signedblinds'], json.loads(dump)['signedblinds'])
        for i,s in zip(input, original['signedblinds']):
            decr = encrypt(server.public_key, s)
            self.assertEqual(i, decr)

    def test_send_ore(self):
        # test unparsable json
        data = None
        res = send_ore(data, testing=True)
        self.assertFalse(res)

        # test id not in set
        ids = [str(max_num_items+1)]
        payload = dict()
        payload['ids'] = ids
        data = json.dumps(payload)
        res = send_ore(data, testing=True)
        self.assertFalse(res)

        # test id in set
        ids = [int(sha256((str(max_num_items-1) + str(server.public_key.e)).encode('utf-8')).hexdigest(), 16)]
        payload = dict()
        payload['ids'] = ids
        data = json.dumps(payload)
        res = send_ore(data, testing=True)
        self.assertTrue(res)


    def test_create_reverse_mapping(self):
        original_dict = dict()
        original_dict[1] = 1
        original_dict[2] = 2
        original_dict[3] = 99
        mapping = create_reverse_mapping(original_dict)
        self.assertEqual(mapping[int(sha256((str(1) + str(server.public_key.e)).encode('utf-8')).hexdigest(), 16)], 1)
        self.assertEqual(mapping[int(sha256((str(2) + str(server.public_key.e)).encode('utf-8')).hexdigest(), 16)], 2)
        self.assertEqual(original_dict[mapping[int(sha256((str(3) + str(server.public_key.e)).encode('utf-8')).hexdigest(), 16)]], original_dict[3])
        self.assertEqual(len(original_dict), len(mapping))

if __name__ == '__main__':
    unittest.main()

import unittest
from base64 import b64decode, b64encode

from app.Buyer.tasks import reconstruct_bloom_filter, blind_input, random_factors, init_client, start_ore
from app.Seller.tasks import init_server
from app.PyPSI.psi.protocol.rsa.utils import decrypt, encrypt, sign, inverse, mulmod
from app.PyPSI.psi.datastructure.bloom_filter import deserialize
from app.PyPSI.psi.datastructure import bloom_filter
from bitarray import bitarray
import simplejson as json
import gmpy2

class TestBuyer(unittest.TestCase):

    def test_reconstruct_bloom_filter(self):
        input = [1,2,3,4]
        encoded = [str(i) .encode()for i in input]
        bf = bloom_filter.build_from(encoded, fp_prob=0.0001)
        data = dict()
        ba = dict()
        ba['endian'] = bf._bitarray.endian()
        ba['len'] = len(bf._bitarray)
        ba['bytes'] = b64encode(bf._bitarray.tobytes())
        data['bloomarray'] = ba
        data['bloomcapacity'] = bf.max_capacity
        data['bloomfpprob'] = 0.0001
        data['bloomcount'] = bf.count
        reconstructed = reconstruct_bloom_filter(data)
        self.assertEqual(bf.count, reconstructed.count)
        self.assertEqual(bf._bitarray, reconstructed._bitarray)
        for e in encoded:
            self.assertTrue(reconstructed.check(e))

    def test_blind_input(self):
        # init server to get pubkey and initialize client
        server = init_server()
        client = init_client(server.public_key)
        self.assertEqual(server.public_key.n, client.public_key.n)
        self.assertEqual(server.public_key.e, client.public_key.e)
        input = [1,2,3,4,5]
        blinded_input, random_factors = blind_input(input, client)
        random_factors[1][1]
        for l in range(len(input)):
            self.assertEqual(input[l], mulmod(blinded_input[l], inverse(client.public_key, random_factors[l][1]), client.public_key.n))
            


if __name__ == '__main__':
    unittest.main()

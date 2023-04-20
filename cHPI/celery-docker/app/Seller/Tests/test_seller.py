import unittest
from base64 import b64decode

from app.Seller.tasks import load_products, store_list, send, store, load_pubkey, load_encryptedNumber, load_number, deblind_result
from app.paillier.phe.paillier import generate_paillier_keypair
import os

from bitarray import bitarray
from hashlib import sha256
import simplejson as json
import gmpy2


class TestSeller(unittest.TestCase):
    def setup(self):
        pass

    def test_store_and_load_prices(self):
        prices = [1,2,3,4]
        store_list(prices, 'Seller/input.txt')
        loaded = load_products()
        self.assertEqual(prices, loaded)
        os.remove('Seller/input.txt')

    def test_store_and_load_pubkey(self):
        pubkey, privkey = generate_paillier_keypair()

        store(pubkey.n, 'Seller/pubkey.txt')
        loaded_key = load_pubkey()
        enc = loaded_key.encrypt(22)
        # check pubkey has correct n
        self.assertEqual(loaded_key.n, pubkey.n)
        # check encryption is correct
        self.assertEqual(privkey.decrypt(enc), 22)
        os.remove('Seller/pubkey.txt')

    def test_store_and_load_encryptedNumber(self):
        pubkey, privkey = generate_paillier_keypair()
        enc = pubkey.encrypt(22)
        cipher = enc.ciphertext()
        store(pubkey.n, 'Seller/pubkey.txt')
        store(cipher, 'Seller/enc_num.txt')
        loaded_num = load_encryptedNumber('Seller/enc_num.txt')
        # check encrypted num is decrypted correctly
        self.assertEqual(privkey.decrypt(loaded_num), 22)

        # remove temp file
        os.remove('Seller/enc_num.txt')
        os.remove('Seller/pubkey.txt')

    def test_store_and_load_number(self):
        num = 22
        store(num, 'Seller/temp.txt')
        loaded_num = load_number('Seller/temp.txt')
        # check correctness
        self.assertEqual(num, loaded_num)

        # remove temp file
        os.remove('Seller/temp.txt')


    def test_deblind_result(self):
        pubkey, privkey = generate_paillier_keypair()
        config = [1,0]
        r1 = 5
        T = 7
        blinds = [10, 12]
        prices = [5, 100]
        blinded_res = pubkey.encrypt(35)

        store(r1, 'Seller/random1.txt')
        store(pubkey.encrypt(T).ciphertext(), 'Seller/threshold.txt')
        store(pubkey.n, 'Seller/pubkey.txt')
        store(pubkey.encrypt(10).ciphertext(), 'Seller/enc_sum.txt')
        data = dict()
        data['res'] = blinded_res.ciphertext()
        res = deblind_result(json.dumps(data))
        self.assertLess(privkey.decrypt(res), 0)

        T = 4
        store(pubkey.encrypt(T).ciphertext(), 'Seller/threshold.txt')
        js = json.dumps(data)
        res = deblind_result(js)
        self.assertGreater(privkey.decrypt(res), 0)

        os.remove('Seller/random1.txt')
        os.remove('Seller/threshold.txt')
        os.remove('Seller/pubkey.txt')
        os.remove('Seller/enc_sum.txt')


if __name__ == '__main__':
    unittest.main()


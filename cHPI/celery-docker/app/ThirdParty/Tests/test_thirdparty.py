import unittest
from base64 import b64decode

from app.ThirdParty.tasks import store_list, store_single_val, store, load, load_number_list, load_bool, start_calculation
from app.paillier.phe.paillier import generate_paillier_keypair, PaillierPublicKey
from bitarray import bitarray
import simplejson as json
import gmpy2
import os

class TestThirdParty(unittest.TestCase):

    def test_store_and_load_number_list(self):
        nums = [1,2,3,4,5]
        store(nums, 'ThirdParty/nums_temp.txt')
        loaded_nums = load_number_list('ThirdParty/nums_temp.txt')
        os.remove('ThirdParty/nums_temp.txt')
        shouldbeNone = load_number_list('ThirdParty/nums_temp.txt')

        self.assertEqual(nums, loaded_nums)
        self.assertEqual(shouldbeNone, None)

    def test_store_and_load_boolean(self):
        bool = True
        store(bool, 'ThirdParty/bool_temp.txt')
        loaded_bool = load_bool('ThirdParty/bool_temp.txt')
        os.remove('ThirdParty/bool_temp.txt')
        shouldbeFalse = load_bool('ThirdParty/bool_temp.txt')

        bool = True
        store(bool, 'ThirdParty/seller_completion.txt')
        b = load('seller_completion')
        self.assertEqual(bool, b)
        os.remove('ThirdParty/seller_completion.txt')
        self.assertEqual(loaded_bool, bool)
        self.assertEqual(shouldbeFalse, False)

    def test_load_and_store_pubkey(self):
        pubkey, _ = generate_paillier_keypair()
        store(pubkey.n, 'ThirdParty/pubkey.txt')
        loaded_key = load('pubkey')
        os.remove('ThirdParty/pubkey.txt')
        no = load('pubkey')

        self.assertEqual(pubkey.n, loaded_key.n)
        self.assertEqual(no, None)

    def test_load_and_store_encrypted_values(self):
        pubkey, privkey = generate_paillier_keypair()
        vals = [1,2,3]
        store(pubkey.n, 'ThirdParty/pubkey.txt')
        enc_vals = [pubkey.encrypt(v) for v in vals]
        ciphers = [e.ciphertext() for e in enc_vals]
        store(ciphers, 'ThirdParty/buyer_vals.txt')
        loaded_vals = load('buyer_values')
        os.remove('ThirdParty/buyer_vals.txt')
        os.remove('ThirdParty/pubkey.txt')
        no = load('buyer_values')

        decr = [privkey.decrypt(v) for v in loaded_vals]
        self.assertEqual(decr, vals)

        self.assertEqual(no, None)

    def test_start_calculation(self):
        store(True, 'ThirdParty/seller_completion.txt')
        buyer_vals = [1, 2]
        pubkey, privkey = generate_paillier_keypair()
        enc_vals = [pubkey.encrypt(v) for v in buyer_vals]
        ciphers = [e.ciphertext() for e in enc_vals]
        store(ciphers, 'ThirdParty/buyer_vals.txt')
        store(pubkey.n, 'ThirdParty/pubkey.txt')
        seller_vals = [5, 10]
        store(seller_vals, 'ThirdParty/seller_vals.txt')
        res = start_calculation()
        os.remove('ThirdParty/seller_completion.txt')
        os.remove('ThirdParty/buyer_vals.txt')
        os.remove('ThirdParty/pubkey.txt')
        os.remove('ThirdParty/seller_vals.txt')

        self.assertEqual(privkey.decrypt(res), 25)

if __name__ == '__main__':
    unittest.main()

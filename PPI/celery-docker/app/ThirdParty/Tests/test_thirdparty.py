import unittest
from base64 import b64decode

from app.ThirdParty.tasks import store_buyer, load_buyer_data, handle_seller
from app.ORE.OrderRevealingEncryption.ore import rnd_word, ore_enc
from bitarray import bitarray
import simplejson as json
import gmpy2

class TestThirdParty(unittest.TestCase):

    def test_store_and_load_buyer(self):
        td = dict()
        td[1] = 123
        td[2] = 234
        td[3] = 345
        store_buyer(td)
        loaded = load_buyer_data()
        self.assertEqual(td, loaded)

    def test_comparison(self):
        #secret key
        key = rnd_word(10)
        # create input dict
        input = dict()
        input['1'] = ore_enc(bin(123)[2:], key)
        input['2'] = ore_enc(bin(234)[2:], key)
        store_buyer(input)
        sellerdata = dict()
        sellerdata['1'] = ore_enc(bin(123)[2:], key)
        sellerdata['2'] = ore_enc(bin(234)[2:], key)

        wrongsellerdata = dict()
        wrongsellerdata[1] = ore_enc(bin(123)[2:], key)

        expensive_sellerdata = dict()
        expensive_sellerdata[1] = ore_enc(bin(456)[2:], key)
        expensive_sellerdata[2] = ore_enc(bin(99999999)[2:], key)

        comp1 = handle_seller(json.dumps(sellerdata))
        self.assertTrue(comp1)
        comp2 = handle_seller(json.dumps(wrongsellerdata))
        self.assertFalse(comp2)
        comp3 = handle_seller(json.dumps(expensive_sellerdata))
        self.assertFalse(comp3)


if __name__ == '__main__':
    unittest.main()

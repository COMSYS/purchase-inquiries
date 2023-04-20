import unittest
from base64 import b64decode, b64encode

from app.paillier.phe.paillier import generate_paillier_keypair, EncryptedNumber, PaillierPublicKey, PaillierPrivateKey
from app.Buyer.tasks import send_blinds_to_seller, send_encryptions_to_thirdparty, store_public_key, load_public_key, store_private_key, load_private_key
from bitarray import bitarray
import simplejson as json
import gmpy2
import os

class TestBuyer(unittest.TestCase):

    def tearDown(self):
        try:
            os.remove('Buyer/pubkey.txt')
            os.remove('Buyer/privkey.txt')
        except FileNotFoundError:
            pass

    def test_send_blinds_to_seller(self):
        pubkey, privkey = generate_paillier_keypair()
        val = 22
        enc_val = pubkey.encrypt(22)
        orig, js = send_blinds_to_seller(pubkey.n, enc_val, enc_val, testing=True)
        # json parses correctly
        self.assertEqual(orig, json.loads(js))
        # reconstruction of ciphtertext works
        self.assertEqual(EncryptedNumber(pubkey,orig['blind_enc_sum']).ciphertext(be_secure=False), enc_val.ciphertext())
        # decryption works
        self.assertEqual(privkey.decrypt(EncryptedNumber(pubkey,orig['blind_enc_sum'])), privkey.decrypt(enc_val))

    def test_send_encryptions_to_thirdparty(self):
        pubkey, privkey = generate_paillier_keypair()
        vals = [1, 2, 3, 4, 5]
        enc_vals = [pubkey.encrypt(v) for v in vals]
        ciphertexts = [v.ciphertext() for v in enc_vals]
        orig, js = send_encryptions_to_thirdparty(pubkey.n, enc_vals, testing=True)
        # json parses correctly
        publicKey = PaillierPublicKey(orig['pubkey'])
        self.assertEqual(orig, json.loads(js))
        # list of encryptions is recoverable
        self.assertEqual([EncryptedNumber(publicKey, v).ciphertext(be_secure=False) for v in orig['encryptedVals']], ciphertexts)

    def test_store_and_load_publickey(self):
        pubkey, privkey = generate_paillier_keypair()
        store_public_key(pubkey)

        loaded_key = load_public_key()
        # check equality
        self.assertEqual(pubkey.n, loaded_key.n)

    def test_store_and_load_privatekey(self):
        pubkey, privkey = generate_paillier_keypair()
        val = pubkey.encrypt(22)
        store_public_key(pubkey)
        store_private_key(privkey)
        loaded_key = load_private_key()
        # check equality
        self.assertEqual(privkey.p, loaded_key.p)
        self.assertEqual(privkey.q, loaded_key.q)
        # assert decryption is correct
        self.assertEqual(privkey.decrypt(val), 22)


if __name__ == '__main__':
    unittest.main()

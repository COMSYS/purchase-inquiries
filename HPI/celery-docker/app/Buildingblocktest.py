
import random
import time
import app.paillier.phe.paillier as paillier
from app.paillier.phe.paillier import PaillierPublicKey, EncryptedNumber


config_size = 10
max_num_items = 1000

if __name__ == '__main__':

    for i in range(3):
        buyerconfig = []
        for i in range(config_size):
            buyerconfig.append(1)
        for i in range(max_num_items - config_size):
            buyerconfig.append(0)

        seller_prices = []
        for i in range(max_num_items):
            seller_prices.append(random.randrange(2, 2 ** 32))
        threshold = config_size*(2**33)



        pubkey, privkey = paillier.generate_paillier_keypair()

        start_encryption = time.time()
        config_enc = [pubkey.encrypt(v) for v in buyerconfig]

        end_encryption = time.time()
        print("Encryption took")
        encryptiontime= end_encryption-start_encryption
        print(encryptiontime)

        start_blinding = time.time()
        r1 = random.randrange(2 ** 8, 2 ** 12)
        blinded_prices = [r1 * p for p in seller_prices]

        end_blinding = time.time()
        print("blinding took")
        blindingtime = end_blinding-start_blinding
        print(blindingtime)

        extended_blinding_s = time.time()
        r1 = random.randrange(2 ** 8, 2 ** 12)
        rands = [random.randrange(2**8, 2**12) for p in seller_prices]
        blinded_prices = [r1 * p+r for p,r in zip(seller_prices, rands)]
        extended_blinding_e= time.time()
        print("extended blinding (for thirdparty) took")
        extendedblindingtime = extended_blinding_e-extended_blinding_s
        print(extendedblindingtime)

        start_vectormult = time.time()
        mult = sum([v * u for v, u in zip(config_enc, blinded_prices)])
        r2 = random.randrange(1, r1 - 1)
        res = mult - (r1 * threshold) + pubkey.encrypt(r2)
        end_vectormult = time.time()
        print("Vector multiplication took")
        vectormulttime = end_vectormult-start_vectormult
        print(vectormulttime)

        with open('eval/buildingblocks/encryption'+ str(max_num_items) +'.txt', 'a+') as f:
            f.write('%s\n'% str(encryptiontime))

        with open('eval/buildingblocks/blinding'+ str(max_num_items) +'.txt', 'a+') as f:
            f.write('%s\n'% str(blindingtime))

        with open('eval/buildingblocks/vector'+ str(max_num_items) +'.txt', 'a+') as f:
            f.write('%s\n'% str(vectormulttime))
        with open('eval/buildingblocks/extendedblinding'+ str(max_num_items) +'.txt', 'a+') as f:
            f.write('%s\n'% str(extendedblindingtime))

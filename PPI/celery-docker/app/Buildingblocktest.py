import app.PyPSI.psi.protocol.rsa as rsa
from app.PyPSI.psi.datastructure import bloom_filter
from app.ORE.OrderRevealingEncryption.ore import ore_enc
from app.Evaluator import performancedecorator, post
from app.ORE.OrderRevealingEncryption.ore import ore_comp
import random
import time

size = 10000
config = 10000
size_ore = 10000

def measure_psi():
    for i in range(3):
        server = rsa.Server()
        privkey = server.private_key
        pubkey = server.public_key

        seller_ids = []
        for i in range(1, size):
            seller_ids.append(i)

        seller_prices = dict()
        for id in seller_ids:
            seller_prices[str(id)] = random.randrange(2, 2 ** 32)

        buyer_ids = []
        for i in range(1, config):
            buyer_ids.append(i)
        buyer_prices = dict()
        prices = dict()
        for id in buyer_ids:
            buyer_prices[str(id)] = random.randrange(2 ** 33, 2 ** 34)

        sign_ids = time.time()
        signed_set = server.sign_set(seller_ids)
        end_sign_ids = time.time()
        sign_ids_time = end_sign_ids - sign_ids
        print("signing ids took")
        print(sign_ids_time)

        build_bloom_s = time.time()
        signed_server_set = [str(sss).encode() for sss in signed_set]
        fp_prob = 0.00001
        bf = bloom_filter.build_from(signed_server_set, fp_prob=fp_prob)
        build_bloom_e = time.time()
        build_bloom_time = build_bloom_e - build_bloom_s
        print("building bloom filter took")
        print(build_bloom_time)

        blinding_client_s = time.time()
        client = rsa.Client(pubkey)
        random_factors = client.random_factors(len(buyer_ids))
        blinded_input = client.blind_set(buyer_ids, random_factors)
        blinding_client_e = time.time()
        blinding_client_time = blinding_client_e - blinding_client_s
        print("Blinding client vals took")
        print(blinding_client_time)

        signing_client_s = time.time()
        signed_set = server.sign_set(blinded_input)
        signing_client_e = time.time()
        signing_client_time = signing_client_e - signing_client_s
        print("Signing blinded client took")
        print(signing_client_time)

        unblinding_s = time.time()
        unblinded_set = client.unblind_set(signed_set, random_factors)
        unblinding_e = time.time()
        unblinding_time = unblinding_e - unblinding_s
        print("unblinding took")
        print(unblinding_time)

        intersect_s = time.time()
        encoded_set = [str(ucs).encode() for ucs in unblinded_set]
        intr = client.intersect(buyer_ids, encoded_set, bf)
        intersect_e = time.time()
        intersect_time = intersect_e - intersect_s
        print("intersection took")
        print(intersect_time)

        with open("eval/buildingblocks/psi_buildingblock_eval.txt", 'a+') as f:
            f.write("sign ids, %s\n" % str(sign_ids_time))
            f.write("build bloom, %s\n" % str(build_bloom_time))
            f.write("blind client values, %s\n" % str(blinding_client_time))
            f.write("sign client values, %s\n" % str(signing_client_time))
            f.write("unblinding client values, %s\n" % str(unblinding_time))
            f.write("intersection, %s\n" % intersect_time)

def measure_ore():
    server = rsa.Server()
    privkey = server.private_key
    pubkey = server.public_key

    seller_ids = []
    for i in range(1, size_ore):
        seller_ids.append(i)

    seller_prices = dict()
    for id in seller_ids:
        seller_prices[str(id)] = random.randrange(2, 2 ** 32)

    buyer_ids = []
    for i in range(1, size_ore):
        buyer_ids.append(i)
    buyer_prices = dict()

    for id in buyer_ids:
        buyer_prices[str(id)] = random.randrange(2 ** 33, 2 ** 34)

    for i in range(3):
        buyer_enc_s = time.time()
        enc = []
        for k in buyer_ids:
            enc.append(ore_enc(bin(buyer_prices[str(k)])[2:], str(pubkey.e)))
        buyer_enc_e = time.time()
        buyer_enc_time = buyer_enc_e - buyer_enc_s
        print(" buyer enccryption took")
        print(buyer_enc_time)

        seller_enc_s = time.time()
        enc_seller = []
        for k in buyer_ids:
            enc_seller.append(ore_enc(bin(seller_prices[str(k)])[2:], str(pubkey.e)))
        seller_enc_e = time.time()
        seller_enc_time = seller_enc_e - seller_enc_s
        print("seller encrypiton took")
        print(seller_enc_time)

        compare_s = time.time()
        for b,s in zip(enc, enc_seller):
            ore_comp(b,s)
        compare_e = time.time()
        compare_time = compare_e - compare_s
        print("comparison took")
        print(compare_time)

        with open("eval/buildingblocks/ore_buildingblock_eval.txt", 'a+') as f:
            f.write("Buyer encryption, %s\n" % str(buyer_enc_time))
            f.write("seller encryption, %s\n" % str(seller_enc_time))
            f.write("comparison, %s\n" % str(compare_time))

if __name__ == '__main__':
    measure_psi()
    measure_ore()

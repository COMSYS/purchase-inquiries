import os

import hashlib
import random
from app.paillier.phe import paillier, util, encoding
import time
if __name__ == '__main__':
    len = 10000
    v_orig = [1 for i in range(1, len-1)]+[0]
    u_orig = [random.randrange(2 ** 30, 2 ** 32) for i in range(1, len)]
    T = sum(u_orig) - u_orig[-1] +1
    rand2 = random.randrange(2 ** 2, 2 ** 10)
    start = time.time()
    rand1 = random.randrange(2**2,2**10)
    # print("v", v_orig)
    # print("u", u_orig)
    print("T", T)
    print("rand1", rand1, " rand2", rand2)

    pubkey, privkey = paillier.generate_paillier_keypair()
    v_enc = [pubkey.encrypt(v) for v in v_orig]
    u_blind = [(rand2*u+rand1) for u in u_orig]
    # encoded_u_blind = [encoding.EncodedNumber.encode(pubkey, u) for u in u_blind]

    T_enc = pubkey.encrypt(T)
    v_blind = [v*rand1 for v in v_orig]
    v_blind_enc = pubkey.encrypt(sum(v_blind))
    mult = sum([v * u for v,u in zip(v_enc,u_blind)])
    print("Shoudl be 63", privkey.decrypt(mult))

    removed_blind = mult - v_blind_enc
    print("should be 55", privkey.decrypt(removed_blind))
    rand3 = 4
    res = removed_blind - (rand2*T_enc) + pubkey.encrypt(rand3)
    runtime = time.time() -start
    result = privkey.decrypt(res)
    print("res is", result)
    if result < 0:
        print("seller viable")
    else:
        print('Seller not viable')
    print("runtime for {} entries is {}".format(len, runtime))

    print("second idea")
    start = time.time()
    pubkey, privkey = paillier.generate_paillier_keypair()
    v_enc = [pubkey.encrypt(v) for v in v_orig]
    u_blind = [rand2*u for u in u_orig]
    T_enc = pubkey.encrypt(T)
    mult = sum([v*u for v,u in zip(v_enc, u_blind)])
    res = mult-(rand2*T_enc) + pubkey.encrypt(rand3)
    runtime = time.time() - start
    print("res is", privkey.decrypt(res))
    print("runtime for {} entries is {}".format(len, runtime))
    


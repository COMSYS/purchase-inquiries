import random
import sys
from app.ORE.OrderRevealingEncryption.ore import ore_enc
e=0x10001
ks = [1,10,100, 1000]
def sizes():
    for k in ks:
        prices = []
        for i in range(k):
            prices.append(random.randrange(2**33, 2 ** 34))
        encs = []
        for p in prices:
            encs.append(ore_enc(bin(p)[2:], str(e)))
        print(sys.getsizeof(encs))
        size = 0
        for p in encs:
            size = size + sys.getsizeof(p)
        print(size)
if __name__ == '__main__':
    sizes()

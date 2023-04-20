import hashlib
import random
from string import ascii_uppercase, digits
LEN = 32
MAX_LEN = 64

def rnd_word(n):
    return ''.join(random.choice(ascii_uppercase + digits) for _ in range(n))


def prf(msg, k):
    pad = "0" * (LEN - len(msg))
    return int(hashlib.sha224((str(msg) + pad + str(k)).encode('utf-8')).hexdigest(), 16)


def ore_enc(m, k):
    tmp_m = ""
    tmpres = ""
    for i in m:
        tmp_m += i
        tmpres += str((prf(tmp_m[:-1], k) + int(tmp_m[-1])) % 3)
    return tmpres


def ore_comp(u, v):
    if u == v:
        return 0
    L = len(u)
    cnt = 0
    while u[cnt] == v[cnt]:
        cnt += 1
    if (int(u[cnt]) + 1) % 3 == int(v[cnt]):
        return -1
    else:
        return 1


def int_comp(u, v):
    if u == v:
        return 0
    elif u > v:
        return 1
    else:
        return -1

def pad_to_length(num):
    """ convert number to binary and add leading zeros to pad to max length"""
    return format(num, 'b').zfill(MAX_LEN)
cnt = 0
tests = 10
for i in range(tests):
    passwd = rnd_word(10)
    num1 = random.randrange(2**1, 2**63)
    num2 = random.randrange(2**1, 2**63)
    num1 = pad_to_length(num1)
    num2 = pad_to_length(num2)

    a = ore_enc(num1, passwd)
    b = ore_enc(num2, passwd)
    if ore_comp(a, b) == int_comp(num1, num2):
        cnt += 1
print("Succeded in: %d out of %d tests." % (cnt, tests))

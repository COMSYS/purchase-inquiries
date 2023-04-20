import math
import hashlib
import gmpy2
from binascii import unhexlify
from bitarray import bitarray
import simplejson as json
from base64 import b64encode, b64decode

class BloomFilter:
    """
    Bloom filter implementation.
    Section 3: http://gsd.di.uminho.pt/members/cbm/ps/dbloom.pdf
    """

    def __init__(self, capacity, fp_prob=0.001, bits=None, count=0):
        """
        Args:
            capacity: maximum number of elements the bloom filter should hold to
                satisfy the probability of false positives.
            fp_prob: probability of false positives. Inserting more than the
                specified size will increase this probability.
        """
        if capacity <= 0:
            raise ValueError("capacity must be an integer > 0")
        if not 0 < fp_prob < 1:
            raise ValueError("fp_prob must be in the range (0,1)")

        self.max_capacity = capacity

        self._size = math.ceil(-capacity * math.log2(fp_prob) / math.log(2))
        self._size = math.ceil(self._size / 8) * 8
        self._num_hash_functions = math.ceil(-math.log2(fp_prob))
        if(bits is None):
            # set bitarray
            self.count = 0
            self._bitarray = bitarray(self._size)
            self._bitarray.setall(0)
        else:
            self.count = count
            self._bitarray = bits

    def hashes(self, x):
        """Compute the hash of x for the different filters.

        Args:
            x: element to hash (bytes).

        Returns:
            list of hashes, one hash for each filter.
        """
        assert isinstance(x, bytes), "BloomFilter accepts bytes objects"

        hash_func = hashlib.new('sha256')
        hash_func.update(b'1' + x)
        h1 = int(hash_func.hexdigest(), 16) % self._size
        hash_func = hashlib.new('sha256')
        hash_func.update(b'2' + x)
        h2 = int(hash_func.hexdigest(), 16) % self._size

        hashes = []
        for i in range(self._num_hash_functions):
            hashes.append((h1 + i * h2) % self._size)

        return hashes

    def add(self, x):
        """Add an element to the bloom filter.

        Args:
            x: element to add (bytes).
        """
        if self.count >= self.max_capacity:
            raise RuntimeWarning("Bloom filter is at maximum capacity")

        hashes = self.hashes(x)
        for h in hashes:
            self._bitarray[h] = 1

        self.count += 1

    def check(self, x):
        """Check whether an element is in the bloom filter.

        Args:
            x: element to check (bytes).

        Returns:
            boolean whether x is possibly in the bloom filter (True) or not (False).
        """
        hashes = self.hashes(x)
        for h in hashes:
            if not self._bitarray[h]:
                return False

        return True

    def __contains__(self, x):
        return self.check(x)

    def __len__(self):
        return self.count


def build_from(X, capacity=None, fp_prob=None):
    """Create a bloom_filter and add the set X.

    Args:
        X: a list of elements.
        capacity: maximum capacity of the bloom filter, set to len(X) if not
            specified.
        fp_prob: probability of false positives.

    Returns:
        BloomFilter filled with elements of the set X.
    """
    if capacity is None:
        capacity = len(X)

    if fp_prob is None:
        bf = BloomFilter(capacity)
    else:
        bf = BloomFilter(capacity, fp_prob)

    for x in X:
        bf.add(x)

    return bf

########################################################################
##
## Made changes (below):
##  Added (de)serialization support to PyPSI
##
########################################################################

def serialize(ba):
    """Serialize a bitarray ba and return its json representation.

    Args:
        ba: a bitarray.

    Returns:
        json object filled with elements of the bitarray ba.
    """
    return json.dumps({
        "endian": ba.endian(),
        "bytes": b64encode(ba.tobytes()),
        "len": len(ba)
    })


def deserialize(data):
    """Deserialize a json object data and return its bitarray ba.

    Args:
        data: a json object.

    Returns:
        bitarray ba extracted from the json object data.
    """
    ba = bitarray(endian=data["endian"])
    ba.frombytes(b64decode(data["bytes"]))
    return ba[:data["len"]]

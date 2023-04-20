from tests.protocol.test_rsa import run_protocol
from timeit import default_timer as timer

start = timer()
server = list(range(0,2**15))
client = [5,4,99]


run_protocol(client,server)
end = timer()
print("elapsed time")
print("%6.2f"%(end-start))


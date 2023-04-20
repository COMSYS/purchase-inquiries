import sys
from memory_profiler import profile, memory_usage
import time
from app.Testmode import Testmode
from app.create_values import testmode
import functools
import requests
import inspect


def performancedecorator(func):
    @functools.wraps(func)
    def function_wrapper(*args, **kwargs):
        fd = open(func.__name__ + '.log', 'w+')
        sys.stdout = fd
        f = profile(func)
        res = f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        fd.close()

        return res

    def timing_wrapper(*args, **kwargs):

        start_precise = time.time()
        res = func(*args, **kwargs)
        end_precise = time.time()
        with open('starttimes_' + func.__name__ + '.txt', 'a+') as fd:
            fd.write('%s\n' % start_precise)
        with open('endtimes_' + func.__name__ + '.txt', 'a+') as fd:
            fd.write('%s\n' % end_precise)
        return res

    @functools.wraps(func)
    def overall_timing_wrapper(*args, **kwargs):
        print('Starting function %s' % func.__name__)
        if func.__name__ == 'distribute_encryption':
            start = time.time()
            with open('starttimes.txt', 'a+') as f:
                f.write('%s\n' % start)
        start_precise = time.time()
        fd = open(func.__name__ + '.log', 'w+')
        sys.stdout = fd
        f = profile(func)
        res = f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        fd.close()
        end_precise = time.time()
        if func.__name__ == 'evaluate_result':
            end = time.time()
            with open('endtimes.txt', 'a+') as f:
                f.write('%s\n' % end)
        with open('starttimes_' + func.__name__ + '.txt', 'a+') as fd:
            fd.write('%s\n' % start_precise)
        with open('endtimes_' + func.__name__ + '.txt', 'a+') as fd:
            fd.write('%s\n' % end_precise)
        return res


    return overall_timing_wrapper



def post(*args, **kwargs):
    if True:

        start = time.time()
        response = requests.post(*args, **kwargs)
        end = time.time()
        method_len = len(response.request.method)
        url_len = len(response.request.url)
        headers_len = len('\r\n'.join('{}{}'.format(k, v) for k, v in response.request.headers.items()))
        body_len = len(response.request.body if response.request.body else [])

        req_size = method_len + url_len + headers_len + body_len
        print("size is ", req_size)
        print("writing to file now ")
        outername =  inspect.currentframe().f_back.f_code.co_name
        try:
            f = open('network_measurements.log', 'a+')
            f.write('%s, %s, %s, %s\n' % (str(start), str(end), str(req_size), outername))
            f.close()
        except:
            raise
        return response
    else:
        return requests.post(*args, **kwargs)

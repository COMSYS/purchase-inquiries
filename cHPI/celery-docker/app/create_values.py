import pickle
import random
import os
import requests
import time
import simplejson as json
from app.Testmode import Testmode
import datetime
import shutil


testmode = Testmode.OVERALL

overall_prefix = 'eval/overall_times/'
precise_times_prefix = 'eval/precise_times/'
memory_prefix = 'eval/memory/'
network_prefix = 'eval/network/'
precise_times_functions_prefix = 'eval/precise_times_functions/'
temp_files = ['Seller/pubkey.txt', 'Seller/enc_sum.txt', 'Seller/randoms.txt', 'Seller/random1.txt', 'Seller/blindedprices.txt',
              'ThirdParty/buyer_vals.txt', 'ThirdParty/seller_vals.txt', 'ThirdParty/seller_completion.txt', 'ThirdParty/pubkey.txt', 'finished.txt']

additional_files = ['Buyer/pubkey.txt', 'Buyer/privkey.txt', 'Buyer/encryptions.txt']

timing_files = ['starttimes.txt', 'endtimes.txt', 'starttimes_distribute_encryption.txt',
                    'endtimes_distribute_encryption.txt', 'starttimes_evaluate_result.txt', 'endtimes_evaluate_result.txt', 'starttimes_beginPaillier.txt', 'endtimes_beginPaillier.txt',
                    'starttimes_store_buyervalues.txt', 'endtimes_store_buyervalues.txt', 'starttimes_deblind_result.txt', 'endtimes_deblind_result.txt',
                'starttimes_store_seller_data.txt', 'endtimes_store_seller_data.txt', 'starttimes_store_buyer_data.txt', 'endtimes_store_buyer_data.txt']

network_eval_files = ['thirdparty_send_time.txt', 'thirdparty_send_size.txt', 'buyer_send_to_thirdparty_time.txt', 'buyer_send_to_thirdparty_size.txt', 'buyer_send_to_seller_size.txt',
                 'buyer_send_to_seller_time.txt', 'seller_send_to_buyer_result_size.txt', 'seller_send_to_buyer_result_time.txt',
                 'seller_send_to_thirdparty_size.txt', 'seller_send_to_thirdparty_time.txt',
                 'seller_send_to_buyer_start_size.txt', 'seller_send_to_buyer_start_time.txt']

memory_files = ['beginPaillier.log', 'store_buyervalues.log', 'deblind_result.log',
                 'distribute_encryption.log', 'evaluate_result.log',
                'store_seller_data.log', 'store_buyer_data.log']

########################################################################
##
## Configure the evaluation:
##  Configure either (i) Performance or (ii) Real-World Performance
##
########################################################################

# Performance Measurements (below)
max_nums = [5000, 10000, 50000, 100000, 500000, 1000000]
configs = [10]

# Real-World Performance Measurements (below)
# Comment for Performance Measurements
max_nums = [38880, 944784]
configs = [1]

number_of_runs = 10
########################################################################


def getMaxNumItems():
    return max_num_items

def create_buyer_config():
    """
    create config with config size many 1s indicating item is needed
    rest 0s indicating item not wanted
    :return:
    """
    with open('Buyer/config.txt', 'w+') as f:
        for i in range(config_size):
            f.write('%s\n' % 1)
        for i in range(max_num_items-config_size):
            f.write('%s\n' % 0)


def create_seller_prices():
    with open('Seller/prices.txt', 'w+') as f:
        for i in range(max_num_items):
            f.write('%s\n' % random.randrange(2, 2**32))


def set_treshold():
    with open('Buyer/threshold.txt', 'w+') as f:
        f.write('%s\n' % (config_size*(2**33)))


def create_all(max_num, config):
    global max_num_items
    max_num_items = max_num
    global config_size
    config_size = config
    create_buyer_config()
    create_seller_prices()
    set_treshold()


def remove_intermediate_files():
    for f in temp_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            print('file', f, 'not found')


def remove_all_files():
    remove_intermediate_files()
    for f in additional_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            print('File %s not found' % f)
    for f in network_eval_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            print('File %s not found' % f)

    for f in timing_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            print('File %s not found' % f)

if __name__ == '__main__':
    # wait for system to start
    print('Removing old values')
    remove_all_files()
    try:
        os.remove('Buyer/encryptions.txt')
    except FileNotFoundError:
        print('File encryptions.txt not found')
    print('Waiting for system to start...')
    time.sleep(30)
    print('system should run now')
    for n in max_nums:
        for c in configs:
            print('Evaluating for %s items' % n)
            create_all(n, c)
            for i in range(number_of_runs):
                # start
                requests.post('http://' + os.environ['SELLER_FRONTEND_ADDRESS'] + ':' + os.environ['SELLER_FRONTEND_PORT'] + '/start_paillier', json=json.dumps(dict()))

                # check if finished
                while not os.path.exists("finished.txt"):
                    time.sleep(5)
                remove_intermediate_files()
                if True:
                    for f in memory_files:
                        changes = []
                        with open(f, 'r') as fd:
                            # fd.readline()
                            # fd.readline()
                            # fd.readline()
                            # fd.readline()
                            lines = fd.readlines()

                            for l in lines:
                                vals = l.split('   ')
                                if len(vals)>2 and vals[2]:
                                    changes.append(vals[2].strip())
                        with open(memory_prefix + f[:-4] + '_items_' + str(n) + '_conf_' + str(c) + '_' + str(datetime.datetime.now())[:19].replace(":", "_") + '.log', 'w+') as out:
                            for val in changes:
                                out.write('%s\n' % val)
                        os.remove(f)
                if True:
                    f = 'network_measurements.log'
                    shutil.copy(f, (network_prefix + f[:-4] + '_items_' + str(n) + '_conf_' + str(c) + '_' + str(datetime.datetime.now())[:19].replace(":", "_") + '.log'))
                    try:
                        os.remove(f)
                    except FileNotFoundError:
                        pass

            now = str(datetime.datetime.now())[:19]
            now = now.replace(":", "_")
            if True:
                # calculate times:
                start_times = []
                with open('starttimes.txt', 'r') as f:
                    for l in f:
                        start_times.append(float(l[:-1]))
                end_times = []
                with open('endtimes.txt', 'r') as f:
                    for l in f:
                        end_times.append(float(l[:-1]))
                assert(len(start_times) == len(end_times))
                runtimes = [e-s for e, s in zip(end_times, start_times)]
                avg = (sum(runtimes)/len(runtimes))
                print(runtimes)
                print('AVG: ', avg)
                # store values
                with open(overall_prefix+'Runtime_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + str(now) + '.txt', 'w+') as f:
                    for r in runtimes:
                        f.write('%s\n' % r)
            if True:
                # calculate times for buyer
                start_times_distribution = []
                with open('starttimes_distribute_encryption.txt', 'r') as f:
                    for l in f:
                        start_times_distribution.append(float(l[:-1]))
                end_times_distribution = []
                with open('endtimes_distribute_encryption.txt', 'r') as f:
                    for l in f:
                        end_times_distribution.append(float(l[:-1]))
                assert(len(start_times_distribution) == len(end_times_distribution))
                runtimes_distribution = [e-s for e, s in zip(end_times_distribution, start_times_distribution)]
                with open(precise_times_functions_prefix+'Runtime_Buyer_distribute_encryption_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_distribution:
                        f.write('%s\n' % r)
                start_times_eval = []
                with open('starttimes_evaluate_result.txt', 'r') as f:
                    for l in f:
                        start_times_eval.append(float(l[:-1]))
                end_times_eval = []
                with open('endtimes_evaluate_result.txt', 'r') as f:
                    for l in f:
                        end_times_eval.append(float(l[:-1]))
                assert(len(start_times_eval) == len(end_times_eval))
                runtimes_eval = [e-s for e, s in zip(end_times_eval, start_times_eval)]
                with open(precise_times_functions_prefix+'Runtime_Buyer_evaluate_result_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_eval:
                        f.write('%s\n' % r)
                runtimes_buyer = [d+e for d,e in zip(runtimes_distribution, runtimes_eval)]
                avg_buyer = (sum(runtimes_buyer)/len(runtimes_buyer))
                
                # store buyer times
                # store values
                with open(precise_times_prefix+'Runtime_Buyer_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_buyer:
                        f.write('%s\n' % r)
                    
                # calculate times for seller
                start_times_begin = []
                with open('starttimes_beginPaillier.txt', 'r') as f:
                    for l in f:
                        start_times_begin.append(float(l[:-1]))
                end_times_begin = []
                with open('endtimes_beginPaillier.txt', 'r') as f:
                    for l in f:
                        end_times_begin.append(float(l[:-1]))
                assert (len(start_times_begin) == len(end_times_begin))
                runtimes_begin = [e - s for e, s in zip(end_times_begin, start_times_begin)]
                with open(precise_times_functions_prefix+'Runtime_Seller_beginPaillier_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_begin:
                        f.write('%s\n' % r)
                start_times_store = []
                with open('starttimes_store_buyervalues.txt', 'r') as f:
                    for l in f:
                        start_times_store.append(float(l[:-1]))
                end_times_store = []
                with open('endtimes_store_buyervalues.txt', 'r') as f:
                    for l in f:
                        end_times_store.append(float(l[:-1]))
                assert (len(start_times_store) == len(end_times_store))
                runtimes_store = [e - s for e, s in zip(end_times_store, start_times_store)]
                with open(precise_times_functions_prefix+'Runtime_Seller_store_buyervalues_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_store:
                        f.write('%s\n' % r)
                start_times_result = []
                with open('starttimes_deblind_result.txt', 'r') as f:
                    for l in f:
                        start_times_result.append(float(l[:-1]))
                end_times_result = []
                with open('endtimes_deblind_result.txt', 'r') as f:
                    for l in f:
                        end_times_result.append(float(l[:-1]))
                assert (len(start_times_result) == len(end_times_result))
                runtimes_result = [e - s for e, s in zip(end_times_result, start_times_result)]

                with open(precise_times_functions_prefix+'Runtime_Seller_deblind_result_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_result:
                        f.write('%s\n' % r)
                intermed_runtimes_seller = [b+s for b,s in zip(runtimes_begin, runtimes_store)]
                runtimes_seller = [i+r for i,r in zip(intermed_runtimes_seller, runtimes_result)]
                avg_seller = (sum(runtimes_seller)/len(runtimes_seller))
                # store seller times
                # store values
                with open(precise_times_prefix+'Runtime_Seller_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_seller:
                        f.write('%s\n' % r)

                # calculate times for third party
                start_times_storeseller = []
                with open('starttimes_store_seller_data.txt', 'r') as f:
                    for l in f:
                        start_times_storeseller.append(float(l[:-1]))
                end_times_storeseller = []
                with open('endtimes_store_seller_data.txt', 'r') as f:
                    for l in f:
                        end_times_storeseller.append(float(l[:-1]))
                assert (len(start_times_storeseller) == len(end_times_storeseller))
                runtimes_storeseller = [e - s for e, s in zip(end_times_storeseller, start_times_storeseller)]

                with open(precise_times_functions_prefix + 'Runtime_ThirdParty_store_seller_data_Productsize' + str(
                        max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_storeseller:
                        f.write('%s\n' % r)

                start_times_storebuyer = []
                with open('starttimes_store_buyer_data.txt', 'r') as f:
                    for l in f:
                        start_times_storebuyer.append(float(l[:-1]))
                end_times_storebuyer = []
                with open('endtimes_store_buyer_data.txt', 'r') as f:
                    for l in f:
                        end_times_storebuyer.append(float(l[:-1]))
                assert (len(start_times_storebuyer) == len(end_times_storebuyer))
                runtimes_storebuyer = [e - s for e, s in zip(end_times_storebuyer, start_times_storebuyer)]

                with open(precise_times_functions_prefix + 'Runtime_ThirdParty_store_buyer_data_Productsize' + str(
                        max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_storebuyer:
                        f.write('%s\n' % r)

                runtimes_thirdparty =[s+b for s,b in zip(runtimes_storeseller, runtimes_storeseller)]
                avg_thirdparty = (sum(runtimes_thirdparty)/len(runtimes_thirdparty))
                # store values
                with open(
                        precise_times_prefix+'Runtime_ThirdParty_Productsize' + str(max_num_items) + '_Configsize_' + str(config_size) + '_' + str(now) + '.txt',
                        'w+') as f:
                    for r in runtimes_thirdparty:
                        f.write('%s\n' % r)


            remove_all_files()

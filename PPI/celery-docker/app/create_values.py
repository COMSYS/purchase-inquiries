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

initial_files = ['Seller/input.txt', 'Seller/prices.pkl', 'privkey.pem',
                 'Buyer/input.txt', 'Buyer/prices.pkl']

intermed_files = ['Buyer/bloom.pkl', 'Buyer/pubkey.txt', 'Buyer/random_factors.pkl',
                  'Seller/signed_set.txt',
                  'ThirdParty/buyerdata.pkl',
                  'finished.txt']

overall_timing_files = ['starttimes.txt', 'endtimes.txt']

function_names = ['beginPSI', 'checkcontainment', 'construct_blinds', 'handle_buyer', 'handle_seller', 'send_ore', 'sign_blinds']

precise_timing_files = ['starttimes_' + fn + '.txt' for fn in function_names] + ['endtimes_' +fn + '.txt' for fn in function_names]

memory_files = [fn + '.log' for fn in function_names]

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

def remove_intermed_files():
    for f in intermed_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            print('File %s not found' % f)


def remove_all_files():
    for l in (initial_files, intermed_files, overall_timing_files, precise_timing_files, memory_files):
        for f in l:
            try:
                os.remove(f)
            except FileNotFoundError:
                print('File %s not found' % f)


def create_seller_ids(size):
    ids = []
    for i in range(1, size):
        ids.append(i)

    with open("Seller/input.txt", "w+") as file:
        file.writelines(["%s\n" % item for item in ids])


def create_seller_prices():
    # load ids
    ids = []
    with open('Seller/input.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            ids.append(int(currentPlace))
    prices = dict()
    for id in ids:
        prices[str(id)] = random.randrange(2, 2**32)
    a_file = open("Seller/prices.pkl", "wb")
    pickle.dump(prices, a_file)
    a_file.close()



def create_buyer_ids(conf):
    ids = []
    for i in range(1, conf):
        ids.append(i)
    with open("Buyer/input.txt", "w+") as file:
        file.writelines(["%s\n" % item for item in ids])


def create_buyer_prices():
    # load ids
    ids = []
    with open('Buyer/input.txt', 'r') as filehandle:
        for line in filehandle:
            # remove linebreak which is the last character of the string
            currentPlace = line[:-1]

            # add item to the list
            ids.append(int(currentPlace))
    prices = dict()
    for id in ids:
            prices[str(id)] = random.randrange(2**33, 2 ** 34)
    a_file = open("Buyer/prices.pkl", "wb")
    pickle.dump(prices, a_file)
    a_file.close()



if __name__ == '__main__':
    time.sleep(20)
    print('System should run now')
    remove_all_files()
    for n in max_nums:
        for c in configs:
            remove_all_files()
            create_seller_ids(n)
            create_seller_prices()
            create_buyer_ids(c)
            create_buyer_prices()
            for i in range(number_of_runs):
                # start calculation
                requests.post('http://' + os.environ['SELLER_FRONTEND_ADDRESS'] + ':' + os.environ['SELLER_FRONTEND_PORT'] + '/begin', json=json.dumps(dict()))

                # check if finished
                while not os.path.exists("finished.txt"):
                    time.sleep(5)
                remove_intermed_files()
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
                assert (len(start_times) == len(end_times))
                runtimes = [e - s for e, s in zip(end_times, start_times)]
                avg = (sum(runtimes) / len(runtimes))
                print(runtimes)
                print('AVG: ', avg)
                # store values
                with open(overall_prefix + 'Runtime_Productsize' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes:
                        f.write('%s\n' % r)

            if True:
                # calculate times for buyer
                start_times_distribution = []
                with open('starttimes_construct_blinds.txt', 'r') as f:
                    for l in f:
                        start_times_distribution.append(float(l[:-1]))
                end_times_distribution = []
                with open('endtimes_construct_blinds.txt', 'r') as f:
                    for l in f:
                        end_times_distribution.append(float(l[:-1]))
                assert (len(start_times_distribution) == len(end_times_distribution))
                runtimes_distribution = [e - s for e, s in zip(end_times_distribution, start_times_distribution)]
                with open(precise_times_functions_prefix + 'Runtime_Buyer_construct_blinds_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_distribution:
                        f.write('%s\n' % r)

                start_times_eval = []
                with open('starttimes_checkcontainment.txt', 'r') as f:
                    for l in f:
                        start_times_eval.append(float(l[:-1]))
                end_times_eval = []
                with open('endtimes_checkcontainment.txt', 'r') as f:
                    for l in f:
                        end_times_eval.append(float(l[:-1]))
                assert (len(start_times_eval) == len(end_times_eval))
                runtimes_eval = [e - s for e, s in zip(end_times_eval, start_times_eval)]
                with open(precise_times_functions_prefix + 'Runtime_Buyer_checkcontainment_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_eval:
                        f.write('%s\n' % r)

                runtimes_buyer = [d + e for d, e in zip(runtimes_distribution, runtimes_eval)]
                avg_buyer = (sum(runtimes_buyer) / len(runtimes_buyer))

                # store buyer times
                # store values
                with open(
                        precise_times_prefix + 'Runtime_Buyer_Productsize' + str(n) + '_Configsize_' + str(
                                c) + '_' + str(now) + '.txt',
                        'w+') as f:
                    for r in runtimes_buyer:
                        f.write('%s\n' % r)

                # calculate times for seller
                start_times_begin = []
                with open('starttimes_beginPSI.txt', 'r') as f:
                    for l in f:
                        start_times_begin.append(float(l[:-1]))
                end_times_begin = []
                with open('endtimes_beginPSI.txt', 'r') as f:
                    for l in f:
                        end_times_begin.append(float(l[:-1]))
                assert (len(start_times_begin) == len(end_times_begin))
                runtimes_begin = [e - s for e, s in zip(end_times_begin, start_times_begin)]
                with open(precise_times_functions_prefix + 'Runtime_Seller_beginPSI_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_begin:
                        f.write('%s\n' % r)
                start_times_store = []
                with open('starttimes_sign_blinds.txt', 'r') as f:
                    for l in f:
                        start_times_store.append(float(l[:-1]))
                end_times_store = []
                with open('endtimes_sign_blinds.txt', 'r') as f:
                    for l in f:
                        end_times_store.append(float(l[:-1]))
                assert (len(start_times_store) == len(end_times_store))
                runtimes_store = [e - s for e, s in zip(end_times_store, start_times_store)]
                with open(precise_times_functions_prefix + 'Runtime_Seller_sign_blinds_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_store:
                        f.write('%s\n' % r)
                start_times_result = []
                with open('starttimes_send_ore.txt', 'r') as f:
                    for l in f:
                        start_times_result.append(float(l[:-1]))
                end_times_result = []
                with open('endtimes_send_ore.txt', 'r') as f:
                    for l in f:
                        end_times_result.append(float(l[:-1]))
                assert (len(start_times_result) == len(end_times_result))
                runtimes_result = [e - s for e, s in zip(end_times_result, start_times_result)]
                with open(precise_times_functions_prefix + 'Runtime_Seller_send_ore_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_result:
                        f.write('%s\n' % r)
                intermed_runtimes_seller = [b + s for b, s in zip(runtimes_begin, runtimes_store)]
                runtimes_seller = [i + r for i, r in zip(intermed_runtimes_seller, runtimes_result)]
                avg_seller = (sum(runtimes_seller) / len(runtimes_seller))
                # store seller times
                # store values
                with open(precise_times_prefix + 'Runtime_Seller_Productsize_' + str(
                        n) + '_Configsize_' + str(c) + '_' + str(now) + '.txt',
                          'w+') as f:
                    for r in runtimes_seller:
                        f.write('%s\n' % r)

                # calculate times for third party
                start_times_handle_buyer = []
                with open('starttimes_handle_buyer.txt', 'r') as f:
                    for l in f:
                        start_times_handle_buyer.append(float(l[:-1]))
                end_times_storeseller = []
                with open('endtimes_handle_buyer.txt', 'r') as f:
                    for l in f:
                        end_times_storeseller.append(float(l[:-1]))
                assert (len(start_times_handle_buyer) == len(end_times_storeseller))
                runtimes_storeseller = [e - s for e, s in zip(end_times_storeseller, start_times_handle_buyer)]
                with open(precise_times_functions_prefix + 'Runtime_ThirdParty_handle_buyer_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_storeseller:
                        f.write('%s\n' % r)
                start_times_handle_seller = []
                with open('starttimes_handle_seller.txt', 'r') as f:
                    for l in f:
                        start_times_handle_seller.append(float(l[:-1]))
                end_times_handle_seller = []
                with open('endtimes_handle_seller.txt', 'r') as f:
                    for l in f:
                        end_times_handle_seller.append(float(l[:-1]))
                assert (len(start_times_handle_seller) == len(end_times_handle_seller))
                runtimes_storebuyer = [e - s for e, s in zip(end_times_handle_seller, start_times_handle_seller)]
                with open(precise_times_functions_prefix + 'Runtime_ThirdParty_handle_seller_Productsize_' + str(n) + '_Configsize_' + str(
                        c) + '_' + str(now) + '.txt', 'w+') as f:
                    for r in runtimes_storebuyer:
                        f.write('%s\n' % r)
                runtimes_thirdparty = [s + b for s, b in zip(runtimes_storeseller, runtimes_storeseller)]
                avg_thirdparty = (sum(runtimes_thirdparty) / len(runtimes_thirdparty))
                # store values
                with open(
                        precise_times_prefix + 'Runtime_ThirdParty_Productsize' + str(
                            n) + '_Configsize_' + str(c) + '_' + str(now) + '.txt',
                        'w+') as f:
                    for r in runtimes_thirdparty:
                        f.write('%s\n' % r)
            remove_all_files()

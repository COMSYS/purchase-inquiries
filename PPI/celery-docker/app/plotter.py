import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from scipy.stats import skewnorm
import scipy.stats as scp
import os

buyer_functions = ["construct_blinds_", "checkcontainment_"]
seller_functions = ["beginPSI_", "sign_blinds_", "send_ore_"]
thirdparty_functions = ["handle_buyer_", "handle_seller_"]

numbersize = 12
headlinesize = 18

def forward(x):
    return x/60

def backward(x):
    return x*60

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scp.sem(a)
    h = se * scp.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


def overall_time_plot(sizes=[50], configsize=10):
    plt.rcParams['figure.figsize'] = (5.9,5.9)
    # 1000 AVG: 60.5962690114975
    # 5000 AVG: 139.3494766553243
    # 10000 AVG: 272.89529665311176
    meansList = []
    confList = []
    folder = "eval/overall_times/"
    prefix = "Runtime_Productsize"
    # load all files
    print(os.listdir(folder))
    for size in sizes:
        files = [f for f in os.listdir(folder) if
                 os.path.isfile(folder+f) and (prefix + str(size) + "_" in f) and ("Configsize_" + str(configsize) + "_" in f)]
        values = []
        for f in files:
            with open(folder + f, 'r') as input:
                for l in input:
                    values.append(float(l[:-1]))

        mid, lb, ub = mean_confidence_interval(values)
        meansList.append(mid)
        confList.append([lb, ub])

        fileList = []
    # given some mean values and their confidence intervals,
    means = np.array(meansList)
    conf = np.array(confList)
    if (len(means) == 0 or len(conf) == 0):
        return
    # calculate the error
    yerr = np.c_[means - conf[:, 0], conf[:, 1] - means].T

    # and plot it on a bar chart
    ax = plt.subplot(111)
    ax.yaxis.grid(True, which='major', linestyle=':')
    fig = ax.bar(range(len(means)), means, yerr=yerr, tick_label=sizes)
    plt.xticks(range(len(means)), fontsize=12)
    plt.yticks(fontsize=12)
    secax = ax.secondary_yaxis('right', functions=(forward,backward))
    secax.set_ylabel('Runtime [min]', fontsize=18)
    # plt.xticks(sizes)
    plt.xlabel('Size of product catalog', fontsize=18)
    # plt.title('Overall Runtime with ' + str(configsize) + " configuration size", fontsize=20)
    plt.ylabel('Runtime [s]', fontsize=18)
    print("successfully created overall plot")
    plt.savefig('overall_times_ppi.pdf', bbox_inches="tight")
    plt.clf()

def precise_time_plot(sizes=[50], configsize=10):
    meansListBuyer = []
    confListBuyer = []
    meansListSeller = []
    confListSeller = []
    meansListThirdParty = []
    confListThirdParty = []
    folder = "eval/precise_times/"
    buyer_prefix = "Runtime_Buyer_Productsize"
    seller_prefix = "Runtime_Seller_Productsize_"
    third_party_prefix = "Runtime_ThirdParty_Productsize"
    # load all files
    fileList = os.listdir(folder)
    for size in sizes:
        filesBuyer = [f for f in fileList if
                      os.path.isfile(folder+f) and (buyer_prefix + str(size) + "_" in f) and ("Configsize_" + str(configsize) + "_" in f)]
        filesSeller = [f for f in fileList if
                       os.path.isfile(folder+f) and (seller_prefix + str(size) + "_" in f) and ("Configsize_" + str(configsize) + "_" in f)]
        filesThirdParty = [f for f in fileList if
                           os.path.isfile(folder+f) and (third_party_prefix + str(size) + "_" in f) and (
                                       "Configsize_" + str(configsize) + "_" in f)]
        vals = []
        for f in filesBuyer:

            with open(folder + f, 'r') as input:
                values = [float(i[:-1]) for i in input.readlines()]
                for v in values:
                    vals.append(v)

        mid, lb, ub = mean_confidence_interval(vals)
        meansListBuyer.append(mid)
        confListBuyer.append([lb, ub])

        vals = []
        for f in filesSeller:

            with open(folder + f, 'r') as input:
                values = [float(i[:-1]) for i in input.readlines()]
                for v in values:
                    vals.append(v)
                    vals.append(v)
        mid, lb, ub = mean_confidence_interval(vals)
        meansListSeller.append(mid)
        confListSeller.append([lb, ub])
        vals = []
        for f in filesThirdParty:

            with open(folder + f, 'r') as input:
                values = [float(i[:-1]) for i in input.readlines()]
                for v in values:
                    vals.append(v)
                    vals.append(v)
        mid, lb, ub = mean_confidence_interval(vals)
        meansListThirdParty.append(mid)
        confListThirdParty.append([lb, ub])

    # given some mean values and their confidence intervals,
    meansBuyer = np.array(meansListBuyer)
    confBuyer = np.array(confListBuyer)
    meansSeller = np.array(meansListSeller)
    confSeller = np.array(confListSeller)
    meansThirdParty = np.array(meansListThirdParty)
    confThirdParty = np.array(confListThirdParty)


    # calculate the error
    yerrBuyer = np.c_[meansBuyer - confBuyer[:, 0], confBuyer[:, 1] - meansBuyer].T
    yerrSeller = np.c_[meansSeller - confSeller[:, 0], confSeller[:, 1] - meansSeller].T
    yerrThirdParty = np.c_[meansThirdParty - confThirdParty[:, 0], confThirdParty[:, 1] - meansThirdParty].T
    ax = plt.subplot(111)
    w = 0.3
    if len(meansBuyer) != 0:
        ax.bar([x - w for x in range(len(meansBuyer))], meansBuyer, yerr=yerrBuyer,  width=w,
               color='b', align='center')
    if len(meansSeller) != 0:
        ax.bar(range(len(meansSeller)), meansSeller, yerr=yerrSeller, width=w, color='g',
               align='center')
    if len(meansThirdParty) != 0:
        ax.bar([x + w for x in range(len(meansThirdParty))], meansThirdParty, yerr=yerrThirdParty,
               width=w, color='r', align='center')
    ax.legend(('Buyer', 'Seller', 'ECP'))
    ax.autoscale(tight=True)
    ax.set_xticks( np.arange(len(sizes)))
    ax.set_xticklabels(sizes)
    print("successfully created precise plot")
    plt.savefig('precise_times_configsize_' + str(configsize) + ' .pdf')
    plt.clf()

def network_plots(sizes=[50], configsize=10):
    plt.rcParams['figure.figsize'] = (5.9,5.9)
    seller_funcs = ["beginPSI", "sign_blinds", "send_successful_ore_conversion"]
    buyer_funcs = ["construct_blinds", "start_ore"]
    thirdparty_funcs = ["request_seller", "send_final_response"]
    # find all files for size and configsize
    folder = "eval/network/"
    # load all files
    fileList = os.listdir(folder)
    seller_time_means = []
    seller_data_means = []
    buyer_time_means = []
    buyer_data_means = []
    thirdparty_time_means = []
    thirdparty_data_means = []
    seller_time_confs = []
    seller_data_confs = []
    buyer_time_confs = []
    buyer_data_confs = []
    thirdparty_time_confs = []
    thirdparty_data_confs = []
    for size in sizes:
        files = [f for f in fileList if
                      os.path.isfile(folder + f) and ("items_" +str(size)+"_" in f) and ("conf_"+ str(configsize) + "_" in f)]

        lines = []
        seller_times = []
        buyer_times = []
        third_party_times = []
        seller_data = []
        buyer_data = []
        thirdparty_data = []
        for f in files:
            temp_seller = []
            temp_buyer = []
            temp_third = []
            temp_seller_d = []
            temp_buyer_d = []
            temp_third_d  = []
            with open(folder+f, 'r') as file:
                for l in file:
                    line = l.split(', ')
                    line[3] = line[3][:-1]
                    lines.append(line)
                    if line[3] in seller_funcs:
                        temp_seller.append(float(line[1])-float(line[0]))
                        temp_seller_d.append(int(line[2])/1000)
                    elif line[3] in buyer_funcs:
                        temp_buyer.append(float(line[1]) - float(line[0]))
                        temp_buyer_d.append(int(line[2]) / 1000)
                        print("Size "+ str(size) + "add " + str(float(line[1])-float(line[0])) + " to Buyer as func " + line[3])
                    elif line[3] in thirdparty_funcs:
                        temp_third.append(float(line[1]) - float(line[0]))
                        temp_third_d.append(int(line[2]) / 1000)
                seller_times.append(sum(temp_seller))
                buyer_times.append(sum(temp_buyer))
                print("Size "+ str(size) + "Overall buyertime for this file " +str(sum(temp_buyer)))
                third_party_times.append(sum(temp_third))
                seller_data.append(sum(temp_seller_d))
                buyer_data.append(sum(temp_buyer_d))
                thirdparty_data.append(sum(temp_third_d))


        m, l, u = mean_confidence_interval(seller_data)
        seller_data_means.append(m)
        seller_data_confs.append([l,u])
        m, l, u = mean_confidence_interval(seller_times)
        seller_time_means.append(m)
        seller_time_confs.append([l, u])
        m, l, u = mean_confidence_interval(buyer_data)
        buyer_data_means.append(m)
        buyer_data_confs.append([l, u])
        m, l, u = mean_confidence_interval(buyer_times)
        buyer_time_means.append(m)
        buyer_time_confs.append([l, u])
        m, l, u = mean_confidence_interval(thirdparty_data)
        thirdparty_data_means.append(m)
        thirdparty_data_confs.append([l, u])
        m, l, u = mean_confidence_interval(third_party_times)
        thirdparty_time_means.append(m)
        thirdparty_time_confs.append([l, u])



    # given some mean values and their confidence intervals,
    meansBuyer = np.array(buyer_time_means)
    confBuyer = np.array(buyer_time_confs)
    meansSeller = np.array(seller_time_means)
    confSeller = np.array(seller_time_confs)
    meansThirdparty = np.array(thirdparty_time_means)
    confThirdparty = np.array(thirdparty_time_confs)

    # calculate the error
    yerrBuyer = np.c_[meansBuyer - confBuyer[:, 0], confBuyer[:, 1] - meansBuyer].T
    yerrSeller = np.c_[meansSeller - confSeller[:, 0], confSeller[:, 1] - meansSeller].T
    yerrThirdparty = np.c_[meansThirdparty - confThirdparty[:, 0], confThirdparty[:, 1] - meansThirdparty].T
    ax = plt.subplot(111)
    w = 0.3
    width = w*0.9
    if len(meansBuyer) != 0:
        ax.bar([x -w for x in range(len(meansBuyer))], meansBuyer, yerr=yerrBuyer, width=width,
               color='b', align='center')
    if len(meansSeller) != 0:
        ax.bar([x  for x in range(len(meansSeller))], meansSeller, yerr=yerrSeller, width=width, color='g',
               align='center')
    if len(meansThirdparty) != 0:
        ax.bar([x +w for x in range(len(meansThirdparty))], meansThirdparty, yerr=yerrThirdparty, width=width,
                align='center')
    ax.legend(('Buyer', 'Seller', 'ECP'))
    #ax.autoscale(tight=True)
    ax.set_xticks(np.arange(len(sizes)))
    ax.set_xticklabels(sizes)
    ax.yaxis.grid(True, which='major', linestyle=':')
    #ax.set_yscale('log')
    plt.xticks(fontsize=numbersize)
    plt.yticks(fontsize=numbersize)
    plt.xlabel('Size of product catalog', fontsize=headlinesize)
    #plt.title('Network sending time per Party with ' + str(configsize) + " configuration size", fontsize=headlinesize)
    plt.ylabel('Sending time [s]', fontsize=headlinesize)
    print("successfully created Network time plot")
    plt.savefig('eval_network_times_ppi.pdf', bbox_inches="tight")
    plt.clf()

    # given some mean values and their confidence intervals,
    meansBuyer = np.array(buyer_data_means)
    confBuyer = np.array(buyer_data_confs)
    meansSeller = np.array(seller_data_means)
    confSeller = np.array(seller_data_confs)
    meansThirdparty = np.array(thirdparty_data_means)
    confThirdparty = np.array(thirdparty_data_confs)
    # calculate the error
    yerrBuyer = np.c_[meansBuyer - confBuyer[:, 0], confBuyer[:, 1] - meansBuyer].T
    yerrSeller = np.c_[meansSeller - confSeller[:, 0], confSeller[:, 1] - meansSeller].T
    yerrThirdparty = np.c_[meansThirdparty - confThirdparty[:, 0], confThirdparty[:, 1] - meansThirdparty].T
    ax = plt.subplot(111)
    w = 0.3
    width = w * 0.9
    if len(meansBuyer) != 0:
        ax.bar([x - w for x in range(len(meansBuyer))], meansBuyer, yerr=yerrBuyer, width=width,
               color='b', align='center')
    if len(meansSeller) != 0:
        ax.bar([x for x in range(len(meansSeller))], meansSeller, yerr=yerrSeller, width=width, color='g',
               align='center')
    if len(meansThirdparty) != 0:
        ax.bar([x + w for x in range(len(meansThirdparty))], meansThirdparty, yerr=yerrThirdparty, width=width,
                align='center')
    ax.legend(('Buyer', 'Seller', 'ECP'), fontsize=8)
    # ax.autoscale(tight=True)
    ax.set_xticks(np.arange(len(sizes)))
    ax.set_xticklabels(sizes)
    ax.yaxis.grid(True, which='major', linestyle=':')
    plt.xticks(fontsize=numbersize)
    plt.yticks(fontsize=numbersize)
    ax.set_yscale('log')
    plt.xlabel('Size of product catalog', fontsize=headlinesize)
    #plt.title('Amount of transferred data per Party with ' + str(configsize) + " configuration size", fontsize=headlinesize)
    plt.ylabel('Amount of data [KB]', fontsize=headlinesize)
    print("successfully created Network data plot")
    plt.savefig('eval_network_data_ppi.pdf', bbox_inches="tight")
    plt.clf()


def stacked_party_plot(sizes=[50], configsize=10):
    plt.rcParams['figure.figsize'] = (5.9, 2.95)
    folder = "eval/precise_times_functions/"
    buyer_prefix = "Runtime_Buyer_"
    seller_prefix = "Runtime_Seller_"
    thirdparty_prefix = "Runtime_ThirdParty_"
    prod = "Productsize"
    # load all files
    fileList = os.listdir(folder)
    ax = plt.subplot(111)
    w = 0.2
    wid = w - 0.1 * w
    buyer_bot = [0 * len(sizes)]
    seller_bot = [0 * len(sizes)]
    thirdparty_bot = [0* len(sizes)]
    for fun in buyer_functions + seller_functions + thirdparty_functions:
        meansList = []
        confsList = []
        for size in sizes:
            vals = []
            for file in fileList:
                if (fun in file and "Productsize_" + str(size) + "_" in file and "Configsize_" + str(configsize) + "_" in file):
                    with open(folder + file, 'r') as f:
                        for l in f:
                            vals.append(float(l[:-1]))
            m, lb, ub = mean_confidence_interval(vals)
            meansList.append(m)
            confsList.append([lb, ub])
        means = np.array(meansList)
        conf = np.array(confsList)
        yerr = np.c_[
            means - conf[:, 0],
            conf[:, 1] - means].T
        if len(means) != 0:
            if (fun in buyer_functions):
                ax.bar([x - w for x in range(len(means))], means, yerr=yerr, bottom=buyer_bot,
                       width=wid, align='center')
                buyer_bot = buyer_bot + means
            elif (fun in seller_functions):
                ax.bar([x  for x in range(len(means))], means, yerr=yerr, bottom=seller_bot,
                       width=wid, align='center')
                seller_bot = seller_bot + means
            elif (fun in thirdparty_functions):
                ax.bar([x + w for x in range(len(means))], means, yerr=yerr, bottom=thirdparty_bot,
                       width=wid, align='center')
                thirdparty_bot = thirdparty_bot + means

    legend = []
    for l in buyer_functions:
        legend.append("Buyer: "+l[:-1])
    for l in seller_functions:
        legend.append("Seller: "+l[:-1])
    for l in thirdparty_functions:
        legend.append("ECP: "+l[:-1])
    #legend = buyer_functions + seller_functions +thirdparty_functions
    ax.legend(legend, fontsize=6)
    box = ax.get_position()
    #ax.set_position([box.x0, box.y0, box.width * 1, box.height])
    ax.set_xticks(np.arange(len(sizes)))
    ax.set_xticklabels(sizes)
    ax.set_yscale('log')
    ax.yaxis.grid(True, which='major', linestyle=':')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    plt.xlabel('Size of product catalog', fontsize=8)
    #plt.title('Stacked function runtime per Party with ' + str(configsize) + " configuration size", fontsize=headlinesize)
    plt.ylabel('Runtime [s]', fontsize=8)
    print("successfully created Runtimes per Party usage stacked plot")
    plt.savefig('eval_runtime_per_party_ppi.pdf', bbox_inches="tight")
    plt.clf()


def ram_usage_plot(sizes=[50], configsize=10):
    plt.rcParams['figure.figsize'] = (5.9, 2.95)
    folder = 'eval/memory/'
    fileList = os.listdir(folder)
    ax = plt.subplot(111)
    w = 0.2
    wid = w - 0.2 * w
    buyer_bot = [0*len(sizes)]
    seller_bot = [0 * len(sizes)]
    thirdparty_bot =[0*len(sizes)]
    cur_buyer_means = []
    cur_seller_means = []
    cur_tp_means = []
    cur_buyer_con = []
    cur_seller_con = []
    cur_tp_con = []
    for fun in buyer_functions+ seller_functions+thirdparty_functions:
        meansList = []
        confsList = []
        for size in sizes:
            vals = []
            for file in fileList:
                filevalues = []
                if(fun in file and "items_" + str(size) + "_" in file and "conf_" + str(configsize) + "_" in file ):
                    with open(folder+file, 'r') as f:

                        f.readline()
                        for line in f.readlines():
                            num, unit = line.split(' ')
                            if(unit[:-1] == "MiB"):

                                filevalues.append(float(num)*1.0485)
                            elif(unit[:-1] == "GiB"):
                                filevalues.append(float(num)*1000*1.0485)
                    v = max(filevalues)-filevalues[0]
                    #if(v == 0):
                    #    v = 0.1
                    if(not v==0):
                        vals.append(v)
            m, lb, ub = mean_confidence_interval(vals)
            meansList.append(m)
            confsList.append([lb,ub])
        means = np.array(meansList)
        conf = np.array(confsList)

        yerr = np.c_[
            means - conf[:, 0],
            conf[:, 1] - means].T
        if len(means) != 0:
            if(fun in buyer_functions):
                    if(not cur_buyer_means):
                        cur_buyer_means = meansList
                        cur_buyer_con = confsList
                        b_func = fun
                    elif(max(cur_buyer_means)<max(means)):
                        cur_buyer_means = meansList
                        cur_buyer_con = confsList
                        b_func = fun


            elif(fun in seller_functions):
                if (not cur_seller_means):
                    cur_seller_means = meansList
                    cur_seller_con = confsList
                    s_func = fun
                elif (max(cur_seller_means) < max(means)):
                    cur_seller_means = meansList
                    cur_seller_con = confsList
                    s_func = fun

            elif (fun in thirdparty_functions):
                if (not cur_tp_means):
                    cur_tp_means = meansList
                    cur_tp_con = confsList
                    tp_func = fun
                elif (max(cur_tp_means) < max(means)):
                    cur_tp_means = meansList
                    cur_tp_con = confsList
                    tp_func = fun

    means = np.array(cur_buyer_means)
    conf = np.array(cur_buyer_con)
    yerr = np.c_[
        means - conf[:, 0],
        conf[:, 1] - means].T
    ax.bar([x - w for x in range(len(means))], means, yerr=yerr, width=wid, align='center')
    means = np.array(cur_seller_means)
    conf = np.array(cur_seller_con)
    yerr = np.c_[
        means - conf[:, 0],
        conf[:, 1] - means].T
    ax.bar([x for x in range(len(means))], means, yerr=yerr, width=wid, align='center')
    means = np.array(cur_tp_means)
    conf = np.array(cur_tp_con)
    yerr = np.c_[
        means - conf[:, 0],
        conf[:, 1] - means].T
    ax.bar([x + w for x in range(len(means))], means, yerr=yerr, width=wid, align='center')
    legend = ["Buyer: "+ b_func[:-1]] + ["Seller: "+s_func[:-1]] + ["ECP: "+tp_func[:-1]]
    ax.legend(legend, fontsize=6)
    ax.yaxis.grid(True, which='major', linestyle=':')
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height])
    ax.set_xticks(np.arange(len(sizes)))
    ax.set_xticklabels(sizes)
    ax.set_yscale('log')
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    plt.xlabel('Size of product catalog', fontsize=8)
    #plt.title('Maximum RAM Usage per Party with ' + str(configsize) + " configuration size", fontsize=headlinesize)
    plt.ylabel('RAM Usage [MB]', fontsize=8)
    print("successfully created RAM usage stacked plot")
    plt.savefig('eval_ram_usage_ppi.pdf', bbox_inches="tight")
    plt.clf()

if __name__ == '__main__':
    sizes = [5000, 10000, 50000, 100000, 500000, 1000000]
    overall_time_plot(sizes)
    precise_time_plot(sizes)
    stacked_party_plot(sizes)
    network_plots(sizes)
    ram_usage_plot(sizes)



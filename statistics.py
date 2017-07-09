#!/usr/bin/env python

# File name:            statistics.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
Calculate statistics from processed data

"""
import parse
import plotly
import datetime
import numpy
import pickle
import json
import math
from statsmodels.stats.stattools import medcouple


def peak_detection(list,type, innerFence,outerFence):
    """

    :param list: list of timestamps over which a peak-detection is performed. The size of the list corresponds to the size of the sliding window
    :param type: directory where the the data has to be retrieved
    :param innerFence: numeric value of the inner fence, threshold suspects of medium priority
    :param outerFence: numeric value of the outer fence, threshold suspects of high priority
    :return:
    """
    dictData = {}
    mediumSuspect = []
    highSuspect =[]
    dictMediumSuspect = {}
    dictHighSupstect = {}
    # Make a dictionary from the snapshots
    # Detect an abnormal change in the amount of connecions coming from an Autonomous System
    # or a Provider.
    for i in range(0, len(list), 1):
        date = datetime.datetime.fromtimestamp(list[i]).strftime('%Y-%m-%d_%H_%M_%S')
        try:
            with open('ALL_snaps/'+type+'_snaps/'+type+'_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
                dict = pickle.load(handle)
        except IOError, e:
            return

        for key in dict:
            value = dict[key]
            if key in dictData.keys():
                if len(dictData[key]) == i - 1:
                    dictData[key].append(value)
                else:
                    while len(dictData[key]) < i - 1:
                        dictData[key].append(0)
                    dictData[key].append(value)
            else:
                dictData[key] = []
                for j in range(1, i):
                    dictData[key].append(0)
                dictData[key].append(value)

    # Calculate the standard deviation of the number of connected nodes for each AS or Provider listed in the dictionary
    for key in dictData:
        data = dictData[key]
        deviation = numpy.std(data)

        if deviation > innerFence and deviation < outerFence:
            mediumSuspect.append(key)

        elif deviation >= outerFence:
            highSuspect.append(key)

    for i in range(0, len(list), 1):
        date = datetime.datetime.fromtimestamp(list[i]).strftime('%Y-%m-%d_%H_%M_%S')
        try:
            with open('ALL_snaps/'+type+'_snaps/'+type+'_ip_dict_snapshot_'+ date +'.pickle', 'rb') as handle:
                snap = pickle.load(handle)
        except IOError, e:
            print e
        for key in mediumSuspect:
            if key in dictMediumSuspect.keys():
                dictMediumSuspect[key].append(snap[key])
            else:
                dictMediumSuspect[key]= snap[key]
        for key in highSuspect:
            if key in dictHighSupstect.keys():
                dictHighSupstect[key].append(snap[key])
            else:
                dictHighSupstect[key]= snap[key]

        if dictMediumSuspect:
            with open("Snapshot_Stats/Medium_suspected_"+type +"_"+ date+".txt", "a") as out:
                pickle.dump(dictMediumSuspect, out)
        if dictHighSupstect:
            with open("Snapshot_Stats/High_suspected_"+type +"_"+ date+".txt", "a") as out:
                pickle.dump(dictHighSupstect, out)

    # Find the respective ip-addresses owned by the suspected AS or Organization



def conntime_mean(date,honeyNodeLocation):
    """
    Calculate the average connection time of the peers for the given date. If no date is given,
    calculate the cummulative average connection time of the peers.

    :param date: processing date
    :param honeyNodeLocation: geographic location of the honeynode, used as id
    :return: The average connection time
    """
    connResults = open(honeyNodeLocation+"/ConnectionResults.txt","r+")
    connections = []
    if date == 'x':
        for line in connResults:
           [day,hour,min,sec] = parse.get_connection_time(line)
           conntime = datetime.timedelta(days=int(day),hours=int(hour),minutes=int(min),seconds=int(sec))
           # filter feeler connections
           reason = parse.get_deconnection_reason(line)
           if reason != 'feeler':
               connections.append(conntime)
        mean = sum(connections, datetime.timedelta()) / len(connections)
    else:
        for line in connResults:
            if date in line:
                [day,hour,min,sec] = parse.get_connection_time(line)
                conntime = datetime.timedelta(days=int(day),hours=int(hour),minutes=int(min),seconds=int(sec))
                # filter feeler connections
                reason = parse.get_deconnection_reason(line)
                if reason != 'feeler':
                    connections.append(conntime)
        try:
            mean = sum(connections, datetime.timedelta()) / len(connections)
        except ZeroDivisionError:
            return None
    return mean

def connection_number(date,honeyNodeLocation):
    """

    :param date:
    :param honeyNodeLocation:
    :return:
    """
    connNb = 0
    connResults = open(honeyNodeLocation+"/ConnectionResults.txt", "r+")
    for line in connResults:
        if date in line:
            connNb += 1
    return connNb

# Not relevant due to network congestions and different geographic localisation of the peers
def rtt_mean(date):
    """
    Calculate the average round-trip time of the peers.

    :param date:
    :return:
    """
    with open('Peers/RTTstats_' + date + '.txt', 'rb') as handle:
        rttResults = pickle.load(handle)

    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')
    # filter noise out
    for key in rttResults:
        rtts = rttResults[key]
        for index,pingtime in rtts:
            if pingtime > 0.5:
                rttResults[key][index] = None

    x =[]
    for i in range(0,1000,1):
        x.append(i)

    data = []
    for key in rttResults:
        values = rttResults[key]
        data.append(plotly.graph_objs.Scatter(x=x,y=values, name=key))

    plotly.plotly.plot(data, filename='timestamp_'+date+'')


def adjusted_boxplot_fences():
    """
    Calculate the inner and outer fence of the peak-detection algorithm with used of the adjusted boxplot method for
    skewed data.
    :return: a list of two values. The first value is the inner fence and the second value the outer fence
    """
    dictData = {}
    stdDataSet = []
    window = 5
    timestamps=[]
    xas =[]
    index = 0
    times = open('ALL_snaps/timestamps.txt','r+')
    for line in times:
        timestamps.append(int(line))

    for time in timestamps:
        index = index +1
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d_%H_%M_%S')
        try:
            with open('ALL_snaps/AS_snaps/AS_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
                dict = pickle.load(handle)
            xas.append(time)
        except IOError, e:
            print e
            break

       # for key in dict:
        #    value = dict[key]
         #   if key in dictData.keys():
          #      dictData[key].append(value)
           # else:
            #    dictData[key] = []
             #   dictData[key].append(value)

        for key in dict:
            value = dict[key]
            if key in dictData.keys():
                if len(dictData[key]) == index - 1:
                    dictData[key].append(value)
                else:
                    while len(dictData[key]) < index- 1:
                        dictData[key].append(0)
                    dictData[key].append(value)
            else:
                dictData[key] = []
                for j in range(1, index):
                    dictData[key].append(0)
                dictData[key].append(value)

    data = {}
    for key in dictData:
        values = dictData[key]
        if (numpy.mean(values) > 100) or ((max(values) - min(values)) > 60):
            data[key] =[]
            for index in range(0,len(values)-window-1,1):
                stdDataSet.append(numpy.std(values[index:index+window]))
                data[key].append(numpy.std(values[index:index+window]))


    medc =medcouple(stdDataSet)
    q75, q25 = numpy.percentile(stdDataSet, [75, 25])
    iqr = q75 - q25
    innerFence = q75 + 1.5* math.exp(4*medc)*iqr
    outerFence = q75 + 3*math.exp(4*medc)*iqr
    return [innerFence,outerFence]



def block_delay_mean(date,honeyNodeLocation):
    """
    Compute the average delay between GETDATA and BLOCK messages on a given date. If no date is given, compute the average
    over the entire available data.
    :param date:
    :param honeyNodeLocation:
    :return:
    """
    delayResults = open(honeyNodeLocation+"/BlockDelayResults.txt","r+")
    delays = []
    if date == 'x':
        for line in delayResults:
            [hour, min, sec] = parse.get_delay(line)
            delay = datetime.timedelta(hours=int(hour),minutes=int(min), seconds=int(sec))
            delays.append(delay)
        mean = sum(delays, datetime.timedelta()) / len(delays)
    else:
        for line in delayResults:
            if date in line:
                [hour, min, sec] = parse.get_delay(line)
                delay = datetime.timedelta(hours=int(hour),minutes=int(min), seconds=int(sec))
                delays.append(delay)
        if len(delays) == 0:
            mean = 'x'
        else:
            mean = sum(delays, datetime.timedelta()) / len(delays)
    return mean


def tx_delay_mean(date, honeyNodeLocation):
    """
    Compute the average delay between GETDATA and TX messages on a given date. If no date is given, compute the average
    over the entire available data.
    :param date:
    :param honeyNodeLocation:
    :return:
    """
    delayResults = open(honeyNodeLocation+"/TransactionDelayResults.txt", "r+")
    delays = []
    if date == 'x':
        for line in delayResults:
            [hour, min, sec] = parse.get_delay(line)
            delay = datetime.timedelta(hours=int(hour), minutes=int(min), seconds=int(sec))
            delays.append(delay)
        if len(delays) == 0:
            mean = 'x'
        else:
            mean = sum(delays, datetime.timedelta()) / len(delays)
    else:
        for line in delayResults:
            if date in line:
                [hour, min, sec] = parse.get_delay(line)
                delay = datetime.timedelta(hours=int(hour), minutes=int(min), seconds=int(sec))
                delays.append(delay)
        if len(delays) == 0:
            mean = 'x'
        else:
            mean = sum(delays, datetime.timedelta()) / len(delays)
    return mean

def get_AS_list(timestamp):
    """

    :param timestamp:
    :return:
    """
    date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    with open('AS_snaps/AS_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
        snap = pickle.load(handle)

    AS = sorted(snap.values(),reverse=True)
    nb = sorted(snap,key=snap.get,reverse=True)
    dict = {}
    for i in range(0,10,1):
        dict[AS[i]]=nb[i]
    return dict


def message_list_format(honeyNodeLocation, msgtype):
    """

    :param honeyNodeLocation:
    :param msgtype:
    :return:
    """
    res = honeyNodeLocation+'/'+msgtype+'Results.txt'
    msgResult = open(res, 'r+')
    x = []
    y = []
    dict = {}
    suspect = {}
    for line in msgResult:
        if 'received:'in line:
            date = parse.get_date(line)
            version, ip, port = parse.get_ip_port(line)
            if date not in dict.keys():
                dict[date] = 1
                suspect[date] = {}
                suspect[date] = {ip:1}

            else:
                i = dict[date]
                i = i + 1
                dict[date] = i
                if ip not in suspect[date].keys():
                    suspect[date][ip] = 1
                else:
                    n = suspect[date][ip]
                    n = n+1
                    suspect[date][ip] = n

    for key in sorted(dict):
        x.append(key)
        y.append(dict[key])
    return [x,y,suspect]

def get_conn_nb_list_format(honeyNodeLocation):
    """

    :param honeyNodeLocation:
    :return:
    """
    with open(honeyNodeLocation+'/Dict/dictConnectionNb.txt', 'r') as jsonNb:
        dictNbPeers = json.load(jsonNb)
    x=[]
    y=[]
    for key in sorted(dictNbPeers):
        x.append(key)
        y.append(dictNbPeers[key])
    print x
    return [x,y]


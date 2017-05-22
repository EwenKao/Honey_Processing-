#!/usr/bin/env python

# File name:            stats.py
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
import pandas
import math
from statsmodels.stats.stattools import (omni_normtest, jarque_bera,
                                         durbin_watson, _medcouple_1d, medcouple,
                                         robust_kurtosis, robust_skewness)


def peak_detection(list,type):
    """

    :param list: list of consecutive timestamps, usualyy five, defining the window were the peakdetection is peformes
    :param type:
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
        date = datetime.datetime.fromtimestamp(list[i]).strftime('%Y-%m-%d')
        try:
            with open('AS_snaps/'+type+'_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
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

        if deviation > 22.24 and deviation < 40.19:
            mediumSuspect.append(key)

        elif deviation >= 40.19:
            highSuspect.append(key)

    for i in range(0, len(list), 1):
        date = datetime.datetime.fromtimestamp(list[i]).strftime('%Y-%m-%d')
        try:
            with open(type+'_snaps/'+type+'_ip_dict_snapshot_'+ date +'.pickle', 'rb') as handle:
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



# Calculate the average connection time of the peers
def conntime_mean(date,honeyNodeLocation):
    connResults = open(honeyNodeLocation+"/ConnectionResults.txt","r+")
    connections = []
    if date == 'x':
        for line in connResults:
           [day,hour,min,sec] = parse.get_connection_time(line)
           conntime = datetime.timedelta(days=int(day),hours=int(hour),minutes=int(min),seconds=int(sec))
           # filter freeler connections
           reason = parse.get_deconnection_reason(line)
           if reason != 'feeler':
               connections.append(conntime)
        mean = sum(connections, datetime.timedelta()) / len(connections)
    else:
        for line in connResults:
            if date in line:
                [day,hour,min,sec] = parse.get_connection_time(line)
                conntime = datetime.timedelta(days=int(day),hours=int(hour),minutes=int(min),seconds=int(sec))
                # filter freeler connections
                reason = parse.get_deconnection_reason(line)
                if reason != 'feeler':
                    connections.append(conntime)
        mean = sum(connections, datetime.timedelta()) / len(connections)
    return mean

def connection_number(date,honeyNodeLocation):
    connNb = 0
    connResults = open(honeyNodeLocation+"/ConnectionResults.txt", "r+")
    for line in connResults:
        if date in line:
            connNb += 1
    return connNb


def rtt_mean(date):
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


def stdev_AS_mean():
    dictData = {}
    stdDataSet = []
    time = 1479556800 # 19 oct 2016
    window = 5
    stdList = {}

    while 1:
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        try:
            with open('AS_snaps/AS_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
                dict = pickle.load(handle)
        except IOError, e:
            print e
            break

        time = time+86400

        for key in dict:
            value = dict[key]
            if key in dictData.keys():
                dictData[key].append(value)
            else:
                dictData[key] = []
                dictData[key].append(value)
    tot =0
    for key in dictData:
        values = dictData[key]
        if (numpy.mean(values) > 100) or ((max(values) - min(values)) > 40):
            stdList[key] = []
            for index in range(0,len(values)-window-1,1):
                stdList[key].append(numpy.std(values[index:index+window]))
                stdDataSet.append(numpy.std(values[index:index+window]))
                tot =tot+1
            q75, q25 = numpy.percentile(stdList[key], [75, 25])
            iqr = q75 - q25
            upperLimit = q75+1.5*iqr
            supralimit = q75+3*iqr
            ultraLimit = q75+4.5*iqr
            print 'lowLimit ' + str(upperLimit)
            print 'mediumlimit ' + str(supralimit)
            print 'Highlimit ' + str(ultraLimit)

    medc =medcouple(stdDataSet)
    print 'medcouple ' +str(medc)

    q75, q25 = numpy.percentile(stdDataSet, [75, 25])
    standard = numpy.std(stdDataSet)
    iqr = q75 - q25
    supralimit = q75 + 3* math.exp(4*medc)*iqr
    lowerlimit = q25 - 3*math.exp(3.5*medc)*iqr

    #graph.histogram(stdDataSet)
    #graph.boxplot(stdDataSet)

    print 'skewwed upperlimit ' + str(supralimit)
    print 'skewwed lowerlimit ' + str(lowerlimit)
    print 'data ' +str(tot)



# Calculate the average delay between requested and received block
def block_delay_mean(date,honeyNodeLocation):
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


# Calculate the average delay between requested and received transaction
def tx_delay_mean(date, honeyNodeLocation):
    delayResults = open(honeyNodeLocation+"/TransactionDelayResults.txt", "r+")
    delays = []
    if date == 'x':
        for line in delayResults:
            [hour, min, sec] = parse.get_delay(line)
            delay = datetime.timedelta(hours=int(hour), minutes=int(min), seconds=int(sec))
            delays.append(delay)
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


def get_getaddr_list_format(honeyNodeLocation):
    GETADDRres = honeyNodeLocation+'/GETADDRResults.txt'
    getaddrResults = open(GETADDRres, 'r+')
    x = []
    y = []
    dict = {}
    for line in getaddrResults:
        if 'received:'in line:
            date = parse.get_date(line)
            if date not in dict.keys():
                dict[date] = 1
            else:
                i = dict[date]
                i = i + 1
                dict[date] = i

    for key in sorted(dict):
        x.append(key)
        y.append(dict[key])
    return [x,y]

def get_conn_nb_list_format(honeyNodeLocation):
    with open(honeyNodeLocation+'/Dict/dictConnectionNb.txt', 'r') as jsonNb:
        dictNbPeers = json.load(jsonNb)
    x=[]
    y=[]
    for key in sorted(dictNbPeers):
        x.append(key)
        y.append(dictNbPeers[key])
    print x
    return [x,y]


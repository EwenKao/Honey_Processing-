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

def peak_detection(list,type):
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
            with open(type+'_snaps/'+type+'_nb_dict_snapshot_'+ date +'.txt', 'rb') as handle:
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

        if deviation > 30 and deviation < 50:
            mediumSuspect.append(key)

        elif deviation >= 50:
            highSuspect.append(key)

    for i in range(0, len(list), 1):
        date = datetime.datetime.fromtimestamp(list[i]).strftime('%Y-%m-%d')
        try:
            with open(type+'_snaps/'+type+'_ip_dict_snapshot_'+ date +'.txt', 'rb') as handle:
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
def conntime_mean(date):
    connResults = open("ConnectionResults.txt","r+")
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

def connection_number(date):
    connNb = 0
    connResults = open("ConnectionResults.txt", "r+")
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
    index = 481
    iterations = 481 / 2
    stdev = []
    time = 1477742400

    for i in range(1, iterations, 1):
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        index = index - 2
        try:
            with open('AS_snaps/AS_dict_snapshot_' + date + '_' + str(index) + '.txt', 'rb') as handle:
                dict = pickle.load(handle)
        except IOError, e:
            time = time + 86400
            date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
            with open('AS_snaps/AS_dict_snapshot_' + date + '_' + str(index) + '.txt', 'rb') as handle:
                dict = pickle.load(handle)

        print str(i * 100 / iterations) + '%'

        for key in dict:
            value = dict[key]
            if key in dictData.keys():
                dictData[key].append(value)
            else:
                dictData[key] = []
                dictData[key].append(value)

    for key in dictData:
        value = dictData[key]
        if numpy.mean(value) > 100:


            stdev.append(numpy.std(value))
        elif (max(value) - min(value)) > 40:
            stdev.append(numpy.std(value))


    average = numpy.mean(stdev)
    median = numpy.median(stdev)
    print average
    print median


# Calculate the average delay between requested and received block
def block_delay_mean(date):
    delayResults = open("BlockDelayResults.txt","r+")
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
def tx_delay_mean(date):
    delayResults = open("TransactionDelayResults.txt", "r+")
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
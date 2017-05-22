#!/usr/bin/env python

# File name:            debugloganalyser.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
Main file that:
    - prepares the debug.log-file to be processed
    - calculates statistics on processed data
"""


import time
import os.path
import json
import datetime
import pickle
import csv
import collections

import process
import statistics
import geckoboard
import parse
import peerloganalyser
import graph

# NYC or AMS
honeyNodeLocation = 'NYC'

# Create directories
try:
    os.makedirs("Snapshot_Stats")
except OSError:
    pass
try:
    os.makedirs(honeyNodeLocation+"/Dict")
except OSError:
    pass
# 07-03-2017 = 1488888000
# 31-03-2017 = 1490961601

# 01-04-2017 = 1491048000
# 05-04-2017 = 1491393601
# 06-04-2017 = 1491480000
# 30-04-2017 = 1493553601

# 01-05-2017 = 1493640000
# 07-05-2017 = 1494158400
# 21-05-2017 = 1495368001
# INITIALISATION create/ open files, declare globals and buffers
for timestamp in range(1493640000,1495368001,86400):
    date = datetime.datetime.fromtimestamp(timestamp).strftime("%y_%m_%d")
    print date
    debugLog = "Logs/"+date+'.txt'
    bitcoinLog= open(debugLog ,'r+')

    outputMisbehaving = open(honeyNodeLocation+"/MisbehavingResults.txt", "a")
    outputInactivity = open(honeyNodeLocation+"/InactivityResults.txt","a")

    outputConnection = open(honeyNodeLocation+"/ConnectedPeersResults.txt", "a")
    outputStats = open(honeyNodeLocation+"/StatsResults.txt","a")

    bufferAddedIP = []
    bufferMsgIP = []
    bufferADDR = []
    bufferGETADDR =[]
    bufferPeers = []
    bufferBlockPropagation = []
    bufferTXPropagation = []
    bufferInactivity = []
    bufferMisbehaving = []
    bufferVersion = []



    dictIPBlock = {}
    dictIDIP = {}
    dictInactiv = {}
    dictUnsolicited = {}
    dictMisbehaving = {}
    dictVersion = {}

    totalNb = 0
    type = -1
    peerList = -1
    mediumPriorityAS =-1
    highPriorityAS = -1
    mediumPriorityOrg = -1
    highPriorityOrg = -1
    suspect = False

    ####################################################################
    #################### Open dictionaries #############################
    ####################################################################

    # Format: id: {ip,reason,connday,conntime,type}
    try:
        with open(honeyNodeLocation+'/dictPeer.txt', 'r') as jsonPeer:
            dictPeer=json.load(jsonPeer)
    except IOError:
        dictPeer = {}

    # Format: id:{hash:time,hash:time}
    try:
        with open(honeyNodeLocation+'/Dict/dictBlockPropagationTrack.txt', 'r') as jsonBlock:
            dictBlockPropagationTrack = json.load(jsonBlock)
    except IOError:
        dictBlockPropagationTrack = {}

    # Format: id:{hash:time,hash:time}
    try:
        with open(honeyNodeLocation+'/Dict/dictTXPropagationTrack.txt', 'r') as jsonTX:
            dictTXPropagationTrack = json.load(jsonTX)
    except IOError:
        dictTXPropagationTrack = {}

    # Format: id:{hash:time,hash:time}
    try:
        with open(honeyNodeLocation+'/Dict/dictADDR.txt', 'r') as jsonADDR:
            dictADDR = json.load(jsonADDR)
    except IOError:
        dictADDR = {}

    try:
        with open(honeyNodeLocation+'/Dict/dictConnectionNb.txt', 'r') as jsonNb:
            dictNbPeers = json.load(jsonNb)
    except IOError:
        dictNbPeers = {}

    try:
        with open(honeyNodeLocation+'/currentNb.txt','r') as jsonCNb:
            currentNb = json.load(jsonCNb)
    except IOError:
        currentNb = 0

    ####################################################################
    ################ Parse Snapshot of the day #########################
    ####################################################################

    timestampList = []
    # Define window of size 5
    for t in range(timestamp-86400*5,timestamp+1,86400):
        timestampList.append(t)
    # Detect peeks from Autonomus Systems
    statistics.peak_detection(timestampList,'AS')
    # Detect peeks from Providers
    statistics.peak_detection(timestampList,'Organisation')


    # Check whether AS or organizations were supected today
    date =datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    if os.path.isfile('Snapshot_Stats/High_suspected_AS_'+date+'.txt'):
        with open('Snapshot_Stats/High_suspected_AS_'+date+'.txt', 'rb') as high:
            highPriorityAS = pickle.load(high)

    if os.path.isfile('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt', 'rb') as medium:
            mediumPriorityAS = pickle.load(medium)

    if os.path.isfile('Snapshot_Stats/High_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/High_suspected_AS_' + date + '.txt', 'rb') as high:
            highPriorityOrg = pickle.load(high)

    if os.path.isfile('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt', 'rb') as medium:
            mediumPriorityOrg = pickle.load(medium)

    ####################################################################
    ################ Parse Logpeerinfo.txt of the day ##################
    ####################################################################        VANAF 6/04/2017
    """
    # Prepare the LOGPEERINFO.TXT file to be processed
    peerloganalyser.init(timestamp)
    # Process the json formatted logfile AFTER 16 MAY
    #date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y_%m_%d")
    json_log = open("logpeerjson.txt", "r+")
    log = json.load(json_log)
    peerloganalyser.json_parse(log)
    """

    ####################################################################
    ################ Parse Debug.log of the day ########################
    ####################################################################
    # Prepare DEBUG.LOG file to be processed
    # Parse Log lines from log file
    for line in bitcoinLog:
        ## filter misbehaving
        if 'Misbehaving' in line:
            print 'Check for misbehaving'
            bufferMisbehaving.append(line)
            outputMisbehaving.write("".join(line))

        ## filter IP-addresses propagation
        if 'IP' in line and 'Port' in line and 'Added' in line:
            bufferAddedIP.append(line)

        ## filter ADDR and GETADDR messages propagation
        if 'disconnecting peer' in line or 'sending getaddr' in line or 'sending: getaddr' in line or 'received: addr' in line:
            bufferADDR.append(line)

        ## filter received GETADDR messages
        if 'received: getaddr' in line or '"getaddr"' in line or 'Added connection' in line or 'disconnecting peer' in line:
            bufferGETADDR.append(line)

        ## filter connction and disconnection of peers
        if 'Added connection' in line or 'disconnecting' in line or "Making feeler connection" in line or "socket" in line or "ping" in line or "Inactivity" in line or "stalling block" in line:
            bufferPeers.append(line)

        ## filter request and delivery of blocks
        if 'disconnecting peer' in line or 'Inactivity' in line or 'Requesting block' in line or 'sending getdata' in line or 'received: block' in line or 'received block' in line:
            bufferBlockPropagation.append(line)

        ## filter request and delivery of transactions
        if 'disconnecting peer' in line or 'Inactivity' in line or 'Requesting witness-tx' in line or 'sending getdata' in line or 'received: tx' in line or 'received transaction' in line:
            bufferTXPropagation.append(line)

        if 'Inactivity' in line:
            bufferInactivity.append(line)
            outputInactivity.write("".join(line))

        if 'receive version message:' in line:
            bufferVersion.append(line)

    # Process the buffers
    # Check for unsolocited ADDR message
    if bufferADDR:
        print("Check ADDR and GETADDR messages propagation")
        process.message_process(bufferADDR, dictADDR,dictUnsolicited,honeyNodeLocation)
        with open(honeyNodeLocation+'/Dict/dictADDR.txt', 'w') as outfile:
            json.dump(dictADDR, outfile)

    # Monitor connection/disconnection of peers
    if bufferPeers:
        print("Monitor peerconnections")
        process.connection_monitor(bufferPeers, dictPeer,dictNbPeers,currentNb,totalNb,honeyNodeLocation)
        with open(honeyNodeLocation+'/totalNb.txt','r') as jsonCNb:
            totalNb = json.load(jsonCNb)
        with open(honeyNodeLocation+'/Dict/dictPeer.txt', 'w') as outfile:
            json.dump(dictPeer, outfile)
        averageConnectiontime = statistics.conntime_mean('x',honeyNodeLocation)
        averageConnectiontimeDay = statistics.conntime_mean(str(date),honeyNodeLocation)
        connectionNumber = statistics.connection_number(date,honeyNodeLocation)
        outputStats.write("Results of "+str(date)+": \n")
        outputStats.write("Average connectiontime of the day: "+ str(averageConnectiontimeDay) +"\n")
        outputStats.write("Cumulative average connectiontime: "+ str(averageConnectiontime) +"\n")
        outputStats.write("Number of connections of the day: "+ str(totalNb) +"\n")
        with open(honeyNodeLocation+'/Dict/dictConnectionNb.txt','w') as nb:
            json.dump(dictNbPeers,nb)

    # Monitor delay between request and delivery of Blocks
    if bufferBlockPropagation:
        print("Monitor block propagation delays")
        process.track_block_propagation(bufferBlockPropagation,dictBlockPropagationTrack,dictPeer,honeyNodeLocation)
        with open(honeyNodeLocation+'/Dict/dictBlockPropagationTrack.txt', 'w') as outfile:
            json.dump(dictBlockPropagationTrack, outfile)
        try:
            averageBlockDelay = statistics.block_delay_mean('x',honeyNodeLocation)
            averageBlockDelayDay = statistics.block_delay_mean(str(date),honeyNodeLocation)
            outputStats.write("Average block delay of the day: " + str(averageBlockDelayDay) + "\n")
            outputStats.write("Cumulative Average block delay: " + str(averageBlockDelay) + "\n")
        except IOError,e:
            print e

    # Monitor delay between request and delivery of Transactions
    if bufferTXPropagation:
        print "Monitor tx propagation delays"
        process.track_tx_propagation(bufferTXPropagation,dictTXPropagationTrack,dictPeer,honeyNodeLocation)
        with open(honeyNodeLocation+'/Dict/dictTXPropagationTrack.txt', 'w') as outfile:
            json.dump(dictTXPropagationTrack, outfile)
        try:
            averageBlockDelay = statistics.tx_delay_mean('x',honeyNodeLocation)
            averageBlockDelayDay = statistics.tx_delay_mean(str(date),honeyNodeLocation)
            outputStats.write("Average transaction delay of the day: " + str(averageBlockDelayDay) + "\n")
            outputStats.write("Cumulative average transaction delay: " + str(averageBlockDelay) + "\n")
        except IOError, e:
            print e

    if bufferGETADDR:
        process.get_addr_provenance(bufferGETADDR,honeyNodeLocation)



    # Monitor inactivity of peers
    if bufferInactivity:
        print "Inactivity Check"
        process.inactivity_check(bufferInactivity,dictInactiv)

    # Keep track of the core version used by peers
    if bufferVersion:
        process.version_check(bufferVersion,dictVersion)


    # Peer information
    if os.path.isfile(honeyNodeLocation+'/Peers/in_out_bound_' + date + '.txt'):
        with open(honeyNodeLocation+'/Peers/in_out_bound_' + date + '.txt', 'rb') as out:
            type = pickle.load(out)
    if os.path.isfile(honeyNodeLocation+'/Peers/in_out_bound_' + date + '.txt'):
        with open(honeyNodeLocation+'/Peers/PeerList_' + date + '.txt', 'rb') as peers:
            peerList = pickle.load(peers)

"""

    # Bring into account the second log file
    outputStats.write("Peers of the day: \n")
    if peerList != -1:
        for key in peerList:
            ip = peerList[key]
            connType = type[key]
            version = dictVersion[key]
            outputStats.write("peer id: "+str(key)+"\n")
            outputStats.write("peer ip-address: "+str(ip)+"\n")
            outputStats.write("type of connection: "+connType+"\n")
            outputStats.write("version: "+version+"\n")
            outputStats.write("suspected: ")

            if mediumPriorityAS != -1:
                for AS in mediumPriorityAS:
                    if key in mediumPriorityAS[AS]:
                        outputStats.write("Medium priority \n")
                        suspect = True
            if highPriorityAS != -1:
                for AS in highPriorityAS:
                    if key in highPriorityAS[AS]:
                        outputStats.write("Hight priority \n ")
                        suspect = True
            if not suspect:
                outputStats.write("No \n")


            outputStats.write("Suspicious behaviour: ")
            if bufferInactivity:
                if str(key) in dictInactiv.keys():
                    outputStats.write("Inactivity: "+str(dictInactiv[str(key)])+", ")
            if dictUnsolicited:
                if str(key) in dictUnsolicited:
                    outputStats.write("Unsolicited ADDR message size:"+str(dictUnsolicited[str(key)])+", ")
            outputStats.write("\n")


"""


## Push data on Gecko dashboard
# Convert data to json format
x,y = statistics.get_getaddr_list_format(honeyNodeLocation)
geckoboard.update_getaddr_chart(x,y)

# Display line chart with numer of connection of Honeynode NYC
x,y = statistics.get_conn_nb_list_format(honeyNodeLocation)
geckoboard.update_connection_nb(x,y,honeyNodeLocation)

# Display cumulatieve avg connection time
averageConnectiontime = statistics.conntime_mean('x',honeyNodeLocation)
geckoboard.avg_cum_conntime((averageConnectiontime.seconds%3600)//60)

# Display avg connection time of the day
averageConnectiontimeDay = statistics.conntime_mean(str(date),honeyNodeLocation)
geckoboard.avg_day_conntime((averageConnectiontimeDay.seconds%3600)//60, date)

# Display current date
dateString = datetime.datetime.fromtimestamp(timestamp).strftime("%d %b %y")
geckoboard.display_current_date(dateString)

# Update organisation line chart
graph.AS_graph(timestamp)

# Update AS line chart

"""
# Prepare the LOGPEERINFO.TXT file to be processed
peerloganalyser.init()
# Process the json formatted logfile AFTER 16 MAY
#date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y_%m_%d")
json_log = open("logpeerjson.txt", "r+")
log = json.load(json_log)
peerloganalyser.json_parse(log)
"""
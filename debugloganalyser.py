#!/usr/bin/env python

# File name:            debugloganalyser.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
Main file of the processing unit that:
    - prepares the debug.log-file to be processed
    - calculates statistics on processed data
"""


import os.path
import json
import datetime
import pickle


import process
import statistics
import geckoboard
import parse
import peerloganalyser
import graph

# NYC or AMS or General
honeyNodeID = 'AMS'

# 07-03-2017 = 1488888000
# 31-03-2017 = 1490961601

# 01-04-2017 = 1491048000
# 05-04-2017 = 1491393601
# 06-04-2017 = 1491480000
# 25-04-2017 = 1493121600
# 26-04-2017 = 1493208000
# 30-04-2017 = 1493553601

# 01-05-2017 = 1493640000
# 07-05-2017 = 1494158400
# 21-05-2017 = 1495368001
# 26-05-2017 = 1495800000
# 27-05-2017 = 1495886400
# 28-05-2017 = 1495972800
# 29-05-2017 = 1496059200
# 30-05-2017 = 1496145600
# 31-05-2017 = 1496232001

# 01-06-2017 = 1496318400
# 02-06-2017 = 1496404800
# 03-06-2017 = 1496491200
# 04-06-2017 = 1496577600
# 05-06-2017 = 1496664000
# 06-06-2017 = 1496750400
# 07-06-2017 = 1496836800
# 08-06-2017 = 1496923200
# 09-06-2017 = 1497009600
# 10-06-2017 = 1497096000
# 11-06-2017 = 1497182400
# 12-06-2017 = 1497268800
# 13-06-2017 = 1497355200
# 14-06-2017 = 1497441600
# 15-06-2017 = 1497528000
# 16-06-2017 = 1497614400
# 17-06-2017 = 1497700800
# 18-06-2017 = 1497787200
# 24-06-2017 = 1498305600

start = 1496318400
stop = 1497787201



# Create directories
try:
    os.makedirs("Snapshot_Stats")
except OSError:
    pass
try:
    os.makedirs(honeyNodeID+"/Dict")
except OSError:
    pass



if honeyNodeID == 'General':
    timestampList = []
   # def tail(f, n, offset=0):
    stdin, stdout = os.popen2("tail -n " + str(10) +  ' ' + 'ALL_snaps/timestamps.txt')
    stdin.close()
    lines = stdout.readlines()
    stdout.close()
    for time in lines:
        timestampList.append(int(time))

    # Redefine thresholds
    print "Calculate new treshold"
    upperlimit, supralimit = statistics.adjusted_boxplot_fences()
    print upperlimit
    print supralimit
    # Detect peeks from Autonomus Systems
    print "start peak detection"
    statistics.peak_detection(timestampList, 'AS', upperlimit, supralimit)
    # Detect peeks from Providers
    statistics.peak_detection(timestampList, 'Organization', upperlimit, supralimit)

    # Check whether AS or organizations were supected today
    date = datetime.datetime.fromtimestamp(timestampList[-1]).strftime("%Y-%m-%d_%H_%M_%S")
    if os.path.isfile('Snapshot_Stats/High_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/High_suspected_AS_' + date + '.txt', 'rb') as high:
            highPriorityAS = pickle.load(high)
    else:
        highPriorityAS = {}

    if os.path.isfile('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt', 'rb') as medium:
            mediumPriorityAS = pickle.load(medium)
    else:
        mediumPriorityAS = {}

    if os.path.isfile('Snapshot_Stats/High_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/High_suspected_AS_' + date + '.txt', 'rb') as high:
            highPriorityOrg = pickle.load(high)

    if os.path.isfile('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt'):
        with open('Snapshot_Stats/Medium_suspected_AS_' + date + '.txt', 'rb') as medium:
            mediumPriorityOrg = pickle.load(medium)


    print "Update graphs and Monitor"
    # Update organisation line chart
    geckoboard.update_AS_graph('ALL_snaps','AS')
    #graph.AS_graph('ALL_snaps','Organization')
    geckoboard.update_AS_graph('Last_Days_snaps','AS')

    print "Update lists"
    # Get list of AS with organisation name and # nodes
    ASList = process.get_AS_leaders(timestampList[-1])
    geckoboard.update_AS_leaderboard(ASList, mediumPriorityAS, highPriorityAS)
    print highPriorityAS
    # Display current date
    dateString = datetime.datetime.fromtimestamp(timestampList[-1]).strftime("%d %b %y")
    geckoboard.display_current_date(dateString,honeyNodeID)
    geckoboard.update_AS_suspected_ip_list(highPriorityAS, date)

    geckoboard.update_protocol_pie(date)




else:
    # INITIALISATION create/ open files, declare globals and buffers
    for timestamp in range(start,stop,86400):
        date = datetime.datetime.fromtimestamp(timestamp).strftime("%y_%m_%d")
        print date
        debugLog = honeyNodeID+"_Logs/"+date+'.txt'
        bitcoinLog= open(debugLog ,'r+')

        outputMisbehaving = open(honeyNodeID+"/MisbehavingResults.txt", "a")
        outputInactivity = open(honeyNodeID+"/InactivityResults.txt","a")

        outputConnection = open(honeyNodeID+"/ConnectedPeersResults.txt", "a")
        outputStats = open(honeyNodeID+"/StatsResults.txt","a")

        bufferAddedIP = []
        bufferMsgIP = []
        bufferADDR = []
        bufferMessages =[]
        bufferPeers = []
        bufferBlockPropagation = []
        bufferTXPropagation = []
        bufferInactivity = []
        bufferMisbehaving = []
        bufferVersion = []

        dictIPBlock = {}
        dictIDIP = {}
        dictInactiv = {}
        dictMisbehaving = {}
        dictVersion = {}

        totalNb = 0
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
            with open(honeyNodeID+'/Dict/dictPeer.txt', 'r') as jsonPeer:
                dictPeer=json.load(jsonPeer)
        except IOError:
            dictPeer = {}
        print 'dictpeer'
        print dictPeer

        # Format: id:{hash:time,hash:time}
        try:
            with open(honeyNodeID+'/Dict/dictBlockPropagationTrack.txt', 'r') as jsonBlock:
                dictBlockPropagationTrack = json.load(jsonBlock)
        except IOError:
            dictBlockPropagationTrack = {}

        # Format: id:{hash:time,hash:time}
        try:
            with open(honeyNodeID+'/Dict/dictTXPropagationTrack.txt', 'r') as jsonTX:
                dictTXPropagationTrack = json.load(jsonTX)
        except IOError:
            dictTXPropagationTrack = {}

        # Format: id:{hash:time,hash:time}
        try:
            with open(honeyNodeID+'/Dict/dictADDR.txt', 'r') as jsonADDR:
                dictADDR = json.load(jsonADDR)
        except IOError:
            dictADDR = {}

        try:
            with open(honeyNodeID+'/Dict/dictConnectionNb.txt', 'r') as jsonNb:
                dictNbPeers = json.load(jsonNb)
        except IOError:
            dictNbPeers = {}

        try:
            with open(honeyNodeID+'/currentNb.txt','r') as jsonCNb:
                currentNb = json.load(jsonCNb)
        except IOError:
            currentNb = 0



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
                print 'Misbehaving activity detected'
                bufferMisbehaving.append(line)
                outputMisbehaving.write("".join(line))

            ## filter IP-addresses propagation
            if 'IP' in line and 'Port' in line and 'Added' in line:
                bufferAddedIP.append(line)

            ## filter ADDR and GETADDR messages propagation
            if 'disconnecting peer' in line or 'Added connection' in line or 'sending getaddr' in line or 'sending: getaddr' in line or 'received: addr' in line:
                bufferADDR.append(line)

            ## filter received ADDR and INV messages
            if 'received: getaddr' in line or 'received: inv' in line or 'received: addr' in line or '"getaddr"' in line or 'Added connection' in line or 'disconnecting peer' in line:
                bufferMessages.append(line)

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
            process.message_process(bufferADDR, dictADDR,honeyNodeID)

        # Monitor connection/disconnection of peers
        if bufferPeers:
            print("Monitor peerconnections")
            process.connection_monitor(bufferPeers, dictPeer,dictNbPeers,currentNb,totalNb,honeyNodeID)
            with open(honeyNodeID+'/totalNb.txt','r') as jsonCNb:
                totalNb = json.load(jsonCNb)
            averageConnectiontime = statistics.conntime_mean('x',honeyNodeID)
            averageConnectiontimeDay = statistics.conntime_mean(str(date),honeyNodeID)
            connectionNumber = statistics.connection_number(date,honeyNodeID)
            outputStats.write("Results of "+str(date)+": \n")
            outputStats.write("Average connectiontime of the day: "+ str(averageConnectiontimeDay) +"\n")
            outputStats.write("Cumulative average connectiontime: "+ str(averageConnectiontime) +"\n")
            outputStats.write("Number of connections of the day: "+ str(totalNb) +"\n")


        # Monitor delay between request and delivery of Blocks
        if bufferBlockPropagation:
            print("Monitor block propagation delays")
            process.track_block_propagation(bufferBlockPropagation,dictBlockPropagationTrack,honeyNodeID)

            try:
                averageBlockDelay = statistics.block_delay_mean('x',honeyNodeID)
                averageBlockDelayDay = statistics.block_delay_mean(str(date),honeyNodeID)
                outputStats.write("Average block delay of the day: " + str(averageBlockDelayDay) + "\n")
                outputStats.write("Cumulative Average block delay: " + str(averageBlockDelay) + "\n")
            except IOError,e:
                print e

        # Monitor delay between request and delivery of Transactions
        if bufferTXPropagation:
            print "Monitor tx propagation delays"
            #process.track_tx_propagation(bufferTXPropagation,dictTXPropagationTrack,honeyNodeID)

            #try:
             #   averageBlockDelay = statistics.tx_delay_mean('x',honeyNodeID)
              #  averageBlockDelayDay = statistics.tx_delay_mean(str(date),honeyNodeID)
               # outputStats.write("Average transaction delay of the day: " + str(averageBlockDelayDay) + "\n")
                #outputStats.write("Cumulative average transaction delay: " + str(averageBlockDelay) + "\n")
            #except IOError, e:
             #   print e

        if bufferMessages:
            process.get_msg_provenance(bufferMessages,honeyNodeID)

        # Monitor inactivity of peers
        if bufferInactivity:
            print "Inactivity Check"
            process.inactivity_check(bufferInactivity,dictInactiv)

        # Keep track of the core version used by peers
        if bufferVersion:
            process.version_check(bufferVersion,dictVersion)

        # Peer information
        if os.path.isfile(honeyNodeID+'/Peers/in_out_bound_' + date + '.txt'):
            with open(honeyNodeID+'/Peers/in_out_bound_' + date + '.txt', 'rb') as out:
                type = pickle.load(out)
        if os.path.isfile(honeyNodeID+'/Peers/in_out_bound_' + date + '.txt'):
            with open(honeyNodeID+'/Peers/PeerList_' + date + '.txt', 'rb') as peers:
                peerList = pickle.load(peers)


    ## Push data on Gecko dashboard
    # Convert data to json format
    print 'push GETADDR'
    x,y,suspect = statistics.message_list_format(honeyNodeID,'GETADDR')
    geckoboard.update_getaddr_chart(x,y,honeyNodeID)
    geckoboard.getaddr_list(suspect,honeyNodeID)

    print 'push INV'
    x,y,suspect = statistics.message_list_format(honeyNodeID,'INV')
    geckoboard.update_inv_chart(x,y,honeyNodeID)

    print 'push ADDR'
    x,y,suspect = statistics.message_list_format(honeyNodeID,'ADDR')
    geckoboard.update_addr_chart(x,y,honeyNodeID)


    # Display list of current active peers
    with open(honeyNodeID + '/Dict/dictPeer.txt', 'rb') as out:
        dictPeer = json.load(out)
    geckoboard.update_peer_list(dictPeer,honeyNodeID)


    # Display cumulatieve avg connection time
    averageConnectiontime = statistics.conntime_mean('x',honeyNodeID)
    geckoboard.avg_cum_conntime((averageConnectiontime.seconds%3600)//60,honeyNodeID)

    # Display avg connection time of the day
    averageConnectiontimeDay = statistics.conntime_mean(str(date),honeyNodeID)
    if averageConnectiontimeDay == None:
        geckoboard.avg_day_conntime(0, date,honeyNodeID)
    else:
        geckoboard.avg_day_conntime((averageConnectiontimeDay.seconds%3600)//60, date,honeyNodeID)

    # Display current date
    dateString = datetime.datetime.fromtimestamp(timestamp).strftime("%d %b %y")
    geckoboard.display_current_date(dateString,honeyNodeID)

    # Displays average block delay
    averageBlockDelay = statistics.block_delay_mean('x',honeyNodeID)
    geckoboard.avg_cum_blockdelay((averageBlockDelay.seconds%3600),honeyNodeID)

    # Display average tx delay
    averageTxDelay = statistics.tx_delay_mean('x',honeyNodeID)
    if averageTxDelay == 'x':
        geckoboard.avg_cum_txdelay(1,honeyNodeID)
    else:
        geckoboard.avg_cum_txdelay((averageTxDelay.seconds%3600),honeyNodeID)

    # Display line chart with numer of connection of Honeynode NYC
    x, y = statistics.get_conn_nb_list_format(honeyNodeID)
    geckoboard.update_connection_nb(x, y, honeyNodeID)

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
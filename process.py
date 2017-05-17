#!/usr/bin/env python

# File name:            process.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This file process the debug.log file
"""

import datetime
import json
import parse
import ipaddress
import collections
import random


# Check for unsolicited ADDR msg
def message_process(buffer,dictADDR,dictUnsolicited):
    outputADDR = open("unsolicitedADDRmsgResult.txt","a")
    for line in buffer:
        if "sending" in line:
            id = parse.get_peer_id(line)
            dictADDR[id] = 0
        elif "received:" in line:
            id = parse.get_peer_id(line)
            if id in dictADDR.keys():
                size = parse.get_size(line)
                if (dictADDR[id] < 3) and (int(size) > 301): # peer can responds with up to 3 ADDR on an GETADDR
                    i= dictADDR[id]
                    i= i+1
                    dictADDR[id] = i
                else:
                    size = parse.get_size(line)
                    if int(size) > 301:  #size of 10 addresses
                        date = parse.get_date(line)
                        time = parse.get_time(line)
                        outputADDR.write(date + " " + time + " Unsolicited ADDR msg, more than three responses from peer=:" + id + " size: " + str(int(size) / 30) + " messages \n")
                        if id not in dictUnsolicited:
                            dictUnsolicited[id] = []
                            dictUnsolicited[id].append(str(int(size)/30))
                        else:
                            dictUnsolicited[id].append(str(int(size)/30))
            else:
                size = parse.get_size(line)
                if int(size) > 301:  # size of 10 addresses. It is normal to send unsolicited ADDR msg containng less than 10 addresses
                    date = parse.get_date(line)
                    time = parse.get_time(line)
                    outputADDR.write(date +" "+time+" Unsolicited ADDR msg from peer="+id + " size: "+ str(int(size)/30) + " messages \n")
                    if id not in dictUnsolicited:
                        dictUnsolicited[id] = []
                        dictUnsolicited[id].append(str(int(size) / 30))
                    else:
                        dictUnsolicited[id].append(str(int(size) / 30))

        elif 'disconnecting peer' in line:
            id = parse.get_peer_id(line)
            if id in dictADDR.keys():
                del dictADDR[id]


def connection_monitor(buffer, dictPeer,dictNbPeer,currentNb,totalNb):
    reason = 'x'
    feelerIP = 'x'
    feelerPort = 'x'
    for line in buffer:
        if "Added connection" in line:
            id  = parse.get_peer_id(line)
            # If proper node restarts
            if id == '0':
                # Reset peerList
                if dictPeer:
                    for peerid in dictPeer:
                        ip = dictPeer[peerid]['ip']
                        connectiontime = dictPeer[peerid]['conntime']
                        deconnectiontime = parse.get_time(line)
                        deconnectionday = parse.get_date(line)
                        enter = datetime.datetime.strptime(connectiontime, '%H:%M:%S')
                        exit = datetime.datetime.strptime(deconnectiontime, '%H:%M:%S')
                        delta = exit - enter
                        outputConnection = open("ConnectionResults.txt", "a")
                        outputConnection.write(deconnectionday + " " + deconnectiontime + " peer=" + peerid + " : " + ip + " connection time:" + "".join(str(delta)) + " reason: disconnection proper node\n")

                dictPeer = {}

                currentNb=0

                # Monitor restarting of node
                outputRestart = open("RestartingNode.txt", "a")
                restartingTime = parse.get_time(line)
                restartingDay = parse.get_date(line)
                outputRestart.write('Node restarts at : '+"".join(restartingDay)+" ".join(restartingTime)+"\n")

            # If new connection with a peer is made
            version, ip, port = parse.get_ip_port(line)
            dictPeer[id] = {}
            dictPeer[id]['ip'] = ip
            dictPeer[id]['conntime'] = parse.get_time(line)
            dictPeer[id]['connday'] = parse.get_date(line)
            dictPeer[id]['reason'] = 'x'
            # Check if connection is a feeler connecion
            if feelerIP == ip and feelerPort == port:
                dictPeer[id]['type'] = "feeler"
            else:
                dictPeer[id]['type'] = "peer"
                connectiontime = parse.get_date(line) + " " + parse.get_time(line)
                currentNb +=1
                print currentNb
                totalNb +=1
                dictNbPeer[connectiontime] = currentNb


        elif "Making feeler connection" in line:
            version, ip, port = parse.get_ip_port(line)
            feelerIP = ip
            feelerPort = port

        elif "socket closed" in line:
            reason = 'closed socket'
        elif "socket send error" in line:
            reason = 'socket error'
        elif "socket recv error Connection reset by peer" in line:
            reason = 'connection reset by peer'
        elif "socket recv error Connection timed out" in line:
            reason = 'socket inactivity'
        elif "socket sending timeout:" in line:
            reason = 'socket inactivity'
        elif "socket receive timeout:" in line:
            reason = 'socket inactivity'
        elif "socket no message in first" in line:
            reason = 'inactivity in first 60sec'
        elif "ping timeout:" in line:
            reason = "ping inactivity"
        elif "Inactivity" in line:
            id = parse.get_peer_id(line)
            if id in dictPeer.keys():
                dictPeer[id]['reason'] = 'inactivity'

        # If node disconnect with a peer
        elif "disconnecting" in line:
            id = parse.get_peer_id(line)
            # Update peerList and monitor the duration of connection
            if id in dictPeer.keys():
                if reason == 'x':
                    reason = dictPeer[id]['reason']
                if 'does not offer the expected services' in line:
                    reason = 'unexpected services'
                if "is stalling block" in line:
                    reason = 'stalling block download'
                if "Timeout downloading block" in line:
                    reason = 'Timeout downloading block'
                if "using obsolete version" in line:
                    reason = "using obsolete version"
                if "connected to self at" in line:
                    reason = "connect to ourself"
                if dictPeer[id]['type'] == "feeler":
                    reason = "feeler"

                connectiontime = dictPeer[id]['conntime']
                connectionday = dictPeer[id]['connday']

                ip = dictPeer[id]['ip']

                deconnectiontime = parse.get_time(line)
                deconnectionday = parse.get_date(line)
                enter = datetime.datetime.strptime(connectiontime, '%H:%M:%S')
                exit = datetime.datetime.strptime(deconnectiontime, '%H:%M:%S')
                delta =  exit - enter

                if connectionday != deconnectionday:
                    start = datetime.datetime.strptime(connectionday, '%Y-%m-%d')
                    stop = datetime.datetime.strptime(deconnectionday, '%Y-%m-%d')
                    days = stop - start
                    delta = delta + days
                outputConnection = open("ConnectionResults.txt", "a")
                outputConnection.write(deconnectionday+" "+deconnectiontime+" peer="+id+" : "+ip+ " connection time:"+"".join(str(delta))+ " reason:" + reason +"\n")
                if dictPeer[id]['type'] == "peer":
                    deconnection = deconnectionday + " " + deconnectiontime
                    currentNb -=1
                    print currentNb
                    dictNbPeer[deconnection] = currentNb
                dictPeer.pop(id)
                reason = 'x'
                feelerIP = 'x'
                feelerPort = 'x'
    with open('currentNb.txt', 'w') as cnb:
        json.dump(currentNb, cnb)
    with open('totalNb.txt', 'w') as cnb:
        json.dump(totalNb, cnb)

            #.replace(" -1 day, ", ""))
def track_block_propagation(buffer,dict,dictPeer):
    inactivePeer = "-1"
    inactive = False
    for line in buffer:
        if 'Requesting block' in line:
            id = parse.get_peer_id(line)
            hash = parse.get_hash(line)
            time = parse.get_time(line)

            if id not in dict.keys():
                dict[id]= {}
                dict[id][hash] = time
            else:
                dict[id][hash] = time


        elif 'received block'in line:
            id = parse.get_peer_id(line)
            hash = parse.get_hash(line)
            time = parse.get_time(line)
            date = parse.get_date(line)
            if id in dict:
                if hash in dict[id].keys():
                    requestedTime = dict[id][hash]
                    requested = datetime.datetime.strptime(requestedTime, '%H:%M:%S')
                    received = datetime.datetime.strptime(time, '%H:%M:%S')
                    delta = received - requested
                    if delta < datetime.timedelta(minutes=0):
                        delta = delta + datetime.timedelta(days=1)
                    outputBlockDelay = open("BlockDelayResults.txt", "a")
                    outputBlockDelay.write(date +" "+ time +" Peer:" + id + " Block delay:" + "".join(str(delta).replace(" -1 day, ", "")) + " \n")
                    del dict[id][hash]
                else:
                    outputUnsolicitedBlock = open("UnsolicitedBlockHash.txt", "a")
                    outputUnsolicitedBlock.write(date + " Received block from peer: "+id+" with hash: "+hash+" is not coming from a recent getdata \n")

        elif 'Inactivity' in line:
            inactivePeer = parse.get_peer_id(line)

        elif 'disconnecting peer' in line:
            id = parse.get_peer_id(line)
            currentTime = parse.get_time(line)
            received = datetime.datetime.strptime(currentTime, '%H:%M:%S')
            if id in dict:
                if (id == inactivePeer): # inactive == True: # replace by:  if (id == inactivePeer): for logs after 25 of April
                    for hash in dict[id]:
                        sentTime = dict[id][hash]
                        requested = datetime.datetime.strptime(sentTime, '%H:%M:%S')
                        delta = received - requested
                        if delta < datetime.timedelta(minutes=0):
                            delta = delta + datetime.timedelta(days=1)
                        if delta > datetime.timedelta(minutes=20):
                            outputBlockDelay = open("BlockTimeOuts.txt", "a")
                            outputBlockDelay.write(date + " " + time + " Peer:" + id + " didn't response to block:" + hash + " \n")
                del dict[id]

        if 'socket sending timeout:' in line or 'socket receive timeout:' in line: # To be removed for logs after 25 of April
            inactive = True

def track_tx_propagation(buffer, dict, dictPeer):
    inactivePeer = "-1"
    inactive = False
    for line in buffer:
        if 'Requesting witness-tx' in line:
            id = parse.get_peer_id(line)
            hash = parse.get_hash(line)
            time = parse.get_time(line)

            if id not in dict.keys():
                dict[id] = {}
                dict[id][hash] = time
            else:
                dict[id][hash] = time

        elif 'received transaction' in line: # Only from logs after 23/04
            id = parse.get_peer_id(line)
            hash = parse.get_hash(line)
            time = parse.get_time(line)
            date = parse.get_date(line)
            if id in dict:
                if hash in dict[id].keys():
                    requestedTime = dict[id][hash]
                    requested = datetime.datetime.strptime(requestedTime, '%H:%M:%S')
                    received = datetime.datetime.strptime(time, '%H:%M:%S')
                    delta = received - requested
                    if delta < datetime.timedelta(minutes=0):
                        delta = delta + datetime.timedelta(days=1)
                    outputTransactionDelay = open("TransactionDelayResults.txt", "a")
                    outputTransactionDelay.write(date + " " + time + " transaction delay from peer:" + id + " delay:" + "".join(str(delta).replace(" -1 day, ", "")) + " \n")
                    del dict[id][hash]
                else:
                    outputUnsolicitedBlock = open("UnsolicitedTransactionHash.txt", "a")
                    outputUnsolicitedBlock.write(date + " Received transaction from peer: " + id + " with hash: " + hash + " is not coming from a recent getdata \n")

        elif 'Inactivity' in line:
            inactivePeer = parse.get_peer_id(line)

        elif 'disconnecting peer' in line:
            id = parse.get_peer_id(line)
            currentTime = parse.get_time(line)
            received = datetime.datetime.strptime(currentTime, '%H:%M:%S')
            if id in dict:
                if inactive == True:  # replace by:  if (id == inactivePeer): for logs after 23 of April

                    for hash in dict[id]:
                        sentTime = dict[id][hash]
                        requested = datetime.datetime.strptime(sentTime, '%H:%M:%S')
                        delta = received - requested
                        if delta < datetime.timedelta(minutes=0):
                            delta = delta + datetime.timedelta(days=1)
                        if delta > datetime.timedelta(minutes=20):
                            outputBlockDelay = open("TxTimeOuts.txt", "a")
                            outputBlockDelay.write(date + " " + time + " Peer:" + id + " didn't response to tx:" + hash + " \n")
                del dict[id]

        if 'socket sending timeout:' in line or 'socket receive timeout:' in line:  # To be removed for logs after 23 of April
            inactive = True




def inactivity_check(buffer,dict):
    for line in buffer:
        id = parse.get_peer_id(line)
        reason = parse.get_inactivity_reason(line)
        dict[id] = reason

def version_check(buffer,dict):
    for line in buffer:
        id = parse.get_peer_id(line)
        version = parse.get_version(line)
        dict[id] = version



# look for AS6719 KNOPP : 188.65.214
def ip_block_monitor(buffer,dict):
    for line in buffer:
        date = parse.get_date(line)
        version, ip ,port = parse.get_ip_port(line)
        if (version == 4):
            ## Create an IPv4Address object
            ipv4_netw = ipaddress.ip_network('' + ip + '').supernet(new_prefix=20)
            ipv4 = unicode(ipv4_netw)

            # IPblock kept in dictionary
            if dict.get(str(ipv4)):
                i = dict[str(ipv4)]
                i = i + 1
                dict[str(ipv4)] = i

            else:
                dict[str(ipv4)] = 1

    outputIPBlock = open("IPBlockResults.txt", "a")
    outputIPBlock.write("results of " +date+"\n")

    for ipblock in dict:
        outputIPBlock.write("IP block: " + str(ipblock) + " # ip: " + str(dict[ipblock]) + " \n")


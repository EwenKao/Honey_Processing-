#!/usr/bin/env python

# File name:            process.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This file process the debug.log file
    def message_process(buffer,dictADDR,dictUnsolicited,honeyNodeID):
    def connection_monitor(buffer, dictPeer,dictNbPeer,currentNb,totalNb,honeyNodeID):
    def track_block_propagation(buffer,dict,dictPeer,honeyNodeID):
    def track_tx_propagation(buffer, dict, dictPeer,honeyNodeID):
    def inactivity_check(buffer,dict):
    def version_check(buffer,dict):
    def get_addr_provenance(buffer,honeyNodeID):

"""

import datetime
import json
import pickle
import parse



def message_process(buffer,dictADDR,honeyNodeID):
    """
    Check for unsolicited ADDR msg

    :param buffer: lines of parsed log file to be processed
    :param dictADDR: contains for each peer the current number of GETADDR and ADDR messages received or sent
    :param honeyNodeID: the ID of the honeynode the data is coming from
    :return:
    """

    try:
        with open(honeyNodeID+'/Dict/activePeersADDR.txt', 'r') as jsonPeer:
            activePeers=json.load(jsonPeer)
    except IOError:
        activePeers = {}
    outputUnsolicitedADDR = open(honeyNodeID + "/unsolicitedADDRmsgResult.txt", "a")
    outputADDR = open(honeyNodeID + "/ADDRResults.txt", "a")
    for line in buffer:
        if "Added" in line:
            id = parse.get_peer_id(line)
            version, ip, port = parse.get_ip_port(line)
            addr = ip+":"+port
            activePeers[id] = addr
        elif "disconnecting peer" in line:
            id = parse.get_peer_id(line)
            if id in activePeers.keys():
                activePeers.pop(id)
            if id in dictADDR.keys():
                dictADDR.pop(id)
        elif "sending" in line:
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
                    date = parse.get_date(line)
                    time = parse.get_time(line)
                    id = parse.get_peer_id(line)
                    addr = activePeers[id]

                    if int(size) > 301:  #size of 10 addresses
                        outputUnsolicitedADDR.write(date + " " + time + " received unsolicited ADDR msg, more than three responses from size: " + str(int(size) / 30) + " messages peer=" + "".join(id) +" IP:Port="+"".join(addr)+"\n")
                    elif int(size) <= 301:
                        line = line.strip('\n')
                        outputADDR.write("".join(line) + " IP:Port=" + "".join(addr) + "\n")
            else:
                size = parse.get_size(line)
                date = parse.get_date(line)
                time = parse.get_time(line)
                id = parse.get_peer_id(line)
                print activePeers
                addr = activePeers[id]
                if int(size) > 301:  # size of 10 addresses. It is normal to send unsolicited ADDR msg containng less than 10 addresses
                    outputUnsolicitedADDR.write(date + " " + time + " received unsolicited ADDR msg from size: " + str(int(size) / 30) + " messages peer=" + "".join(id) + " IP:Port=" + "".join(addr) + "\n")
                else:
                    line = line.strip('\n')
                    outputADDR.write("".join(line) + " IP:Port=" + "".join(addr) + "\n")
    with open(honeyNodeID+'/Dict/activePeersADDR.txt', 'w') as outfile:
        json.dump(activePeers, outfile)
    with open(honeyNodeID + '/Dict/dictADDR.txt', 'w') as outfile:
        json.dump(dictADDR, outfile)

def connection_monitor(buffer, dictPeer,dictNbPeer,currentNb,totalNb,honeyNodeID):
    """
    Monitor the connection behaviour of the peers:
        - logs the connection duration of the peers
        - log the reason of disconnected peers
        - keep track of the current number of connected peers

    :param buffer: lines of parsed log file to be processed
    :param dictPeer: dictionary that keeps information about the current connected peers
    :param dictNbPeer: dictionary that keeps track of the number of connected peers
    :param currentNb: current number of connected peers
    :param totalNb: total number of connected peers of the day
    :param honeyNodeID: the ID of the honeynode the data is coming from
    :return:
    """
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
                    for peerid in dictPeer.keys():
                        ip = dictPeer[peerid]['ip']
                        connectiontime = dictPeer[peerid]['conntime']
                        deconnectiontime = parse.get_time(line)
                        deconnectionday = parse.get_date(line)
                        enter = datetime.datetime.strptime(connectiontime, '%H:%M:%S')
                        exit = datetime.datetime.strptime(deconnectiontime, '%H:%M:%S')
                        delta = exit - enter
                        outputConnection = open(honeyNodeID+"/ConnectionResults.txt", "a")
                        outputConnection.write(deconnectionday + " " + deconnectiontime + " peer=" + peerid + " : " + ip + " connection time:" + "".join(str(delta)) + " reason: disconnection proper node\n")

                dictPeer = {}
                currentNb=0

                # Monitor restarting of node
                outputRestart = open(honeyNodeID+"/RestartingNode.txt", "a")
                restartingTime = parse.get_time(line)
                restartingDay = parse.get_date(line)
                outputRestart.write('Node restarts at : '+"".join(restartingDay)+" "+"".join(restartingTime)+"\n")

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
                fulltime = datetime.datetime.strptime(parse.get_date(line) + "-" + parse.get_time(line), "%Y-%m-%d-%H:%M:%S")
                formattedTime = fulltime.isoformat()+"+02:00"
                currentNb +=1
                totalNb +=1
                dictNbPeer[formattedTime] = currentNb


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
                outputConnection = open(honeyNodeID+"/ConnectionResults.txt", "a")
                outputConnection.write(deconnectionday+" "+deconnectiontime+" peer="+id+" : "+ip+ " connection time:"+"".join(str(delta))+ " reason:" + reason +"\n")
                if dictPeer[id]['type'] == "peer":
                    fulltime = datetime.datetime.strptime(deconnectionday + "-" + deconnectiontime,"%Y-%m-%d-%H:%M:%S")
                    formattedTime = fulltime.isoformat()+"+02:00"
                    currentNb -=1
                    dictNbPeer[formattedTime] = currentNb
                dictPeer.pop(id)
                reason = 'x'
                feelerIP = 'x'
                feelerPort = 'x'
    with open(honeyNodeID+'/currentNb.txt', 'w') as cnb:
        json.dump(currentNb, cnb)
    with open(honeyNodeID+'/totalNb.txt', 'w') as cnb:
        json.dump(totalNb, cnb)
    with open(honeyNodeID + '/Dict/dictConnectionNb.txt', 'w') as nb:
        json.dump(dictNbPeer, nb)
    with open(honeyNodeID + '/Dict/dictPeer.txt', 'w') as nb:
        json.dump(dictPeer, nb)

def track_block_propagation(buffer,dict,honeyNodeID):
    """
    Monitor the requested and received blocks from the peers:
        - track unsolicided blocks
        - monitor the delay between requested and received blocks

    :param buffer: lines of parsed log file to be processed
    :param dict: dictionary {id:{hash:time}}
    :param honeyNodeID: the ID of the honeynode the data is coming from
    :return:
    """
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
                    outputBlockDelay = open(honeyNodeID+"/BlockDelayResults.txt", "a")
                    outputBlockDelay.write(date +" "+ time +" Peer:" + id + " Block delay:" + "".join(str(delta).replace(" -1 day, ", "")) + " \n")
                    del dict[id][hash]
                else:
                    outputUnsolicitedBlock = open(honeyNodeID+"/UnsolicitedBlockHash.txt", "a")
                    outputUnsolicitedBlock.write(date + " Received block from peer: "+id+" with hash: "+hash+" is not coming from a recent getdata \n")

        elif 'Inactivity' in line:
            inactivePeer = parse.get_peer_id(line)

        elif 'disconnecting peer' in line:
            id = parse.get_peer_id(line)
            currentTime = parse.get_time(line)
            date = parse.get_date(line)
            received = datetime.datetime.strptime(currentTime, '%H:%M:%S')
            if id in dict:
                if (id == inactivePeer): #if inactive == True: # replace by:  if (id == inactivePeer): for logs after 25 of April
                    for hash in dict[id]:
                        sentTime = dict[id][hash]
                        requested = datetime.datetime.strptime(sentTime, '%H:%M:%S')
                        delta = received - requested
                        if delta < datetime.timedelta(minutes=0):
                            delta = delta + datetime.timedelta(days=1)
                        if delta > datetime.timedelta(minutes=20):
                            outputBlockDelay = open(honeyNodeID+"/BlockTimeOuts.txt", "a")
                            outputBlockDelay.write(date + " " + currentTime + " Peer:" + id + " didn't response to block:" + hash + " \n")
                del dict[id]

        #if 'socket sending timeout:' in line or 'socket receive timeout:' in line: # To be removed for logs after 25 of April
            #inactive = True
    with open(honeyNodeID + '/Dict/dictBlockPropagationTrack.txt', 'w') as outfile:
        json.dump(dict, outfile)

def track_tx_propagation(buffer, dict, honeyNodeID):
    """
    Monitor the requested and received transactions from the peers:
        - track unsolicided transactions
        - monitor the delay between requested and received transactions

    :param buffer: lines of parsed log file to be processed
    :param dict: dictionary {id:{hash:time}}
    :param honeyNodeID: the ID of the honeynode the data is coming from
    :return:
    """
    outputTransactionDelay = open(honeyNodeID + "/TransactionDelayResults.txt", "a")
    outputUnsolicitedBlock = open(honeyNodeID + "/UnsolicitedTransactionHash.txt", "a")
    outputBlockDelay = open(honeyNodeID + "/TxTimeOuts.txt", "a")
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
                    outputTransactionDelay.write(date + " " + time + " transaction delay from peer:" + id + " delay:" + "".join(str(delta).replace(" -1 day, ", "")) + " \n")
                    del dict[id][hash]
                else:
                    outputUnsolicitedBlock.write(date + " Received transaction from peer: " + id + " with hash: " + hash + " is not coming from a recent getdata \n")

        elif 'Inactivity' in line:
            inactivePeer = parse.get_peer_id(line)

        elif 'disconnecting peer' in line:
            id = parse.get_peer_id(line)
            currentTime = parse.get_time(line)
            currentDate = parse.get_date(line)
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
                            outputBlockDelay.write(currentDate + " " + currentTime + " Peer:" + id + " didn't response to tx:" + hash + " \n")
                del dict[id]

        if 'socket sending timeout:' in line or 'socket receive timeout:' in line:  # To be removed for logs after 23 of April
            inactive = True
    with open(honeyNodeID + '/Dict/dictTXPropagationTrack.txt', 'w') as outfile:
        json.dump(dict, outfile)


def inactivity_check(buffer,dict):
    """
    Check if a peer disconnects due to inactivity
    :param buffer: lines of parsed log file to be processed
    :param dict:
    :return:
    """
    for line in buffer:
        id = parse.get_peer_id(line)
        reason = parse.get_inactivity_reason(line)
        dict[id] = reason

def version_check(buffer,dict):
    """

    :param buffer:
    :param dict:
    :return:
    """
    for line in buffer:
        id = parse.get_peer_id(line)
        version = parse.get_version(line)
        dict[id] = version


def get_msg_provenance(buffer,honeyNodeID):
    """
    Keep track of the IP addresses of the sender of the protocol messages
    :param buffer:
    :param honeyNodeID:
    :return:
    """
    try:
        with open(honeyNodeID+'/Dict/activePeers.txt', 'r') as jsonPeer:
            activePeers=json.load(jsonPeer)
    except IOError:
        activePeers = {}
    outputGETADDR = open(honeyNodeID+"/GETADDRResults.txt", "a")
    outputINV = open(honeyNodeID + "/INVResults.txt", "a")
    for line in buffer:
        if "Added" in line:
            id = parse.get_peer_id(line)
            version, ip, port = parse.get_ip_port(line)
            addr = ip+":"+port
            activePeers[id] = addr
        if "disconnecting peer" in line:
            id = parse.get_peer_id(line)
            if id in activePeers.keys():
                activePeers.pop(id)
        if 'received: getaddr' in line or '"getaddr"' in line:
            v,ip,id = parse.get_ip_port(line)
            if ip:
                outputGETADDR.write("".join(line))
            else:
                id = parse.get_peer_id(line)
                addr = activePeers[id]
                line = line.strip('\n')
                outputGETADDR.write("".join(line)+" IP:Port="+"".join(addr)+"\n")
        if 'received: inv' in line:
            v,ip,id = parse.get_ip_port(line)
            if ip:
                outputINV.write("".join(line))
            else:
                id = parse.get_peer_id(line)
                addr = activePeers[id]
                line = line.strip('\n')
                outputINV.write("".join(line)+" IP:Port="+"".join(addr)+"\n")

    with open(honeyNodeID+'/Dict/activePeers.txt', 'w') as outfile:
        json.dump(activePeers, outfile)


def getaddr_message(dict):
    """
    Convert data of received GETADDR message in a format that is compatible with the plot tools of the dashboard
    :param dict:
    :return:
    """
    day = 0
    xas =[]
    data = {}
    for key in dict:
        date = datetime.datetime.strptime(key,'%Y-%m-%d')
        xas.append(date)
        for source in dict[key]:
            if source not in data:
                data[source] = []
                for j in range(0,day,1):
                    data[source].append(0)
                data[source].append(dict[key][source])
            else:
                while len(data[source]) < day:
                    data[source].append(0)
                data[source].append(dict[key][source])
        day=day+1
    return data, xas


def get_AS_leaders(time):
    """
    returns a list of numbers of peers belonging to each AS on a given time
    :param time: timestamp in unix format
    :return: a list of [AS,organisation,Nb]
    """
    date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d_%H_%M_%S')
    with open('ALL_snaps/Organization_AS_map/Organization_AS_map_' + date + '.pickle', 'rb') as handle:
        map = pickle.load(handle)

    with open('ALL_snaps/AS_snaps/AS_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
        dictNb = pickle.load(handle)

    list =[]

    for AS in sorted(dictNb, key=dictNb.get, reverse=True):
        Nb =dictNb[AS]
        for organisation in map:
            if AS in map[organisation]:
                list.append([AS,organisation,Nb])
                break
    return list



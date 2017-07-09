#!/usr/bin/env python

# File name:            API.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This file makes use of the API of Bitnodes.21 to:
    - Check the correctness of the propagated IP:PORT combination
    - Regularly retreive a snapshot of the actif nodes and extract information about AS and Provider. Save this
      information in the form of a dictionary

"""
import json
import urllib2
import re
import datetime
import pickle

def check_port(ip, port):
    """
    Check the correctness of the given IP:Port combination with the API of BITNODES.21
    :param ip: IP address of the node to check
    :param port: port of the node to check
    :return: If an IP:Port combination doesn't pass the validity check, the reason is logged in IPPortResults.txt file
    """
    ## Retrieve most two recent snapshots from BITNODES.21
    try:
        json_request = urllib2.urlopen('https://bitnodes.21.co/api/v1/snapshots/')
    except urllib2.HTTPError, e:
        print e.code
        return
    except urllib2.URLError, e:
        print e.args
        return

    request = json.load(json_request)
    urlLastSnap = request['results'][0]['url']

    try:
        json_data = urllib2.urlopen(''+urlLastSnap+'')
    except urllib2.HTTPError, e:
        print e.code
        return
    except urllib2.URLError, e:
        print e.args
        return

    data = json.load(json_data)

    # Parse JSON to get list of IP's
    IPlist = data['nodes'].keys()

    # Pattern
    pattern = re.compile("(([0-9]{1,3}\.){3}[0-9]{1,3}):(\d{1,5})|((\[(([a-zA-Z0-9]{0,4}:){1,7}([a-zA-Z0-9]{0,4}))\]):(\d{1,5}))")

    # Open file in append mode where results are stored
    outputIPPort = open("IPPortResults.txt", "a")

    monitoredport = []
    ## Check if IP:PORT is in database
    ## When no match, check if no match because PORT is wrong or IP not listed
    for line in IPlist:
        if re.search(pattern, line):
            if (pattern.match(line).group(1)):
                if (ip ==pattern.match(line).group(1)):
                    if (port == pattern.match(line).group(3)):
                        return
                    monitoredport.append(pattern.match(line).group(3))
            elif (pattern.match(line).group(5)):
                if (ip ==pattern.match(line).group(5)):
                    if (port == pattern.match(line).group(9)):
                        return
                    monitoredport.append(pattern.match(line).group(9))
    if monitoredport:
        outputIPPort.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " IP address " + ip + " has wrong port: " + port + " instead of " + "".join(monitoredport) +"\n")
    else:
        outputIPPort.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " IP address " + ip + " is not listed in the last snapshot of bitnodes.21 \n")


def parse_snapshot(snapshot,timestamp,directory):
    """
    Extract from the given snapshot:
        - the number of nodes for each AS and saved in a dictionary format in AS_nb_dict_snapshot_date.pickle file
        - the list of IP:Ports for each AS and saved in a dictionary foramt in AS_ip_dict_snapshot_date.pickle file
        - the number of nodes for each organization and saved in a dictionary format in Organization_nb_dict_snapshot_date.pickle file
        - the list of IP:Ports for each organization and saved in a dictionary foramt in Organization_ip_dict_snapshot_date.pickle file
        - the number of nodes for each protocol version and save in an dictionary
        - a dictionary mapping for each AS number, the name of the organisation holding the AS

    :param snapshot: a snapshot from bitnodes.21.co
    :param timestamp: the timestamp in a unix format of the snapshot
    :param directory: the directory where the processed snapshot has to be saved
    :return:
    """
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = urllib2.Request(snapshot, headers=hdr)

    try:
        json_data = urllib2.urlopen(req)
    except urllib2.URLError, e:
        print e.fp.read()
        return

    data = json.load(json_data)
    IPlist = data['nodes'].keys()
    dictASNb = {}
    dictOrganizationNb = {}
    dictASIp = {}
    dictOrganizationIp = {}
    dictVersionNb = {}
    dictASOrganisationMap ={}
    timestamps = []

    for i in IPlist:
        version = data['nodes'][i][1]
        ASnumber =  data['nodes'][i][11]
        organization = data['nodes'][i][12]

        # Update AS dictionary
        if ASnumber not in dictASNb:
            dictASNb[ASnumber] = 1
        else:
            j = dictASNb[ASnumber]
            j = j+1
            dictASNb[ASnumber] = j

        if ASnumber not in dictASIp:
            dictASIp[ASnumber] = []
            dictASIp[ASnumber].append(i)
        else:
            dictASIp[ASnumber].append(i)


        # Update provider dictionary
        if organization not in dictOrganizationNb:
            dictOrganizationNb[organization] = 1
        else:
            j = dictOrganizationNb[organization]
            j = j + 1
            dictOrganizationNb[organization] = j

        if organization not in dictOrganizationIp:
            dictOrganizationIp[organization] = []
            dictOrganizationIp[organization].append(i)
        else:
            dictOrganizationIp[organization].append(i)

        if organization not in dictASOrganisationMap:
            dictASOrganisationMap[organization] = []
            dictASOrganisationMap[organization].append(ASnumber)
        else:
            if ASnumber not in dictASOrganisationMap[organization]:
                dictASOrganisationMap[organization].append(ASnumber)


        # Update Version dictionary
        if version not in dictVersionNb:
            dictVersionNb[version] = 1
        else:
            j = dictVersionNb[version]
            j = j+1
            dictVersionNb[version] = j

    date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d_%H_%M_%S')
    timestamps.append(timestamp)

    with open(directory+'/AS_snaps/AS_nb_dict_snapshot_'+date+'.pickle', 'a') as ASoutput:
        pickle.dump(dictASNb, ASoutput, protocol=pickle.HIGHEST_PROTOCOL)

    with open(directory+'/AS_snaps/AS_ip_dict_snapshot_'+date+'.pickle', 'a') as ASipoutput:
        pickle.dump(dictASIp, ASipoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open(directory+'/Organization_snaps/Organization_nb_dict_snapshot_'+date+'.pickle', 'a') as Organizationoutput:
        pickle.dump(dictOrganizationNb, Organizationoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open(directory+'/Organization_snaps/Organization_ip_dict_snapshot_'+date+'.pickle', 'a') as Organizationipoutput:
        pickle.dump(dictOrganizationIp, Organizationipoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open(directory+'/Protocol/Protocol_nb_dict_snapshot_'+date+'.pickle', 'a') as versionoutput:
        pickle.dump(dictVersionNb, versionoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open(directory+'/Organization_AS_map/Organization_AS_map_'+date+'.pickle', 'a') as mapoutput:
        pickle.dump(dictASOrganisationMap, mapoutput,  protocol=pickle.HIGHEST_PROTOCOL)



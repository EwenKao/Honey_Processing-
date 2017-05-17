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

# Check the correctness of the given IP:PORT combination
# with the API of BITNODES.21
def check_port(ip, port):
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


# Extract from the given snapshot:
# the number of nodes for each AS and save in an dictionary
# the number of nodes for each Provider and save in an dictionary
def parse_snapshot(snapshot,timestamp):

    try:
        json_data = urllib2.urlopen('' + snapshot + '')
    except urllib2.URLError, e:
        return

    data = json.load(json_data)
    IPlist = data['nodes'].keys()
    dictASNb = {}
    dictOrganizationNb = {}
    dictASIp = {}
    dictOrganizationIp = {}
    dictVersionNb = {}

    for i in IPlist:
        version = data['nodes'][i][1]
        ASnumber =  data['nodes'][i][11]
        organization = data['nodes'][i][12]


        # Update AS dictionary
        if ASnumber not in dictASNb:
            dictASNb[ASnumber] = 1
        else:
            i = dictASNb[ASnumber]
            i = i+1
            dictASNb[ASnumber] = i

        if ASnumber not in dictASIp:
            dictASIp[ASnumber] = []
            dictASIp[ASnumber].append(i)
        else:
            dictASIp[ASnumber].append(i)

        # Update provider dictionary
        if organization not in dictOrganizationNb:
            dictOrganizationNb[organization] = 1
        else:
            i = dictOrganizationNb[organization]
            i = i + 1
            dictOrganizationNb[organization] = i

        if ASnumber not in dictOrganizationIp:
            dictOrganizationIp[organization] = []
            dictOrganizationIp[organization].append(i)
        else:
            dictOrganizationIp[organization].append(i)

        # Update Version dictionary
        if version not in dictVersionNb:
            dictVersionNb[version] = 1
        else:
            i = dictVersionNb[version]
            i = i+1
            dictVersionNb[version] = i

    date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    with open('AS_snaps/AS_nb_dict_snapshot_'+date+'.pickle', 'a') as ASoutput:
        pickle.dump(dictASNb, ASoutput, protocol=pickle.HIGHEST_PROTOCOL)

    with open('AS_snaps/AS_ip_dict_snapshot_'+date+'.pickle', 'a') as ASipoutput:
        pickle.dump(dictASIp, ASipoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open('Organization_snaps/Organization_nb_dict_snapshot_'+date+'.pickle', 'a') as Organizationoutput:
        pickle.dump(dictOrganizationNb, Organizationoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open('Organization_snaps/Organization_ip_dict_snapshot_'+date+'.pickle', 'a') as Organizationipoutput:
        pickle.dump(dictOrganizationIp, Organizationipoutput,  protocol=pickle.HIGHEST_PROTOCOL)

    with open('Protocol/Protocol_nb_dict_snapshot_'+date+'.pickle', 'a') as Organizationipoutput:
        pickle.dump(dictOrganizationIp, Organizationipoutput,  protocol=pickle.HIGHEST_PROTOCOL)
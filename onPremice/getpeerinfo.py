#!/usr/bin/env python

# File name:            getpeerinfo.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7


"""
Use the interactif Bitcoin cilient API calls to log info from the current peers.
    getconnetioncount
    getpeerinfo

Regularly check the round-trip time (RTT) from peers

"""

import subprocess
import json
import datetime


# bitcoin-cli calls
def log_peerinfo():

    # Collect data from bitcoin-cli API call
    try:
        subprocess.check_output("bitcoin-cli ping", stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError, e:
        print "Ping stdout output:\n", e.output

    NbPeers = json.loads(subprocess.check_output("bitcoin-cli getconnectioncount", stderr=subprocess.STDOUT, shell=True))
    getpeerinfo = json.loads(subprocess.check_output("bitcoin-cli getpeerinfo", stderr=subprocess.STDOUT, shell=True))

    # Log collected data
    log = {'logday': datetime.datetime.now().strftime('%Y-%m-%d'), 'logtime':datetime.datetime.now().strftime('%H:%M:%S'),'connectioncount': NbPeers, 'peers': getpeerinfo}

    with open("Logpeerinfo/logpeerinfo_"+datetime.datetime.now().strftime('%Y_%m_%d')+".txt", "a") as out:
        json.dump(log, out, indent=4)

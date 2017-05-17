#!/usr/bin/env python

# File name:            main.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This is the main file of the detection platform
"""
# Import build-in modules
import time
import os
import datetime


# Import self-written modules
import getpeerinfo
import API
import parse




# INITIALISATION create/ open files, declare globals and buffers
print "initialisation"
debugLog = 'debug.log'
bitcoinLog= open(debugLog ,'r+')
timestampList = []

# Create directories
try:
    os.makedirs("AS_snaps")
except OSError:
    pass

try:
    os.makedirs("Organization_snaps")
except OSError:
    pass

try:
    os.makedirs("Protocol")
except OSError:
    pass

try:
    os.makedirs("Logpeerinfo")
except OSError:
    pass

print "New directories made"

# REAL-TIME PROCESSING
# Find the size of the Log file and move to the end
st_results = os.stat(debugLog)
st_size = st_results[6]
# Set current position after the offset
bitcoinLog.seek(st_size)

lastTimeGetPeerInfo = time.time()
lastTimeSnapshot = time.time()
while 1:
    where = bitcoinLog.tell() # Current position of the file
    line = bitcoinLog.readline()
    if not line:
        time.sleep(1)
        bitcoinLog.seek(where)
    else:
        # PARSING LOG LINES
        # filter IP-addresses propagation
        if 'IP' in line and 'Port' in line and 'Added' in line:
            # Check if IP is not on wrong port
            version, ip, port = parse.get_ip_port(line)
            if ip:
                API.check_port(ip, port)

    # getpeerinfo every 2 min
    if ((time.time() - lastTimeGetPeerInfo) >= 120):
        lastTimeGetPeerInfo = time.time()
        datetime.datetime.now()
        print("Process time: " )
        print datetime.datetime.now().replace(microsecond=0)

        # Collect stats about peers
        print("Collect peerinfo ")
        getpeerinfo.log_peerinfo()

    # process snapshot once a day
    if ((time.time() - lastTimeSnapshot >= 86400)):
        lastTimeSnapshot = time.time()
        snaphot = 'https://bitnodes.21.co/api/v1/snapshots/latest'
        # Collect snapshot data
        API.parse_snapshot(snaphot,lastTimeSnapshot)



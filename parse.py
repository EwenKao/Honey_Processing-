#!/usr/bin/env python

# File name:            parse.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This file uses regular expressions to parse lines of log files and return the data that matches the pattern

List of functions:
    - get_time()
    - get_date()
    - get_ip_port()
    - get_peer_id()
    - get_size()
    - get_hash()
    - get_connection_time()
    - get_delay()
    - get_deconnection_reason()

"""

import re

# Returns the time in format hh:mm:ss of when the log line was written
def get_time(line):
    # group 1 = hh:mm:ss
    pattern = re.compile(".*([0-2][0-9]:[0-5][0-9]:[0-5][0-9])")
    result = re.search(pattern,line)
    if result:
        time = pattern.match(line).group(1)
        return time
    else:
        return None

# Returns the date in format yyyy-mm-dd of when the log line was written
def get_date(line):
    # group 1 = yyyy-mm-dd
    pattern = re.compile("([0-9]{4}-[0-1][0-9]-[0-3][0-9])")
    result = re.search(pattern, line)
    if result:
        time = pattern.match(line).group(1)
        return time
    else:
        return None

# Returns the IP-address, the port and the version (IPv4 or IPv6)
# found in a given log line
def get_ip_port(line):
    # group 1 = [IPv6]      group 6 = IPv4
    # group 2 = IPv6        group 8 = port
    # group 5 = port
    pattern = re.compile(".*?(\[(([a-zA-Z0-9]{0,4}:){1,7}([a-zA-Z0-9]{0,4}))\]):(\d{1,5})|.*?(([0-9]{1,3}\.){3}[0-9]{1,3}):(\d{1,5})")
    # PARSE: IP-addresses
    result = re.search(pattern, line)
    if result:
        if pattern.match(line).group(1):  # IPv6
            version = 6
            ip = pattern.match(line).group(1)
            port = pattern.match(line).group(5)
        else:
            version = 4
            ip = pattern.match(line).group(6)  # IPv4
            port = pattern.match(line).group(8)
        return [version, ip, port]
    else:
        return [None, None, None]

# Returns the ID of the peer foud in a give log line
def get_peer_id(line):
    # group 1 = peer=id     group 3 = Peer=id`
    # group 2 = id          group 4 = id
    pattern= re.compile(".*(peer=([^\s]+))|.*(Peer=([^\s]+))")

    result = re.search(pattern, line)
    if result:
        if pattern.match(line).group(2):
            id = pattern.match(line).group(2)
            if not id.isdigit():
                id = id[:-1]
        else:
            id = pattern.match(line).group(4)
        return id
    else:
        return None

# Returns the logged size of the message that has been send or received
def get_size(line):
    # group 1 = (size bytes)    group 2 size
    pattern = re.compile(".*(\(([^\s]+) bytes\))")

    result = re.search(pattern, line)
    if result:
        size = pattern.match(line).group(2)
        return size
    else:
        return None

# Returns the 64 bytes message digest of a SHA256 computation
# found in a given log line
def get_hash(line):
    # group 1 = hash
    pattern = re.compile(".*([a-f0-9]{64})")

    result = re.search(pattern, line)
    if result:
        hash = pattern.match(line).group(1)
        return hash
    else:
        return None

# Returns the connection duration of the peers
def get_connection_time(line):
    # group 1 = D days, HH:MM:SS
    #pattern = re.compile(".*time:(.*[0-9]{1,2}:[0-5][0-9]:[0-5][0-9])")
    # group 1 = D day, HH:MM:SS     group 6 = HH:MM:SS      group 10 = D days, HH:MM:SS
    # group 2 = D                   group 7 = HH            group 11 = D
    # group 3 = HH                  group 8 = MM            group 12 = HH
    # group 4 = MM                  group 9 = SS            group 13 = MM
    # group 5 = SS                                          group 14 = SS
    pattern = re.compile(".*time:((.*) day\, ([0-9]{1,2}):([0-5][0-9]):([0-5][0-9]))|.*time:(([0-9]{1,2}):([0-5][0-9]):([0-5][0-9]))|.*time:((.*) days\, ([0-9]{1,2}):([0-5][0-9]):([0-5][0-9]))")

    result = re.search(pattern, line)
    if result:
        if pattern.match(line).group(1):
            day = pattern.match(line).group(2)
            hours = pattern.match(line).group(3)
            min = pattern.match(line).group(4)
            sec = pattern.match(line).group(5)
        elif pattern.match(line).group(6):
            day = 0
            hours = pattern.match(line).group(7)
            min = pattern.match(line).group(8)
            sec = pattern.match(line).group(9)

        elif pattern.match(line).group(10):
            day = pattern.match(line).group(11)
            hours = pattern.match(line).group(12)
            min = pattern.match(line).group(13)
            sec = pattern.match(line).group(14)

        return [day,hours,min,sec]
    else:
        return [None,None,None,None]

def get_delay(line):
    # group 1 = HH      group 2 = MM        group 3 = SS
    pattern = re.compile(".*delay:([0-9]{1}):([0-5][0-9]):([0-5][0-9])")

    result = re.search(pattern, line)
    if result:
        hours = pattern.match(line).group(1)
        min = pattern.match(line).group(2)
        sec = pattern.match(line).group(3)
        return [hours, min, sec]
    else:
        return [None, None, None]

def get_deconnection_reason(line):
    # group 1 = reason
    pattern = re.compile(".*reason:(. *)")

    result = re.search(pattern, line)
    if result:
        reason = pattern.match(line).group(1)
        return reason
    else:
        return None

def get_inactivity_reason(line):
    pattern = re.compile(".*Inactivity,(.*)from")

    result = re.search(pattern, line)
    if result:
        reason = pattern.match(line).group(1)
        return reason
    else:
        return None

def get_version(line):
    pattern = re.compile(".*Satoshi:(.*)\/")
    result = re.search(pattern,line)
    if result:
        version = pattern.match(line).group(1)
        return version
    else:
        return None
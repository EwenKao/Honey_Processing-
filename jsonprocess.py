#!/usr/bin/env python

# File name:            jsonprocess.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
This file process the logpeeringo.txt log file written in json language. The following information are extracted:
    - The time of connection of each peer
    - The list of round-trip time of each peer
    - the type of connection inbound or outbound of each peer
"""

import datetime
import pickle




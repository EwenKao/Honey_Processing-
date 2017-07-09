#!/usr/bin/env python

# File name:            geckoboard.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
requirements:
    requests > 2.9.1
    pip install https://pypi.python.org/packages/2.7/r/requests/requests-2.9.1-py2.py3-none-any.whl

Use PUT requests to push data in a json format to the widgets of the dahboard.
The dashboard is publicly available on following link: https://share.geckoboard.com/dashboards/MKF6CPLIE6PETMBI
"""


import requests
import pickle
import datetime
import numpy

# Update general info about the Bitcoin network
def display_current_date(value,honeynodeID):
    """
    Display the date of the day when the processed data has been logged 
    :param value: current date
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'General':
        widgetKey = '171386-03507aa0-3406-0135-e8a0-22000bb5c791'
        text = 'Bitcoin status as of '
    elif honeynodeID == 'NYC' or honeynodeID == 'AMS':
        widgetKey = '168161-575cb4e0-25df-0135-6642-22000acbe644'
        text = 'Honeynode status as of '
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data' :
    {
      "item": [
        {
          "text": text +str(value),
          "type": 0
        }
      ]
    }})


def update_AS_graph(period,type):
    """

    :param period: dictionary where data is available
    :param type:
    :return:
    """

    timestamps = []
    times = open(period + '/timestamps.txt', 'r+')
    for line in times:
        line = line.strip('\n')
        timestamps.append(int(line))

    iterations = len(timestamps)

    dictData = {}
    xas = []

    for i in range(0, iterations, 1):
        date = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d_%H_%M_%S')
        try:
            with open(period + '/' + type + '_snaps/' + type + '_nb_dict_snapshot_' + date + '.pickle', 'rb') as handle:
                dictionary = pickle.load(handle)
        except IOError, e:
            print e

        xas.append(datetime.datetime.fromtimestamp(timestamps[i]))

        for key in dictionary:
            value = dictionary[key]
            if key in dictData.keys():
                if len(dictData[key]) == i - 1:
                    dictData[key].append(value)
                else:
                    while len(dictData[key]) < i - 1:
                        dictData[key].append(0)
                    dictData[key].append(value)
            else:
                dictData[key] = []
                for j in range(1, i):
                    dictData[key].append(0)
                dictData[key].append(value)
    geckoboard = []
    for key in sorted(dictData, key=dictData.get, reverse=True):
        value = dictData[key]
        pertinance = max(value) - min(value)
        # Select only relevant AS
        if numpy.mean(value) > 100:
            geckoboard.append({"name": key, "data": value})
        elif pertinance > 60:
            geckoboard.append({"name": key, "data": value})

    x = []
    for label in xas:
        x.append(label.isoformat() + "+02:00")

    if period == 'Last_Days_snaps':
        widgetKey = '171386-34d43b10-3409-0135-7711-22000a891cb1'
    elif period == 'ALL_snaps':
        if type == 'AS':
            widgetKey = '171386-10f26b80-3406-0135-77b8-22000acbe644'
        elif type == 'Organization':
            widgetKey = '168161-744823b0-1df7-0135-cfdc-22000bb5c791'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data': {
        "x_axis": {
            "type": "datetime",
            "labels": x
        },
        "series": geckoboard
    }})



def update_AS_leaderboard(list,mediumSuspect,highSuspect):
    """

    :param list:
    :param mediumSuspect: list of meduim suspected AS
    :param highSuspect: list of high suspected AS
    :return:
    """
    widgetKey = '171386-fc2ffdb0-340a-0135-771a-22000a891cb1'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    datalist = []
    for i in range(0,20,1):
        AS = list[i][0]
        name = list[i][0] + ": " + list[i][1]
        value = list[i][2]

        if AS in mediumSuspect.keys():
                datalist.append({"title": {"text": str(name)},
                                 "label": {"name": "Medium priority suspect",
                                           "color": "#ffa500"},
                                 "description": str(value)})
        elif AS in highSuspect.keys():
                datalist.append({"title": {"text": str(name)},
                                 "label": {"name": "High priority suspect",
                                           "color": "#ff0000"},
                                 "description": str(value)})
        else:
            datalist.append({"title":{"text":str(name)}, "description":str(value)})


    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data': datalist
    })

def update_AS_suspected_ip_list(highSuspect,date):
    """
    Push the IP addresses of highly suspected AS to the dashboard
    :param highSuspect: list of IP's belonging to highly suspected AS
    :param date: date of pocessing
    :return:
    """
    widgetKey= '171386-ae1d3240-340a-0135-7718-22000a891cb1'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    data = []
    with open('ALL_snaps/AS_snaps/AS_ip_dict_snapshot_' + date +'.pickle', 'rb') as handle:
        dictionary = pickle.load(handle)
    for AS in highSuspect:
        ips = dictionary[AS]
        for ip in ips:
            data.append({ "title":{"text": str(ip)},
                          "description": str(AS)})

    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data': data
                             })


#
def avg_cum_conntime(value,honeynodeID):
    """
    Push the average cumulative connection time to the dashboard
    :param value: the average cumulative connection time
    :param honeynodeID: geographic location of the honeynode
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-0f897130-3747-0135-eb16-22000bb5c791'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-d1243df0-3761-0135-00a7-22000aedfc71'

    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf',
                          'data':
                              {'item': [
                            {
                                'value': int(value),
                                'text': 'Cumulative avg connetion time'
                            }
                        ]
                    }})

def avg_day_conntime(value,date,honeynodeID):
    """
    Push the average connectiontime of the given day to the dashboard
    :param value: average connectiontime of the given day
    :param date: date of processing
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-5bb831d0-3747-0135-eb17-22000bb5c791'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-e6183250-3761-0135-7a67-22000acbe644'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf',
                                 'data':
                                     {'item': [
                                         {
                                             'value': int(value),
                                             'text': 'Avg connetcion time of the day '+date
                                         }
                                     ]
                                     }})

def avg_cum_blockdelay(value,honeynodeID):
    """
    Push the average cumulative delay between the request and delivery of blocks to the dashboard
    :param value: the average cumulative delay between the request and delivery of blocks
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-a85b2a90-3761-0135-7a66-22000acbe644'
    elif honeynodeID == 'AMS':
        widgetKey ='171386-edf2d7c0-3761-0135-931b-22000a2fcae5'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf',
                          'data':
                              {'item': [
                            {
                                'value': int(value),
                                'text': 'Cumulative avg block delay'
                            }
                        ]
                    }})


def avg_cum_txdelay(value,honeynodeID):
    """
    Push the average cumulative delay bewteen the request and delivery of transactions to the dashboard
    :param value: the average cumulative delay bewteen the request and delivery of transactions
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-c4d6f710-3761-0135-931a-22000a2fcae5'
    elif honeynodeID == 'AMS':
        widgetKey ='171386-fd5a2330-3761-0135-79b7-22000a891cb1'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf',
                          'data':
                              {'item': [
                            {
                                'value': int(value),
                                'text': 'Cumulative avg tx delay'
                            }
                        ]
                    }})

def update_getaddr_chart(x,y,honeynodeID):
    """
    Update the dashboard with the number of received GETADDR messages
    :param x: list of dates
    :param y: list of amount of received GETADDR messages
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-100c8430-3762-0135-7a68-22000acbe644'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-1c1fe770-3762-0135-931c-22000a2fcae5'

    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf','data':{
    "x_axis": {
        "type": "datetime",
        "labels": x
    },
      "series": [
        {
          "data": y
        }
      ]
    }})


def getaddr_list(dict,honeynodeID):
    """
    Push the IP address of the peer that sent an abnormal amount of GETADDR (more than 5 on the same day)
    :param dict: dictionary containing for each IP address, the number of GETADDR messages sent by this IP address
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-54aa6920-3762-0135-7a69-22000acbe644'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-65c65280-3762-0135-931f-22000a2fcae5'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    data =[]
    for date in sorted(dict, reverse=True):
        for ip in dict[date]:
            if dict[date][ip] > 5:
                data.append({"title":{"text": ip},"description": "sent " +str(dict[date][ip])+ " GETADDR messages on " +str(date)})

    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data': data
    })

def update_inv_chart(x,y,honeynodeID):
    """
    Update the dashboard with the number of received INV messages
    :param x: list of dates
    :param y: list of amount of received INV messages
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-2ff65c50-3762-0135-931e-22000a2fcae5'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-3d147140-3762-0135-eb41-22000bb5c791'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf','data':{
    "x_axis": {
        "type": "datetime",
        "labels": x
    },
      "series": [
        {
          "data": y
        }
      ]
    }})

def update_addr_chart(x,y,honeynodeID):
    """
    Update the dashboard with the number of received ADDR messages
    :param x: list of dates
    :param y: list of amount of received ADDR messages
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-a88e06d0-3762-0135-9320-22000a2fcae5'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-b440dec0-3762-0135-7a6b-22000acbe644'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf','data':{
    "x_axis": {
        "type": "datetime",
        "labels": x
    },
      "series": [
        {
          "data": y
        }
      ]
    }})

def update_connection_nb(x,y,honeynodeID):
    """
    Update the dashboard with the number of connection kept by the honeynode
    :param x: list of date
    :param y: list of amount of connected peers
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-c42843f0-3762-0135-00ae-22000aedfc71'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-94253ae0-3762-0135-7a6a-22000acbe644'

    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'25537648ec0b44a180b3169cf699dccf','data':{
      "x_axis": {
        "type": "datetime",
          "labels": x
      },
      "series": [
        {
            "data": y
        }
      ]
    }})

def update_peer_list(dictionary,honeynodeID):
    """
    Update the dashboard with a list containing the IP addresses of the peers
    :param dictionary: key: peer id, value: IP address
    :param honeynodeID: the ID of the honeynode the data is coming from
    :return:
    """
    if honeynodeID == 'NYC':
        widgetKey = '171386-71f12050-3762-0135-00ab-22000aedfc71'
    elif honeynodeID == 'AMS':
        widgetKey = '171386-7cbe90a0-3762-0135-00ac-22000aedfc71'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    data = []
    for id in sorted(dictionary):
        if dictionary[id]["type"] == 'peer':
            ip = dictionary[id]["ip"]
            data.append({"title":{"text":"peer IP "+str(ip)}, "description" : "ID "+str(id)})

    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data':data})

def update_protocol_pie(date):
    """
    Update the dashboard with the protocols used by the reachable nodes of the network
    :param date: date of snapshot
    :return:
    """
    widgetKey = '171386-b9893330-3761-0135-eb3e-22000bb5c791'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    with open('ALL_snaps/Protocol/Protocol_nb_dict_snapshot_' + date +'.pickle', 'rb') as handle:
        dict = pickle.load(handle)
        data =[]
        dictSortedKeys = sorted(dict, key=dict.get, reverse=True)
        total= sum(dict.values())
        for key in dictSortedKeys:
            if dict[key] > 100:
                if key == '/Free the Markets - Free the People - https://btcpop.co /BitcoinUnlimited:1.0.2(EB16; AD12)/':
                    perc = dict[key]*100/total
                    data.append({"value":perc,"label":str(perc)+'% ' +'/BitcoinUnlimited:1.0.2(EB16; AD12)/'})
                else:
                    perc = dict[key] * 100 / total
                    data.append({"value": perc, "label": str(perc)+'% ' +key})

    requests.post(url, json={'api_key': '25537648ec0b44a180b3169cf699dccf', 'data':{
      "item": data
    }})





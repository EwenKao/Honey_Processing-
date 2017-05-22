#!/usr/bin/env python

# File name:            geckoboard.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
requirements:
    requests > 2.9.1
    pip install https://pypi.python.org/packages/2.7/r/requests/requests-2.9.1-py2.py3-none-any.whl

Main file that:
    - use PUT requests to push data in a joson format to the wodget of the dahboard
"""


import requests
import pickle


def display_current_date(value):
    widgetKey = '168161-63ac6eb0-1f86-0135-e69d-22000aedfc71'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url, json={'api_key': '7b2085513d88b615146903afb360e785', 'data' :
    {
      "item": [
        {
          "text": str(value),
          "type": 0
        }
      ]
    }})


def avg_cum_conntime(value):
    widgetKey = '168161-bb344910-1cfc-0135-5d53-22000acbe644'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'7b2085513d88b615146903afb360e785',
                          'data':
                              {'item': [
                            {
                                'value': int(value),
                                'text': 'Cumulative avg connetion time'
                            }
                        ]
                    }})

def avg_day_conntime(value,date):
    widgetKey = '168161-c664a400-1d30-0135-cebc-22000bb5c791'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url, json={'api_key': '7b2085513d88b615146903afb360e785',
                                 'data':
                                     {'item': [
                                         {
                                             'value': int(value),
                                             'text': 'Avg connetcion time of the day '+date
                                         }
                                     ]
                                     }})

def update_getaddr_chart(x,y):
    widgetKey = '168161-5c0f71d0-1d45-0135-5ded-22000acbe644'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    requests.post(url,json={'api_key':'7b2085513d88b615146903afb360e785','data':{
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

def update_connection_nb(x,y,location):

    if location == 'NYC':
        widgetKey = '168161-535dbb80-1cee-0135-5d40-22000acbe644'
    elif location == 'AMS':
        widgetKey = '168161-48a93d10-2153-0135-e7b0-22000aedfc71'

    url = 'https://push.geckoboard.com/v1/send/' + widgetKey
    requests.post(url,json={'api_key':'7b2085513d88b615146903afb360e785','data':{
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

def peers_of_the_day():
    widgetKey = '168161-45f431c0-1d86-0135-5e43-22000acbe644'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    r = requests.post(url, json={'api_key': '7b2085513d88b615146903afb360e785', 'data':
        [
  {
    "title": {
      "text": "Chrome"
    },
    "label": {
      "name": "New!",
      "color": "#ff2015"
    },
    "description": "40327 visits"
  },
  {
    "title": {
      "text": "Safari"
    },
    "description": "11577 visits"
  },
  {
    "title": {
      "text": "Firefox"
    },
    "description": "10296 visits"
  },
  {
    "title": {
      "text": "Internet Explorer"
    },
    "description": "3587 visits"
  },
  {
    "title": {
      "text": "Opera"
    },
    "description": "499 visits"
  }
]
    })

def update_protocol_pie(date):
    widgetKey = '168161-dd3b8e10-1d4f-0135-e3e8-22000aedfc71'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey

    with open('Protocol/Protocol_nb_dict_snapshot_' + date +'.pickle', 'rb') as handle:
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

    r=requests.post(url, json={'api_key': '7b2085513d88b615146903afb360e785', 'data':{
      "item": data
    }})
    print r

update_protocol_pie('2017-05-18')

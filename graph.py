#!/usr/bin/env python

# File name:            graph.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
Plot processed data and statistics

"""
import math

import plotly
import pickle
import datetime
import numpy
import json
import requests
import statistics
import process

def AS_graph(period,type):
    """

    :param time:
    :return:
    """

    timestamps =[]
    times =open(period+'/timestamps.txt','r+')
    for line in times:
        line = line.strip('\n')
        timestamps.append(int(line))

    iterations = len(timestamps)

    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')

    dictData = {}
    data =[]
    xas=[]

    for i in range(0,iterations,1):
        date = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d_%H_%M_%S')
        try:
            with open(period+'/'+type+'_snaps/'+type+'_nb_dict_snapshot_'+date+'.pickle', 'rb') as handle:
                dictionary = pickle.load(handle)
        except IOError,e:
            print e

        print str(i*100/iterations) + '%'
        xas.append(datetime.datetime.fromtimestamp(timestamps[i]))

        for key in dictionary:
            value = dictionary[key]
            if key in dictData.keys():
                if len(dictData[key]) == i-1:
                    dictData[key].append(value)
                else:
                    while len(dictData[key]) < i-1:
                        dictData[key].append(0)
                    dictData[key].append(value)
            else:
                dictData[key] = []
                for j in range(1,i):
                    dictData[key].append(0)
                dictData[key].append(value)
    geckoboard = []
    for key in sorted(dictData, key=dictData.get, reverse=True):
        value = dictData[key]
        pertinance = max(value) - min(value)
        # Select only relevant AS
        if numpy.mean(value) > 100:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key, line=dict(width = 3)))
            geckoboard.append({"name": key, "data": value})
        elif pertinance > 60:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key, line=dict(width = 3)))
            geckoboard.append({"name": key, "data": value})

    layout = plotly.graph_objs.Layout(
        title='Number of nodes per '+type,
        titlefont=dict(
            size=44,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(
            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(

            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            #x=-1.0,
            #y=1.0,
            font=dict(
                size=30
            )
        ))

    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    plotly.plotly.plot(fig, filename='relevant-AS-feb-april')

    x = []
    for label in xas:
        x.append(label.isoformat() + "+02:00")

    if period == 'Last_Days_snaps':
        widgetKey = '168161-ecffd3a0-1df9-0135-e4ce-22000aedfc71'
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

def organisation_graph(period):
    """

    :param period:
    :return:
    """
    timestamps = []
    times = open(period + '/timestamps.txt', 'r+')
    for line in times:
        line = line.strip('\n')
        timestamps.append(int(line))

    iterations = len(timestamps)

    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')


    dictData = {}
    data =[]
    xas=[]


    for i in range(0,iterations,1):
        date = datetime.datetime.fromtimestamp(timestamps[i]).strftime('%Y-%m-%d')
        try:
            with open(period+'/Organization_snaps/Organization_nb_dict_snapshot_'+date+'.pickle', 'rb') as handle:
                dictionary = pickle.load(handle)

        except IOError,e:
            print e

        print str(i*100/iterations) + '%'
        xas.append(datetime.datetime.fromtimestamp(timestamps[i]))

        for key in dictionary:
            value = dictionary[key]
            if key in dictData.keys():
                if len(dictData[key]) == i-1:
                    dictData[key].append(value)
                else:
                    while len(dictData[key]) < i-1:
                        dictData[key].append(0)
                    dictData[key].append(value)
            else:
                dictData[key] = []
                for j in range(1,i):
                    dictData[key].append(0)
                dictData[key].append(value)

    geckoboard =[]
    for key in dictData:
        value = dictData[key]
        while len(value) < 80:
            value.append(0)
        pertinance = max(value) - min(value)
        # Select only relevant AS
        if numpy.mean(value) > 100:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))
            geckoboard.append({"name":key,"data":value})

        elif pertinance > 60:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))
            geckoboard.append({"name": key, "data": value})

    layout = plotly.graph_objs.Layout(
        title='Number of nodes per organisation',
        titlefont=dict(
            size=34,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(
            title='time',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=24
            )
        ))

    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    plotly.plotly.plot(fig, filename='relevant-Providers-feb-april')


    x = []
    for label in xas:
        x.append(label.isoformat()+"+02:00")

    widgetKey = '168161-744823b0-1df7-0135-cfdc-22000bb5c791'
    url = 'https://push.geckoboard.com/v1/send/' + widgetKey



    requests.post(url, json={'api_key': '7b2085513d88b615146903afb360e785', 'data': {
      "x_axis": {
          "type": "datetime",
          "labels": x
      },
      "series": geckoboard
    }})

def RTT_graph(date,filename):
    y = []
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')
    with open('Peers/RTTstats/RTTstats_' + date + '.txt', 'rb') as handle:
        dictionary = pickle.load(handle)

    with open("Peers/RTTlogtimes/RTTlogtimes_"+date+".txt", "rb") as t:
        times = [line.rstrip('\n') for line in t]
        [datetime.datetime.strptime(a, '%H:%M:%S') for a in times]

    data = []
    data.append(plotly.graph_objs.Scatter(x=times, y=0, showlegend=False))
    for key in dictionary:
        values = dictionary[key]
        i=0
        for ping in values:
            if ping < 0.5:
                y.append(values[i])
            else:
                y.append("")
            i+=1
        data.append(plotly.graph_objs.Scatter(x=times,y=y, name=key))
        x = []
        y = []

    layout = plotly.graph_objs.Layout(
        title='round-trip-time 07 May',
        titlefont=dict(
            size=50,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(

            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='delay',
            titlefont=dict(
                size=36,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=34
            )
        ))

    fig = plotly.graph_objs.Figure(data=data,layout=layout)
    plotly.plotly.plot(fig, filename=filename)

def connections_graph():
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')
    with open('dictConnectionNb.txt', 'rb') as handle:
        dictionary = json.load(handle)
    data = []
    x =[]
    y =[]
    [datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S') for a in dictionary]
    for key in sorted(dictionary):
        x.append(key)
        y.append(dictionary[key])

    data.append(plotly.graph_objs.Scatter(x=x,y=y))

    layout = plotly.graph_objs.Layout(
        title='Number of active peers',
        xaxis=dict(
            title='time',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        )
    )

    fig = plotly.graph_objs.Figure(data=data, layout=layout)

    plotly.plotly.plot(fig, filename='Active peers intime')

def getaddr_graph():
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')
    times, values, dictionary = statistics.message_list_format('NYC','GETADDR')
    dictdata,xas = process.getaddr_message(dictionary)
    data =[]
    for key in dictdata:
        data.append(plotly.graph_objs.Bar(x=xas,y=dictdata[key],name=key))

    layout = plotly.graph_objs.Layout(
        title='Received GETADDR messages',
        titlefont=dict(
            size=44,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(
            title='time',
            titlefont=dict(
                size=36,
                color='rgb(107, 107, 107)'
            ),

            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                size=36,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=32,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=34
            )
        ),
        barmode='stack'
    )

    fig = plotly.graph_objs.Figure(data=data, layout=layout)
    plotly.plotly.plot(fig, filename='addr')


#organisation_graph(1479556800)

def check(x,y):
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')
    i =0
    data = []
    for item in x:
        data.append(plotly.graph_objs.Bar(x=i,y=y[i],name=str(x[i])))
        i=i+1


    layout = plotly.graph_objs.Layout(
        title='Number of active peers',
        xaxis=dict(
            title='time',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=24
            )
        )
    )

    fig = plotly.graph_objs.Figure(data=data, layout=layout)

    plotly.plotly.plot(fig, filename='Active peers intime')

def connections(x,y):
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')

    data=[]
    data.append(plotly.graph_objs.Scatter(x=x, y=y))

    layout = plotly.graph_objs.Layout(
        title='Number of Peers',
        titlefont=dict(
            size=34,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(
            title='time',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),

            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=24
            )
        )
    )

    fig = plotly.graph_objs.Figure(data=data, layout=layout)

    plotly.plotly.plot(fig, filename='connected peers')

def line(dictionary,xas):
    plotly.tools.set_credentials_file(username='sarahlouise11', api_key='StPbPMsI3Ddha5Q0JuGU')
    data =[]
    xdata =[]
    yinner = []
    youter = []
    for x in xas:
        xdata.append(datetime.datetime.fromtimestamp(x).isoformat())
        yinner.append(34.30)
        youter.append(64.20)
    for key in dictionary:
        data.append(plotly.graph_objs.Scatter(x=xdata, y=dictionary[key],mode = 'markers', name = key, ))

    data.append(plotly.graph_objs.Scatter(x=xdata, y=yinner, name='inner fence', mode = 'lines+text',line = dict(
        color = ('rgb(0, 0, 0)'),
        width = 3), text=['Inner fence'],textposition='top right',textfont=dict(
        size=20,
        color=('rgb(0, 0, 0)')
    ), showlegend=False))
    data.append(plotly.graph_objs.Scatter(x=xdata, y=youter, name='outer fence', mode = 'lines+text',line = dict(
        color = ('rgb(0, 0, 0)'),
        width = 3), text=['Outer fence'],textposition='top right',textfont=dict(
        size=20,
        color=('rgb(0, 0, 0)')
    ), showlegend=False))

    layout = plotly.graph_objs.Layout(
        title='Result of Peer-detection',
        titlefont=dict(
            size=34,
            color='rgb(107, 107, 107)'
        ),
        xaxis=dict(
            title='time',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),

            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        yaxis=dict(
            title='amount',
            titlefont=dict(
                size=26,
                color='rgb(107, 107, 107)'
            ),
            tickfont=dict(
                size=22,
                color='rgb(107, 107, 107)'
            )
        ),
        legend=dict(
            x=0,
            y=1.0,
            font=dict(
                size=24
            )
        )
    )

    fig = plotly.graph_objs.Figure(data=data, layout=layout)

    plotly.plotly.plot(fig, filename='peak')

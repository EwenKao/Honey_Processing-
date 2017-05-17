#!/usr/bin/env python

# File name:            graph.py
# Author:               Sarah-Louise Justin
# e-mail:               sarahlouise.justin@student.kuleuven.be
# Python Version:       2.7

"""
Plot processed data and statistics

"""

import plotly
import pickle
import datetime
import numpy
import json

def AS_graph(time):

    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')

    dictData = {}
    data =[]
    xas=[]
    iterations = 187

    for i in range(1,iterations,1):
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        try:
            with open('AS_snaps/AS_nb_dict_snapshot_'+date+'.txt', 'rb') as handle:
                dict = pickle.load(handle)
        except IOError,e:
            print e

        time = time + 86400
        print str(i*100/iterations) + '%'
        xas.append(datetime.datetime.fromtimestamp(time))

        for key in dict:
            value = dict[key]
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

    for key in dictData:
        value = dictData[key]
        while len(value) < 80:
            value.append(0)
        pertinance = max(value) - min(value)
        # Select only relevant AS
        if numpy.mean(value) > 100:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))

        elif pertinance > 50:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))

    plotly.plotly.plot(data, filename='relevant-AS-feb-april')

def organisation_graph(time,index):

    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')

    dictData = {}
    data =[]
    xas=[]
    iterations = index/2

    for i in range(1,iterations,1):
        date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        index = index -2
        try:
            with open('Provider_nb_dict_snapshot_'+date+'_'+str(index)+'.pickle', 'rb') as handle:
                dict = pickle.load(handle)
        except IOError,e:
            time = time + 86400
            date = datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d')
            with open('Provider_nb_dict_snapshot_'+date+'_'+str(index)+'.pickle', 'rb') as handle:
                dict = pickle.load(handle)

        print str(i*100/iterations) + '%'
        xas.append(datetime.datetime.fromtimestamp(time))

        for key in dict:
            value = dict[key]
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

    for key in dictData:
        value = dictData[key]
        while len(value) < 80:
            value.append(0)
        pertinance = max(value) - min(value)
        # Select only relevant AS
        if numpy.mean(value) > 100:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))

        elif pertinance > 50:
            data.append(plotly.graph_objs.Scatter(x=xas, y=value, name=key))

    plotly.plotly.plot(data, filename='relevant-Providers-feb-april')


def RTT_graph(date,filename):

    x = []
    y = []
    plotly.tools.set_credentials_file(username='ASgraphs', api_key='tygulSRh6C3QKYIrlgsg')
    with open('Peers/RTTstats_' + date + '.txt', 'rb') as handle:
        dictionary = pickle.load(handle)

    with open("Peers/RTTlogtimes_"+date+".txt", "rb") as t:
        times = [line.rstrip('\n') for line in t]
        [datetime.datetime.strptime(a, '%H:%M:%S') for a in times]

    data = []
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
        title='round-trip-time '+date,
        xaxis=dict(
            title=date,
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        ),
        yaxis=dict(
            title='delay',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
            )
        )
    )

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
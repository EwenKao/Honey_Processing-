
import graph
import API
import urllib2
import datetime
import json
import statistics
import quickspikes
import peerloganalyser
#timestamp =


#ipcheck.AS_provider_stats_of_snapshot('https://bitnodes.21.co/api/v1/snapshots/', timestamp)
#graph.RTT_graph()

# Generate Snapshot between december and april
def draw():
    timestamp = 1478260800
    index = 481
    graph.AS_graph(timestamp)


# Generate a snapshot every 20 to 24 hours from now back to given input date
# given timestamp must be in a unix format
# input snapshotNb is max 481
def generate_AS_Organization_data(snapshotNb):
    for i in range(1,snapshotNb,1):
        print i
        url = 'https://bitnodes.21.co/api/v1/snapshots/?page='+str(i)+'&limit=100'
        try:
            snapshotList = urllib2.urlopen('' + url + '')
        except urllib2.URLError, e:
            print i
            print e
            break
        jsonList = json.load(snapshotList)
        urlSnap = jsonList['results'][0]['url']
        timestamp = jsonList['results'][0]['timestamp']
        API.parse_snapshot(urlSnap, timestamp)



#generate_AS_Organization_data(500)

"""
print "start generating data"
generate_AS_Organization_data(500)
print "data generation completed"
print "drawing"
draw()
print "start peak detection"
#stats.peak_detection(207)
time = 1492516800
list =[]
while time <= 1494244800:
    list.append(time)
    if len(list) > 5:plotly.graph_objs.
        del list[0]
    stats.peak_detection(list,'AS')
    time = time +86400

#stats.stdev_AS_mean()
"""

"""
date = '2017-05-05'
filename = 'rtt_'+date
graph.RTT_graph(date,filename)

# Prepare the LOGPEERINFO.TXT file to be processed
peerloganalyser.init()
# Process the json formatted logfile AFTER 16 MAY
#date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y_%m_%d")
json_log = open("logpeerjson.txt", "r+")
log = json.load(json_log)
peerloganalyser.json_parse(log)


#statistics.stdev_AS_mean()

#19-11-2016
t=[1479556800, 1479643200, 1479729600, 1479816000, 1479902400]
for i in range(0,500,1):
    statistics.peak_detection(t,'AS')
    newt = t[-1]
    newt = newt+86400
    t.append(newt)
    t.pop(0)

"""
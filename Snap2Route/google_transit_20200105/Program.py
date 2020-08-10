import pandas as pd
import requests
import numpy
import os
import math


#           Function that takes a bread crumb data frame and formats all gps coordinates into a google api request
def Formatter(frame):
    request = "https://roads.googleapis.com/v1/snapToRoads?path="
    print("forming request")
    for index, row in frame.iterrows():
        request += (str(row['GPS_LATITUDE']) + "," + str(row['GPS_LONGITUDE']) + "|")
    request = request[:-1]
    request += "&key=" + os.environ['ROADS_API']
    return request


#               Read in data
pd.set_option('display.max_colwidth', 100)
frame = pd.read_csv('../bos_2020030206.tsv', delimiter='\t')
singletrip = frame.loc[frame['EVENT_NO_TRIP'] == 152570206]

<<<<<<< HEAD
#           length var to see how many hundreds of GPS points are in trip
length = int(len(singletrip)/100)+1
=======
          #length var to see how many hundreds of GPS points are in trip
length = int(math.ceil(len(singletrip)/100))
#length = int(len(singletrip)/100)+1
>>>>>>> fed450c... Updated Program.py for the length logic
googlerequests = []
first = 0
last = 5
locationsList = [] #[('latitude', 'longitude', 'data origin')]
interCounter = 0
indexCounter = 0


#           Loop to send 100 or less coordinates at a time to be formatted
for x in range (0, length):
    googlerequests.append(Formatter(singletrip[first:last]))
    first += 5
    last += 5
<<<<<<< HEAD
print("printing request")
for x in range (0,length):
    print(googlerequests[x])
=======
    #first += 100
    #last += 100
singletripList = singletrip.values.tolist()
print("Printing original list")
print(singletripList)
#print("printing request")
# for x in range (0,length):
#     print(googlerequests[x])
>>>>>>> fed450c... Updated Program.py for the length logic
print("sending request")

for x in range (0, len(googlerequests)):
    response = requests.post(googlerequests[x])
    print("printing response")
    print(str(response.status_code) + " response from " + response.url)
    print(response.json())
    jsonResponse = response.json()
    snappedPoint = jsonResponse['snappedPoints']


    print("length of json" + str(len(snappedPoint)))
    for y in range (0, len(snappedPoint)):
        snap = snappedPoint[y]
        print(snap)
        location =  snap['location']
        latitude = location['latitude']
        longitude = location['longitude']
        #orignialIndex = location['originalIndex']
        print(  "length of snap " + str(len(snap)))
        if len(snap) < 3:
            locationsList.append([latitude, longitude, 'interpolated'+ str(interCounter)])
            interCounter += 1
        else:
            locationsList.append([latitude, longitude, 'originalIndex' + str(indexCounter)])
            indexCounter += 1
    print(locationsList)
    print(len(locationsList))
locationFrame = pd.DataFrame(locationsList, columns = ["latitude", "longitude", "data origin"])
# header = locationFrame.iloc[0]
# locationsFrame = locationFrame[1:]
# locationsFrame.rename(columns=header)

print(locationFrame)
locationFrame.to_csv("output1.csv")















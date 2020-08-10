import pandas as pd
import requests
import numpy
import os
import math
from statistics import median, mean


#           Function that takes a bread crumb data frame and formats all gps coordinates into a google api request
def Formatter(frame):
    request = "https://roads.googleapis.com/v1/snapToRoads?path="
    print("forming request")
    for index, row in frame.iterrows():
        request += (str(row['GPS_LATITUDE']) + "," + str(row['GPS_LONGITUDE']) + "|")
    request = request[:-1]
    #If user wanted interpolated points they would have &interpolate=true
    #request += "&interpolate=true&key=" + os.environ['ROADS_API']
    request += "&key=" + os.environ['ROADS_API']
    return request


#               Read in data
pd.set_option('display.max_colwidth', 100)
frame1 = pd.read_csv('../bos_2020022428.tsv', delimiter='\t')
frame2 = pd.read_csv('../bos_2020030206.tsv', delimiter='\t')
frame3 = pd.read_csv('../bos_2020030913.tsv', delimiter='\t')
frame4 = pd.read_csv('../bos_20200301620.tsv', delimiter='\t')
masterFrame = [frame1, frame2, frame3, frame4]
frame = pd.concat(masterFrame)
frame.append(frame2, ignore_index=True)
frame.dropna(inplace=True) # This will drop rows with empty data


singletrip = frame.loc[frame['EVENT_NO_TRIP'] == 152570206]
originalList = singletrip.values.tolist()
#print(originalList)

          #length var to see how many hundreds of GPS points are in trip
length = int(math.ceil(len(singletrip)/100))
googlerequests = []
first = 0
last = 100
locationsList = []
# interCounter = 0 #used for when interpolation is on to help define which data is interpolated.
# indexCounter = 0


#           Loop to send 100 or less coordinates at a time to be formatted
for x in range (0, length):
    googlerequests.append(Formatter(singletrip[first:last]))
    first += 100 # The google maps API will only take 100 gps points at a time
    last += 100

singletripList = singletrip.values.tolist()

#print("Printing original list")
#print(singletripList)
#print("printing request")

# for x in range (0,length):
#     print(googlerequests[x])
print("sending request")

for x in range (0, len(googlerequests)):
    response = requests.post(googlerequests[x])
    jsonResponse = response.json()
    #To Debug Failed JSON Response
    #print(jsonResponse)
    snappedPoint = jsonResponse['snappedPoints']

#       reformatting snapped GPS points into a single list
    for y in range (0, len(snappedPoint)):
        snap = snappedPoint[y]
        #print(snap)
        location =  snap['location']
        latitude = location['latitude']
        longitude = location['longitude']
        #orignialIndex = location['originalIndex']
        locationsList.append([latitude, longitude])

        #This commented out code can be used to differentiate between interpolated data and non-interpolated
        # if len(snap) < 3:
        #     locationsList.append([latitude, longitude, 'interpolated'+ str(interCounter)])
        #     interCounter += 1
        # else:
        #     locationsList.append([latitude, longitude, 'originalIndex' + str(indexCounter)])
        #     indexCounter += 1
#       Reformatting the original trip and snapped trip into Data frames

#Data Manipulation
originalTripFrame = pd.DataFrame(singletrip)
originalTripFrame.reset_index(drop = True, inplace=True) # reseting the index so it merges properly with locationFrame
originalTripFrame['TIMESTAMP'] = originalTripFrame['OPD_DATE'].astype(str) + ":" + originalTripFrame['ACT_TIME'].astype(str)
originalTripFrame.rename(columns={"EVENT_NO_TRIP": "tripID", "VEHICLE_ID": "vehicleID", "METERS": "distance", "GPS_LONGITUDE": "origLongitude", "GPS_LATITUDE": "origLatitude"}, inplace=True)
snappedTripFrame = pd.DataFrame(locationsList, columns = ["correctedLatitude", "correctedLongitude"])
snappedTripFrame.reset_index()

#       Merging original and snapped
mergedDf = originalTripFrame.merge(snappedTripFrame, left_index=True, right_index=True)
mergedDf.to_csv("output1.csv")

#Calculations assume that Corrected data matches index of Original data coordinates

minLong_deviation = 0
minLong_Timestamp = ""
maxLong_deviation = 0
maxLong_Timestamp = ""
meanLong_deviation = 0
medianLong_deviation = 0
longlist = []

minLat_deviation = 0
minLat_Timestamp = ""
maxLat_deviation = 0
maxLat_Timestamp = ""
meanLat_deviation = 0
medianLat_deviation = 0
latlist = []

#[origlat, origlong, latdeviation, long,deviation)
minpoint_deviation = []
minpoint_Timestamp= ""
maxpoint_deviation = []
minpoint_Timestamp= ""
#meanpoint_deviation = []
#medianpoint_deviation = []

for row in mergedDf.head().itertuples():
    #Minimum Longitude Deviation
    if minLong_deviation == 0:
        minLong_deviation = abs(row.origLongitude - row.correctedLongitude)
        minLong_Timestamp = row.TIMESTAMP
    if minLong_deviation < abs(row.origLongitude - row.correctedLongitude):
        minLong_deviation = abs(row.origLongitude - row.correctedLongitude)
        minLong_Timestamp = row.TIMESTAMP
    #Maximimum Longitude Deviation
    if maxLong_deviation == 0:
        maxLong_deviation = abs(row.origLongitude - row.correctedLongitude)
        maxLong_Timestamp = row.TIMESTAMP
    if abs(row.origLatitude - row.correctedLatitude) > maxLong_deviation:
        maxLong_deviation = abs(row.origLongitude - row.correctedLongitude)
        maxLong_Timestamp = row.TIMESTAMP

    #Minimum Latitude Deviation
    if minLat_deviation ==0:
        minLat_deviation = abs(row.origLatitude - row.correctedLatitude)
        minLat_Timestamp = row.TIMESTAMP
    if abs(row.origLatitude - row.correctedLatitude) < minLat_deviation:
        minLat_deviation = abs(row.origLatitude - row.correctedLatitude)
        minLat_Timestamp = row.TIMESTAMP
    #Maximum Latitude Deviation
    if maxLat_deviation ==0:
        maxLat_deviation = abs(row.origLatitude - row.correctedLatitude)
        maxLat_Timestamp = row.TIMESTAMP
    if abs(row.origLatitude - row.correctedLatitude) > maxLat_deviation:
        maxLat_deviation = abs(row.origLatitude - row.correctedLatitude)
        maxLat_Timestamp = row.TIMESTAMP

    #Point with smallest Deviation(Gives the Original Point along with the least amount of deviations in both long and lat calculation)
    if not minpoint_deviation:
        minpoint_deviation = (row.origLatitude, row.origLongitude, abs(row.origLatitude - row.correctedLatitude), abs(row.origLongitude - row.correctedLongitude))
        minpoint_Timestamp = row.TIMESTAMP
    if abs(abs(row.origLatitude) + abs(row.origLongitude)) - abs(abs(row.correctedLatitude + abs(row.correctedLongiude))) < (minpoint_deviation[2]+ minpoint_deviation[3]):
        minpoint_deviation = [row.origLatitude, row.origLongitude, abs(row.origLatitude - row.correctedLatitude), abs(row.origLongitude - row.correctedLongitude)]
        minpoint_Timestamp = row.TIMESTAMP

    #Point with largest Deviation(Gives the Original Point along with the largest amount of deviations in both long and lat calculation)
    if not maxpoint_deviation:
        maxpoint_deviation = (row.origLatitude, row.origLongitude, abs(row.origLatitude - row.correctedLatitude), abs(row.origLongitude - row.correctedLongitude))
        maxpoint_Timestamp = row.TIMESTAMP
    if abs(abs(row.origLatitude) + abs(row.origLongitude)) - abs(abs(row.correctedLatitude + abs(row.correctedLongitude))) > (minpoint_deviation[2] + minpoint_deviation[3]):
        maxpoint_deviation = [row.origLatitude, row.origLongitude, abs(row.origLatitude - row.correctedLatitude), abs(row.origLongitude - row.correctedLongitude)]
        maxpoint_Timestamp = row.TIMESTAMP


    #Appending deviations to a List
    longlist.append(abs(row.origLongitude - row.correctedLongitude))
    latlist.append(abs(row.origLatitude - row.correctedLatitude))

meanLong_deviation = mean(longlist)
medianLong_deviation = median(longlist)

meanLat_deviation = mean(latlist)
medianLat_deviation= median(latlist)

print("Minimum Longitude Deviation: " + "{:.15f}".format(minLong_deviation) + " Maximum Longitude Deviation: " + "{:.15f}".format(maxLong_deviation))
print("Median Longitude Deviation: " + "{:.15f}".format(medianLong_deviation) + " Mean Longitude Deviation: " + "{:.15f}".format(meanLong_deviation))

print("Minimum Latitude Deviation: " + "{:.15f}".format(minLat_deviation) + " Maximum Latitude Deviation: " + "{:.15f}".format(maxLat_deviation))
print("Median Latitude Deviation: " + "{:.15f}".format(medianLat_deviation) + " Mean Latitude Deviation: " + "{:.15f}".format(meanLat_deviation))

print("Point with the Smallest Deviation: " + "Latitude " + str(minpoint_deviation[0]) + ", " + "Longitude " + str(minpoint_deviation[1]))
print("Minimum Deviated Latitude" + str(minpoint_deviation[2]) + "Minimum Deviated Longitude" + str(minpoint_deviation[1]))

print("Point with the largest Deviation: " + "Original Latitude " + str(maxpoint_deviation[2]) + ", " + "Orignal Longitude " + str(maxpoint_deviation[3]))
print("Minimum Deviated Latitude" + str(maxpoint_deviation[0]) + "Minimum Deviated Longitude" + str(maxpoint_deviation[1]))













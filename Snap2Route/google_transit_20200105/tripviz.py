import pandas as pd
import argparse
import sys, traceback
import os

# tripviz.py: visualize C-Tran recorded trips along with the corresponding planned trip
#     with highlights for recorded trip locations that deviate from the planned trip.
#
# to use it, you must do these steps:
#  a. get a corrected deviation file. this includes both original sensor GPS coordiantes
#     and corrected GPS sensor coordinates for C-Tran vehicles
#  b. get ctran's GTFS shapes.txt file for the period corresponding
#     to the timestamps in the corrections file.
#  c. go to mapbox.com, create a free acount, get an API access token and insert into the
#     the code in the output_html function as indicated below
#  d. run the program with "python tripviz.py --help" to see the command line options. 
#     then run it with "python tripviz.py -d -t <trip ID goes here>". Use the -c and -s 
#     options to indicate the locations of the corrected breadcrumbs file and shapes file
#     as needed. use the --deviation_threshold option to change the deviation threshold
#
#  If the program runs successfully then it will create an output HTML file called tripviz.html
#  Open the tripviz.html file in your web browser. It should display a satellite map showing
#  a blue polyline (the planned trip), a red polyline (the recorded trip) and multiple
#  yellow line segments for each breadcrumb reading that deviates more than 
#  deviation_threshold from the planned trip.
# 

DEBUG = False

DEFAULT_TRIPID = 152570206
tripID = DEFAULT_TRIPID  # the trip to be analyzed. user must specify tripID on command line

corr_df = pd.DataFrame()  # corrected recorded trip data
trip_df = pd.DataFrame() # subset of corr_df corresponding to tripID


DEFAULT_CORRECTIONS_FILE = "output1.csv"
corrections_file = DEFAULT_CORRECTIONS_FILE # file containing corrected trip data

DEFAULT_OUTPUT_HTML_FILE = "trip150193541Route37.html"
outhtml = DEFAULT_OUTPUT_HTML_FILE # output file

DEFAULT_DEVIATION_THRESHOLD = 10.0 
deviation_theshold = DEFAULT_DEVIATION_THRESHOLD   # in meters

olat_lis = [] 
vehicleID = -1
olon_lis = []
clat_lis = []
clon_lis = []

def initialize():
	global tripID, DEBUG, outhtml, corrections_file

	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--correctionsfile", default=DEFAULT_CORRECTIONS_FILE, 
		help="file containing corrected breadcrumb coordinates")
	parser.add_argument("-d", "--debug", default = False, 
		help="debugging switch", action="store_true")
	parser.add_argument("-o", "--outhtml", default=DEFAULT_OUTPUT_HTML_FILE, 
		help="output html file")
	parser.add_argument("-t", "--tripID", default=DEFAULT_TRIPID,
		help="ID of trip to be analyzed")
	args = parser.parse_args()

	outhtml = args.outhtml
	DEBUG = args.debug
	corrections_file = args.correctionsfile
	tripID = int(args.tripID)

def readCSVfile(fname, parsed=[], idf=False):
	if (DEBUG): print(f"\treading data file: {fname}")
	df = pd.read_csv(fname, parse_dates=parsed, infer_datetime_format=idf,
					 low_memory=False)
	return df


# read in all of the data and compute teh shapeID if needed
def ingest_data():
	global corr_df, trip_df
	global olat_lis, vehicleID, olat_lis, olon_lis, clat_lis, clon_lis
	
	try:
		if (DEBUG): print("BEGIN ingesting data")
		
		corr_df = readCSVfile(corrections_file)
		
		trip_df = corr_df.loc[corr_df["tripID"] == tripID]
		if (trip_df.empty):
			print(f"ERROR: trip {tripID} not found in corrections file {corrections_file}")
			exit(-1)

		vehicleID = trip_df['vehicleID'].iloc[0] # assume: all shapeIDs for a given tripID identical
		olat_lis = trip_df['origLatitude'].tolist()
		olon_lis = trip_df['origLongitude'].tolist()
		clat_lis = trip_df['correctedLatitude'].tolist()
		clon_lis = trip_df['correctedLongitude'].tolist()

		if (DEBUG): print("END ingesting data")

	except Exception as e:
		print("ERROR while ingesting data")
		print(e)
		traceback.print_exc(file=sys.stderr)
		exit(-1)

# output html+CSS+javascript showing both trips on a map 
# requires you to have an app key from http://mapbox.com
# if you don't have one then go get one and update the appkey variable accordingly
# 
def output_html():
	global bc_df

	DEFAULT_MAPBOX_TOKEN = " "
	# before running this script, go to mapbox.com, create an account and get an access token
	# then insert your token into the following line in place of DEFAULT_MAPBOX_TOKEN
	mapbox_token = os.environ['MAPBOX_TOKEN']

	if (mapbox_token == DEFAULT_MAPBOX_TOKEN):
		print("ERROR: mapbox_token variable is not set properly")
		print("ERROR: go to mapbox.com, create a free account, get an access token, and insert into source code before using this program")
		exit(-1)

	beginHTML = """
<!DOCTYPE html>
<html>
<head>
	<title>Breadcrumb Trip Map</title>
	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.6.0/dist/leaflet.css"
   integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
   crossorigin=""/>
   <script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"
   integrity="sha512-gZwIG9x3wUXg2hdXF6+rVkLF/0Vi9U8D2Ntg4Ga5I5BZpVkVxlJWbSQtXPSiUTtC0TjtGOmxa1AJPuV0CPthew=="
   crossorigin=""></script>
  <style> 
  #map {position: absolute; top:0; bottom: 0; left: 0; right: 0;}
   </style> 
</head>
<body>
	<div id="map"></div>
	<script>
		var mymap = L.map('map').setView([45.722279,-122.688873], 10);
"""
	tokenLine = "L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token="+mapbox_token+"', {"
	nextHTML = """
    		attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    		id: 'mapbox/satellite-streets-v11',
    		tileSize: 512,
    		maxZoom: 33,
    		zoomOffset: -1,
    		accessToken: 'your.mapbox.access.token'
		}).addTo(mymap);

	"""

	fil = open(outhtml,"w+")
	fil.write(beginHTML)
	fil.write(tokenLine)
	fil.write(nextHTML)

	# create a marker for the first lat/lon pair for the recorded trip	
	lat = str(olat_lis[0])
	lon = str(olon_lis[0])	

	fil.write("\t\tvar omarker = L.marker([" + lat + ',' + lon + "]).addTo(mymap);\n")
	fil.write("\t\tomarker.bindPopup("+'"'+ "begin orig RECORDED trip" + '"' + ")\n")

	# write all of the lat/lon pairs for the recorded trip
	fil.write ("\n\n\t\tvar olatlons = [\n")

	for i in range (len(olat_lis)):
		lat = str(olat_lis[i])
		lon = str(olon_lis[i])
		fil.write("\t\t\t[" + lat + "," + lon + "],\n")
	fil.write ("\t\t];\n")

	fil.write("\n\n")

	fil.write("var opolyline = L.polyline(olatlons, {color: 'red'}).addTo(mymap);\n")

	# create a marker for the first lat/lon pair for the recorded trip	
	clat = str(clat_lis[0])
	clon = str(clon_lis[0])	

	fil.write("\t\tvar cmarker = L.marker([" + clat + ',' + clon + "]).addTo(mymap);\n")
	fil.write("\t\tcmarker.bindPopup("+'"'+ "begin CORRECTED trip" + '"' + ")\n")

	# write all of the lat/lon pairs for the recorded trip
	fil.write ("\n\n\t\tvar clatlons = [\n")

	for i in range (len(clat_lis)):
		clat = str(clat_lis[i])
		clon = str(clon_lis[i])
		fil.write("\t\t\t[" + clat + "," + clon + "],\n")
	fil.write ("\t\t];\n")

	fil.write("\n\n")

	fil.write("var cpolyline = L.polyline(clatlons, {color: 'cyan'}).addTo(mymap);\n")		

	fil.write ("\n")


	endHTML = """
	mymap.fitBounds(cpolyline.getBounds());

	</script>

</body>
</html>
"""

	fil.write(endHTML)
	fil.close()
	if (DEBUG):
		num_readings = len(olat_lis)
		print(f"SUMMARY") 
		print(f"\ttrip {tripID}")
		print(f"\tvehicle {vehicleID}")
		print(f"\t{num_readings} breadcrumb readings in the recorded trip")

		print(f"wrote output to file: {outhtml}")
		print(f"open {outhtml} in web browser to see results")


initialize()
ingest_data()
output_html()

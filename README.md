# Y's-Team


NOTE: Bread crumb data was too large so we had to push it as zip files


Implementation Project Plan

By Jason Yang & Samuel Youngs

Project Objective

Our project objective is to write a python script to take a set of breadcrumb data from C-Tran and enhance the data. We will do this by  Measuring bread crumb deviations and compute distance metrics for individual bread crumb readings and for entire trips. The enhanced data is then created by projecting a deviated bus route to its ideal bus route using the bread crumbs.
Project Approach
For this project, We are being led by Professor Bruce to create analysis tools for C-TRAN. Professor Bruce is supplying the data and dictating the scope of the project. So as a team, we need to be agile and flexible to his specifications that may change through the course. 

We are planning to use python and possibly anaconda. We might use SQL to gather and sort data from the C-Tran GPS readings. Another possible thing we might use is GCP and its road API to locate the road for the bus data. 
Team Structure
Our team is but one of three teams working with Bruce.  Although we have different goals for functionality design, we probably will share code that uses similar functionality. The way Bruce has it set up right now, if a team finds a more efficient algorithm of analyzing roads, this algorithm would be shared between the teams. We will also be sharing our data schema designs.

Our team’s primary goal is working on removing the deviations in the bus gps data by shifting each reading to its closest ideal route location. Deviations would be like the bus taking a different route than the standard route.

Other teams are working on
Automatically characterize bread crumb reading deviations for transit trips
Identify C-Tran trips that deviate the most from their corresponding route.



Project Milestones
Group: Things that the teams will be contributing together after individual research/implementation
Primary: Things that our individual team will be focusing on
Stretch Goal: Things that we can pick up more work

(Group) Understand and devise a common schema for the bread crumb data
(Group) Choose a common technology stack for the three teams so they all use the same tech
(Group) Read the data from the input files and store using the agreed technology stack (such as python + pandas)
(Primary Goal) Removing the deviations in the bus gps data by shifting each reading to its closest ideal route location
(Personal Stretch Goal) Have two routes and have a visual estimation of the route projection times on an actual map.
(Stretch Goal) Host the Snap2Route tool as a web application such that C-Tran analysts can use it.
(Stretch Goal Automatically adjust all readings for a large set of input data. Output data to CSV format file(s) that mimic the input data.
(Stretch Goal) Process and analyze a new set of C-Tran bread crumb data

Note: Some of the sentences in this document are pulled from Professor Bruce’s document with his permission.

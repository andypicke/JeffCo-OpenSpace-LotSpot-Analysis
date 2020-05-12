# Predicting Trailhead Parking Capacity at JeffCo Open Space Trailheads

# Introduction
I propose to build a model to predict parking lot capacity at Jefferson County Open Space trailheads in Colorado. This would be useful to:
- Hikers: When is the best time to go for a hike? Will there be parking available? 
- Open Space managers: How should we plan/allocate resources among the parks?

This takes on added importance in the time of Covid-19, with the goal of maintaining adequate social distancing on trails. 

# Data

## LotSpot Parking Data
The data was shared by Lot Spot, which JeffCo Open Space has contracted with to monitor parking at seven of their trailhead parking lots since August 2019. The LotSpot data features are a timestamp, % capacity of the lot, # spaces in use, and whether a car entered/exited.  The timestamps are not evenly spaced (there is a datapoint whenever a car enters/exits a lot), so I will need to bin/interpolate the data to a regularly spaced timeseries (5mins? 15 mins?) for analysis and modeling. 

## Weather
[Powered by Dark Sky](https://darksky.net/poweredby/)

# EDA


# Modeling

# Results


# Conclusions
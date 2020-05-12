# Predicting Trailhead Parking Capacity at JeffCo Open Space Trailheads

# Introduction
I propose to build a model to predict parking lot capacity at [Jefferson County Open Space](https://www.jeffco.us/open-space) trailheads in Colorado. This would be useful to:
- Hikers: When is the best time to go for a hike? Will there be parking available? 
- Open Space managers: How should we plan/allocate resources among the parks?

This takes on added importance in the time of Covid-19, with the goal of maintaining adequate social distancing on trails. 

# Data

## LotSpot Parking Data
The data was shared by [Lot Spot](https://lotspot.co/), which JeffCo Open Space has contracted with since August 2019 to monitor parking at seven of their popular trailheads: 
- East [Mount Falcon](https://www.jeffco.us/1332/Mount-Falcon-Park)
- West Mount Falcon
- East [Three Sisters](https://www.jeffco.us/980/Alderfer-Three-Sisters-Park)
- West Three Sisters
- East [White Ranch](https://www.jeffco.us/1437/White-Ranch-Park)
- [Lair o' the Bear](https://www.jeffco.us/1254/Lair-o-the-Bear-Park)
- [Mount Galbraith](https://www.jeffco.us/1335/Mount-Galbraith-Park)

 A camera located at the entrance to the parking lot detects when a vehicle enters or exits the lot. The LotSpot data features are a timestamp, % capacity of the lot, # spaces in use, and whether a car entered/exited.  The timestamps are not evenly spaced (there is a datapoint whenever a car enters/exits a lot), so I will need to bin/interpolate the data to a regularly spaced timeseries (1 hr) for analysis and modeling. 

## Weather
[Powered by Dark Sky](https://darksky.net/poweredby/)


# EDA


# Modeling


# Results


# Conclusions
# Get Dark Sky hiostrical weather data and save to file
# Set up to run as cron job each day and get yesterday's weather data

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
import pickle

def get_darksky_historical(api_key, lat = 39.646865, lon = -105.196314, time = '2020-05-01T00:00:00'):
    '''

    Get historical darksky weather data for specified location and time
    
    INPUT
    api_key (str): Secret!
    lat (float): Default is latitude for East Mount Falcon Trailhead
    lon (float): Default is latitude for East Mount Falcon Trailhead
    time (str) : Formatted like '2020-05-01T00:00:00'
    
    OUTPUT
    df_daily, df_hourly : Pandas Dataframes with daily, hourly weather data
    See https://darksky.net/dev/docs#api-request-types for info on data fields
    '''

    req_url = 'https://api.darksky.net/forecast/' + api_key + '/' + str(lat) + ',' + str(lon) + ',' + time
    content = requests.get(req_url)
    dat_dict = content.json()
    daily = dat_dict['daily']['data'][0]
    df_daily = pd.DataFrame.from_dict([daily])
    
    df_daily['lat'] = lat
    df_daily['lon'] = lon

    time_fields = ['time','sunriseTime','sunsetTime','precipIntensityMaxTime','temperatureHighTime','temperatureLowTime',
              'apparentTemperatureHighTime','apparentTemperatureLowTime','windGustTime','uvIndexTime','temperatureMinTime',
              'temperatureMaxTime','temperatureMaxTime','apparentTemperatureMinTime','apparentTemperatureMaxTime']
    for field in time_fields:
        df_daily[field] = pd.to_datetime(df_daily[field], origin='unix', unit='s',utc=True).dt.tz_convert(dat_dict['timezone'])
        
    hourly = dat_dict['hourly']
    df_hourly = pd.DataFrame.from_dict(hourly['data'])
    df_hourly['lat'] = lat
    df_hourly['lon'] = lon
    df_hourly['time'] = pd.to_datetime(df_hourly['time'], origin='unix', unit='s', utc=True).dt.tz_convert(dat_dict['timezone'])
    
    return df_daily, df_hourly


if __name__=='__main__':

   with open('./data/park_info.pkl', 'rb') as f:
        park_info = pickle.load(f)

    API_KEY = os.getenv('DARKSKY_API_KEY')

    today = datetime.now()
    yesterday = datetime.now() + timedelta(-1)
    #print(today.strftime('%Y-%m-%d'))
    #print(yesterday.strftime('%Y-%m-%d'))

    the_time = yesterday.strftime('%Y-%m-%d') + 'T00:00:00'
    #print(the_time)

    for park_name in park_info.keys():
        #print(park_name)
        lat = park_info[park_name]['lat']
        #print(lat)
        lon = park_info[park_name]['lon']
        #print(lon)
        df_daily, df_hourly = get_darksky_historical(api_key=API_KEY, lat = lat, lon = lon, time=the_time )
        
        base_dir = './data/proc/weather/historical/daily_files/'
        
        df_daily.to_csv(base_dir  + park_name + '_historical_' + yesterday.strftime('%Y-%m-%d') + '_daily'   + '.csv', index=False)
        
        df_hourly.to_csv(base_dir + park_name + '_historical_' + yesterday.strftime('%Y-%m-%d') + '_hourly'  + '.csv', index=False)
        
        df_daily.to_pickle(base_dir  + park_name + '_historical_' + yesterday.strftime('%Y-%m-%d') + '_daily'   + '.pkl')
        
        df_hourly.to_pickle(base_dir + park_name + '_historical_' + yesterday.strftime('%Y-%m-%d') + '_hourly'  + '.pkl')
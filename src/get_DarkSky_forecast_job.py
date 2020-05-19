# Get Dark Sky weather forecast and save to file

import os
import pandas as pd
import requests
from datetime import datetime


def get_darksky_forecast(api_key, lat = 39.646865, lon = -105.196314):
    '''
    Get historical darksky weather **FORECAST** for specified location
    
    INPUT
    api_key
    lat
    lon
    
    OUTPUT
    df_daily, df_hourly : Pandas Dataframes with daily,hourly data
    '''
    req_url = 'https://api.darksky.net/forecast/' + api_key + '/' + str(lat) + ',' + str(lon)
    content = requests.get(req_url)
    dat_dict = content.json()
    
    daily = dat_dict['daily']
    df_daily = pd.DataFrame.from_dict(daily['data'])
    df_daily['lat'] = lat
    df_daily['lon'] = lon
    time_fields = ['time','sunriseTime','sunsetTime','precipIntensityMaxTime','temperatureHighTime','temperatureLowTime',
              'apparentTemperatureHighTime','apparentTemperatureLowTime','windGustTime','uvIndexTime','temperatureMinTime',
              'temperatureMaxTime','temperatureMaxTime','apparentTemperatureMinTime','apparentTemperatureMaxTime']
    for field in time_fields:
        df_daily[field] = pd.to_datetime(df_daily[field], origin='unix', unit='s',utc=True).dt.tz_convert(dat_dict['timezone'])

    df_daily['datetime_requested'] = pd.to_datetime(dat_dict['currently']['time'], origin='unix', unit='s',utc=True).tz_convert(dat_dict['timezone'])    
    
    hourly = dat_dict['hourly']
    df_hourly = pd.DataFrame.from_dict(hourly['data'])
    df_hourly['lat'] = lat
    df_hourly['lon'] = lon

    df_hourly['time'] = pd.to_datetime(df_hourly['time'], origin='unix', unit='s', utc=True).dt.tz_convert(dat_dict['timezone'])
    df_hourly['datetime_requested'] = pd.to_datetime(dat_dict['currently']['time'], origin='unix', unit='s',utc=True).tz_convert(dat_dict['timezone'])

    date_req = datetime.now().strftime('%Y-%m-%d')
    
    return date_req, df_daily, df_hourly

if __name__=='__main__':

    park_info = {}
    park_info['east_mount_falcon']  = {'lat':39.646865, 'lon':-105.196314}
    park_info['east_three_sisters'] = {'lat':39.623484, 'lon':-105.345841}
    park_info['east_white_ranch']   = {'lat':39.798109, 'lon':-105.246799}
    park_info['lair_o_the_bear']    = {'lat':39.665616, 'lon':-105.258430}
    park_info['mount_galbraith']    = {'lat':39.774085, 'lon':-105.253516}
    park_info['west_mount_falcon']  = {'lat':39.637136, 'lon':-105.239178}
    park_info['west_three_sisters'] = {'lat':39.624941, 'lon':-105.360398}

    API_KEY = os.getenv('DARKSKY_API_KEY')

    for park_name in park_info.keys():
        #print(park_name)
        lat = park_info[park_name]['lat']
        #print(lat)
        lon = park_info[park_name]['lon']
        #print(lon)
        date_req, df_daily, df_hourly = get_darksky_forecast(api_key=API_KEY, lat = lat, lon = lon)
        #print(date_req)
        base_dir = './data/proc/weather/forecasts/'
        df_daily.to_pickle(base_dir  + park_name + '_forecast_' + date_req + '_daily'   + '.pkl')
        df_hourly.to_pickle(base_dir + park_name + '_forecast_' + date_req + '_hourly'  + '.pkl')
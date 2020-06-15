# Get Dark Sky weather forecast and save to file

import os
import pandas as pd
import requests
from datetime import datetime
import pickle

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

    with open('./data/park_info.pkl', 'rb') as f:
        park_info = pickle.load(f)

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

        df_daily.to_csv(base_dir  + park_name + '_forecast_' + date_req + '_daily'   + '.csv', index=False)

        df_hourly.to_csv(base_dir + park_name + '_forecast_' + date_req + '_hourly'  + '.csv', index=False)

        df_daily.to_pickle(base_dir  + park_name + '_forecast_' + date_req + '_daily'   + '.pkl')

        df_hourly.to_pickle(base_dir + park_name + '_forecast_' + date_req + '_hourly'  + '.pkl')
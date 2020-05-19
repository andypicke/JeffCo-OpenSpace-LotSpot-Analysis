# Combine weather dataframes for each day (made w/ get_darksky_weather.py) into single combined dataframe

import os
import pandas as pd

if __name__=='__main__':

    park_info = {}
    park_info['east_mount_falcon']  = {'lat':39.646865, 'lon':-105.196314}
    park_info['east_three_sisters'] = {'lat':39.623484, 'lon':-105.345841}
    park_info['east_white_ranch']   = {'lat':39.798109, 'lon':-105.246799}
    park_info['lair_o_the_bear']    = {'lat':39.665616, 'lon':-105.258430}
    park_info['mount_galbraith']    = {'lat':39.774085, 'lon':-105.253516}
    park_info['west_mount_falcon']  = {'lat':39.637136, 'lon':-105.239178}
    park_info['west_three_sisters'] = {'lat':39.624941, 'lon':-105.360398}

    for park_name in park_info.keys():

        print('Combining Daily historical weather Files for ' + park_name)

        daily_file_dir = './data/proc/weather/historical/daily_files'
        wea_files = os.listdir(daily_file_dir)
        hourly_files = sorted([file for file in wea_files if file.startswith(park_name + '_historical') & file.endswith('hourly.pkl')])
        daily_files = sorted([file for file in wea_files if file.startswith(park_name + '_historical') & file.endswith('daily.pkl')])

        df_comb_hourly = pd.DataFrame()
        for file in hourly_files:
            df = pd.read_pickle(daily_file_dir + '/' + file)
            df_comb_hourly = pd.concat([df_comb_hourly, df])
        df_comb_hourly.to_pickle('./data/proc/weather/historical/combined/' + (park_name + '_historical_combined_wea_hourly.pkl') )

        df_comb_daily = pd.DataFrame()
        for file in daily_files:
            df = pd.read_pickle(daily_file_dir + '/' + file)
            df_comb_daily = pd.concat([df_comb_daily, df])
        df_comb_daily.to_pickle('./data/proc/weather/historical/combined/' + (park_name + '_historical_combined_wea_daily.pkl') )
# Combine weather dataframes for each day (made w/ get_darksky_weather.py) into single combined dataframe

import os
import pandas as pd
import pickle

if __name__=='__main__':

    with open('./data/park_info.pkl', 'rb') as f:
        park_info = pickle.load(f)

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
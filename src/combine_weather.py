import os
import pandas as pd


if __name__=='__main__':

    wea_files = os.listdir('./data/weather')
    hourly_files = sorted([file for file in wea_files if file.startswith('wea_hourly')])
    daily_files = sorted([file for file in wea_files if file.startswith('wea_daily')])

    df_comb_hourly = pd.DataFrame()
    for file in hourly_files:
        df = pd.read_pickle('./data/weather/' + file)
        df_comb_hourly = pd.concat([df_comb_hourly, df])
    df_comb_hourly.info()
    df_comb_hourly.to_pickle('./data/weather/weather_combined_wea_hourly.pkl')

    df_comb_daily = pd.DataFrame()
    for file in daily_files:
        df = pd.read_pickle('./data/weather/' + file)
        df_comb_daily = pd.concat([df_comb_daily, df])
    df_comb_daily.info()
    df_comb_daily.to_pickle('./data/weather/weather_combined_wea_daily.pkl')
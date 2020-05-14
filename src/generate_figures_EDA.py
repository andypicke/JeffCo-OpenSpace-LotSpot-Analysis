import pandas as pd
import numpy as np
np.set_printoptions(suppress=True)
import matplotlib.pyplot as plt
import seaborn as sns

# make plots look nice
plt.rcParams['font.size'] = 14
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'large'
plt.rcParams['ytick.labelsize'] = 'large'
plt.rcParams['lines.linewidth'] = 3
plt.style.use('ggplot')

park_list = ['east_mount_falcon', 'east_three_sisters', 'east_white_ranch', 'lair_o_the_bear', 
             'mount_galbraith', 'west_mount_falcon', 'west_three_sisters']

def read_process_park_data(park_name):
    '''
    Read in raw LotSpot data for a park and process into dataframe.
    Convert timestamp to US/Mountain datetime, add various datetime fields for analysis

    INPUT
    park_name (str) : Name of park to load

    RETURNS
    df (Pandas Dataframe)
    '''
    col_names = ['percent_capacity','spots_taken','total_spots','timestamp','in_out']
    df = pd.read_csv('./data/raw_data/' + park_name + '.csv', header=None, names=col_names )

    df['datetime_utc'] = pd.to_datetime(df['timestamp'], origin='unix', unit='s', utc=True)
    df['datetime'] = df['datetime_utc'].dt.tz_convert('US/Mountain')
    df.drop(['timestamp','datetime_utc'], axis=1, inplace=True)

    df['in_out'] = df['in_out'].apply(lambda x: x if x<2 else np.NaN)

    df['date']  = df['datetime'].dt.date
    df['month'] = df['datetime'].dt.month
    df['day']   = df['datetime'].dt.day
    df['hour']  = df['datetime'].dt.hour
    df['dow']   = df['datetime'].dt.dayofweek
    
    return df

def read_process_park_data_into_hourly(park_name):
    '''
    Read in raw LotSpot data for a park and process into dataframe, **resampled to 1-hour intervals**
    Convert timestamp to US/Mountain datetime, add various datetime fields for analysis

    INPUT
    park_name (str) : Name of park to load

    RETURNS
    df_hourly (Pandas Dataframe)
    '''
    col_names = ['percent_capacity','spots_taken','total_spots','timestamp','in_out']
    df = pd.read_csv('./data/raw_data/' + park_name + '.csv', header=None, names=col_names )

    df['datetime_utc'] = pd.to_datetime(df['timestamp'], origin='unix', unit='s', utc=True)
    df['datetime'] = df['datetime_utc'].dt.tz_convert('US/Mountain')
    df.drop(['timestamp','datetime_utc'], axis=1, inplace=True)
    
    df.drop(['spots_taken','total_spots','in_out'], axis=1, inplace=True)
    
    df_hourly = df.set_index('datetime').resample('H').pad().reset_index()
    
    df_hourly['date']  = df_hourly['datetime'].dt.date
    df_hourly['month'] = df_hourly['datetime'].dt.month
    df_hourly['day']   = df_hourly['datetime'].dt.day
    df_hourly['hour']  = df_hourly['datetime'].dt.hour
    df_hourly['dow']   = df_hourly['datetime'].dt.dayofweek
    
    return df_hourly

def agg_lotspot_daily(df):
    '''
    Aggregate raw LotSpot data by date. Compute total # cars, and median/avg/max % capacity

    INPUT
    df (Pandas Dataframe) : Dataframe of raw LotSpot data

    RETURNS
    df_gb_day
    '''
    df_gb_day = df.groupby('date').agg(total_cars=pd.NamedAgg(column='in_out', aggfunc='sum'),
                                  med_pc = pd.NamedAgg(column='percent_capacity', aggfunc='median'),
                                  avg_pc = pd.NamedAgg(column='percent_capacity', aggfunc='mean'),
                                  max_pc = pd.NamedAgg(column='percent_capacity', aggfunc='max')).reset_index()
    return df_gb_day

if __name__=='__main__':

    park_name = 'east_mount_falcon'
    park_name_plot = 'East Mount Falcon'
    
    # Plot Timeseries of daily-aggregated data
    df = read_process_park_data(park_name)
    df_gb_day = agg_lotspot_daily(df)
        
    fig,ax = plt.subplots(2,figsize=(14,10), sharex=True)

    ax[0].plot(df_gb_day['date'], df_gb_day['total_cars'],'o-')
    ax[0].set_ylabel('Total Cars')
    ax[0].set_title(park_name_plot)

    ax[1].plot(df_gb_day['date'], df_gb_day['max_pc'],'o-')
    ax[1].set_ylabel('Max % Cap.')

    plt.savefig('./images/' + park_name + '_Daily_TS.png')
    
    
    dfh = read_process_park_data_into_hourly(park_name)
    dfh = dfh[(dfh['hour']>5) & (dfh['hour']<20)]
   
    df3 = dfh.groupby('hour').mean().reset_index()
    df3
    fig,ax = plt.subplots(1, figsize=(8,6))
    ax.bar(df3['hour'], df3['percent_capacity'])
    ax.set_xlabel('Hour')
    ax.set_ylabel('Average % Capacity')
    ax.set_title(park_name_plot)
    plt.savefig('./images/' + park_name + '_AvgPerCap_vs_hour.png')

    df3 = dfh.groupby('dow').mean().reset_index()
    fig,ax = plt.subplots(1, figsize=(8,6))
    ax.bar(df3['dow'], df3['percent_capacity'])
    ax.set_xlabel('Day of Week (0=Monday)')
    ax.set_ylabel('Average % Capacity')
    ax.set_title(park_name_plot)
    plt.savefig('./images/' + park_name + '_AvgPerCap_vs_DayofWeek.png')

    wea = pd.read_pickle('./data/weather/weather_combined_wea_hourly.pkl')
    wea = wea[['time','temperature','cloudCover','precipIntensity','windGust','uvIndex']]
    dfh = pd.merge(dfh,wea,left_on='datetime',right_on='time')

    dfh.set_index('datetime',inplace=True)
    dfh.reset_index(inplace=True)
    fig,ax = plt.subplots(6, figsize=(14,12), sharex=True)
    ax[0].plot(dfh['datetime'].values, dfh['percent_capacity'],'.')
    ax[0].set_ylabel('% Capacity')
    ax[0].set_title(park_name_plot)
    ax[1].plot(dfh['datetime'].values, dfh['temperature'],'.')
    ax[1].set_ylabel('Temp.')
    ax[2].plot(dfh['datetime'].values, dfh['uvIndex'],'.')
    ax[2].set_ylabel('UV Index')
    ax[3].plot(dfh['datetime'].values, dfh['precipIntensity'],'.')
    ax[3].set_ylabel('Precip')
    ax[4].plot(dfh['datetime'].values, dfh['cloudCover'],'.')
    ax[4].set_ylabel('Cloud Cover')
    ax[5].plot(dfh['datetime'].values, dfh['windGust'],'.')
    ax[5].set_ylabel('Wind Gust')
    plt.savefig('./images/' + park_name + '_PerCap_weather_TS.png')


    fig,ax = plt.subplots(nrows=2, ncols=2, figsize=(14,10), sharey=True)
    sns.regplot(dfh['temperature'], dfh['percent_capacity'], robust=True, ci=None, scatter_kws={"alpha": 0.2}, ax = ax.flatten()[0])
    ax.flatten()[0].set_xlabel('Temperature')
    ax.flatten()[0].set_ylabel('% Capacity')
    sns.regplot(dfh['uvIndex'], dfh['percent_capacity'], x_jitter=0.2, robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[1])
    ax.flatten()[1].set_xlabel('UV Index')
    ax.flatten()[1].set_ylabel('% Capacity')
    sns.regplot(dfh['cloudCover'], dfh['percent_capacity'], robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[2])
    ax.flatten()[2].set_xlabel('Cloud Cover')
    ax.flatten()[2].set_ylabel('% Capacity')
    sns.regplot(dfh['precipIntensity'], dfh['percent_capacity'], robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[3])
    ax.flatten()[3].set_xlabel('Precipitation Intensity')
    ax.flatten()[3].set_ylabel('% Capacity')
    plt.savefig('./images/' + park_name + '_weather_scatter.png')
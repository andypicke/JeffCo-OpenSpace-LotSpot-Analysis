import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# make plots look nice
plt.rcParams['font.size'] = 14
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'large'
plt.rcParams['ytick.labelsize'] = 'large'
plt.rcParams['lines.linewidth'] = 3
plt.style.use('ggplot')

park_info = {}
park_info['east_mount_falcon']  = {'pretty_name':'East Mount Falcon', 'lat':39.646865, 'lon':-105.196314}
park_info['east_three_sisters'] = {'pretty_name':'East Three Sisters', 'lat':39.623484, 'lon':-105.345841}
park_info['east_white_ranch']   = {'pretty_name':'East White Ranch', 'lat':39.798109, 'lon':-105.246799}
park_info['lair_o_the_bear']    = {'pretty_name':"Lair O' The Bear", 'lat':39.665616, 'lon':-105.258430}
park_info['mount_galbraith']    = {'pretty_name':'Mount Galbraith', 'lat':39.774085, 'lon':-105.253516}
park_info['west_mount_falcon']  = {'pretty_name':'West Mount Falcon', 'lat':39.637136, 'lon':-105.239178}
park_info['west_three_sisters'] = {'pretty_name':'West Three Sisters', 'lat':39.624941, 'lon':-105.360398}


def load_proc_park_data(park_name, type='raw'):
    '''
    Loads processed data frames w/ LotSpot data for parks. These are made in process_LotSpot.py

    INPUT
    park_name (str)
    type ('str'): Options are 'raw' (default), 'daily', and 'hourly'.
    
    OUTPUT
    df (Pandas DataFrame) 

    '''
    base_dir = './data/proc/LotSpot/'
    
    if type=='raw':
        df = pd.read_pickle(base_dir  + park_name + '_raw.pkl')
    
    if type=='daily':
        df = pd.read_pickle(base_dir  + park_name + '_daily.pkl')
        
    if type=='hourly':
        df = pd.read_pickle(base_dir  + park_name + '_resampled_hourly.pkl')
    
    return df

if __name__=='__main__':

    #park_name = 'east_mount_falcon'
    for park_name in park_info.keys():

        # Plot Timeseries of daily-aggregated data
        df_gb_day = load_proc_park_data(park_name, type='daily')
            
        fig,ax = plt.subplots(2,figsize=(14,10), sharex=True)
        ax[0].plot(df_gb_day['date'], df_gb_day['total_cars'],'o-')
        ax[0].set_ylabel('Total Cars')
        ax[0].set_title(park_info[park_name]['pretty_name'])
        ax[1].plot(df_gb_day['date'], df_gb_day['max_pc'],'o-')
        ax[1].set_ylabel('Max % Of Cap.')
        plt.savefig('./images/' + park_name + '_Daily_TS.png')
        plt.close()

        # Load hourly resampled data and filter to open hours
        #dfh = read_process_park_data_into_hourly(park_name)
        dfh = load_proc_park_data(park_name, type='hourly')
        dfh = dfh[(dfh['hour']>5) & (dfh['hour']<20)]
    
        # Group by hour and plot average % capacity
        d_gbh = dfh.groupby('hour').mean().reset_index()
        fig,ax = plt.subplots(1, figsize=(8,6))
        ax.bar(d_gbh['hour'], d_gbh['percent_capacity'])
        ax.set_xlabel('Hour')
        ax.set_ylabel('Average % Of Capacity')
        ax.set_title(park_info[park_name]['pretty_name'])
        plt.savefig('./images/' + park_name + '_AvgPerCap_vs_hour.png')
        plt.close()

        # Group by day of week and plot average % capacity
        df_gb_dow = dfh.groupby('dow').mean().reset_index()
        fig,ax = plt.subplots(1, figsize=(8,6))
        ax.bar(df_gb_dow['dow'], df_gb_dow['percent_capacity'])
        ax.set_xlabel('Day of Week (0=Monday)')
        ax.set_ylabel('Average % Of Capacity')
        ax.set_title(park_info[park_name]['pretty_name'])
        plt.savefig('./images/' + park_name + '_AvgPerCap_vs_DayofWeek.png')
        plt.close()

        # Load weather data and merge with hourly parking data
        wea = pd.read_pickle('./data/proc/weather/historical/combined/' + park_name + '_historical_combined_wea_hourly.pkl')
        wea = wea[['time','temperature','cloudCover','precipIntensity','windGust','uvIndex']]
        dfh = pd.merge(dfh, wea, left_on='datetime', right_on='time')


        # Plot timeseries of % capacity and weather variables
        dfh.set_index('datetime',inplace=True)
        dfh.reset_index(inplace=True)
        fig,ax = plt.subplots(6, figsize=(14,12), sharex=True)
        ax[0].plot(dfh['datetime'].values, dfh['percent_capacity'],'.')
        ax[0].set_ylabel('% Capacity')
        ax[0].set_title(park_info[park_name]['pretty_name'])
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
        plt.close()

        # Make scatter plots of % capacity versus weather variables
        fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(14,10), sharey=True)
        
        sns.regplot(dfh['temperature'], dfh['percent_capacity'], robust=True, ci=None, scatter_kws={"alpha": 0.2}, ax = ax.flatten()[0])
        ax.flatten()[0].set_xlabel('Temperature')
        ax.flatten()[0].set_ylabel('% Of Capacity')
        ax.flatten()[0].set_ylim(0,100)

        sns.regplot(dfh['uvIndex'], dfh['percent_capacity'], x_jitter=0.2, robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[1])
        ax.flatten()[1].set_xlabel('UV Index')
        ax.flatten()[1].set_ylabel('% Of Capacity')
        ax.flatten()[1].set_ylim(0,100)

        sns.regplot(dfh['cloudCover'], dfh['percent_capacity'], robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[2])
        ax.flatten()[2].set_xlabel('Cloud Cover')
        ax.flatten()[2].set_ylabel('% Of Capacity')
        ax.flatten()[2].set_ylim(0,100)

        sns.regplot(dfh['precipIntensity'], dfh['percent_capacity'], robust=True, ci=None,scatter_kws={"alpha": 0.2}, ax = ax.flatten()[3])
        ax.flatten()[3].set_xlabel('Precipitation Intensity')
        ax.flatten()[3].set_ylabel('% Of Capacity')
        ax.flatten()[3].set_ylim(0,100)

        plt.savefig('./images/' + park_name + '_weather_scatter.png')
        plt.close()
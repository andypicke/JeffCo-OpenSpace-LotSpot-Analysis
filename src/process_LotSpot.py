import pandas as pd
import numpy as np

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
    df = pd.read_csv('./data/raw/LotSpot/' + park_name + '.csv', header=None, names=col_names )

    df['datetime_utc'] = pd.to_datetime(df['timestamp'], origin='unix', unit='s', utc=True)
    df['datetime'] = df['datetime_utc'].dt.tz_convert('US/Mountain')
    df.drop(['timestamp','datetime_utc'], axis=1, inplace=True)

    df['in_out'] = df['in_out'].apply(lambda x: x if x<2 else np.NaN)

    df['percent_capacity'] = df['percent_capacity']*100

    df['date']  = df['datetime'].dt.date
    df['month'] = df['datetime'].dt.month
    df['day']   = df['datetime'].dt.day
    df['hour']  = df['datetime'].dt.hour
    df['dow']   = df['datetime'].dt.dayofweek
    
    return df

def read_process_park_data_into_hourly(park_name):
    '''
    Read in raw LotSpot data for a park and process into dataframe, **resampled to 1-hour intervals**
    Convert timestamp to US/Mountain datetime, add various datetime fields for analysis.

    INPUT
    park_name (str) : Name of park to load

    RETURNS
    df_hourly (Pandas Dataframe), *resampled to hourly intervals*
    '''
    col_names = ['percent_capacity','spots_taken','total_spots','timestamp','in_out']
    df = pd.read_csv('./data/raw/LotSpot/' + park_name + '.csv', header=None, names=col_names )

    df['percent_capacity'] = df['percent_capacity']*100

    df['datetime_utc'] = pd.to_datetime(df['timestamp'], origin='unix', unit='s', utc=True)
    df['datetime'] = df['datetime_utc'].dt.tz_convert('US/Mountain')
    df.drop(['timestamp','datetime_utc'], axis=1, inplace=True)
    df.drop(['spots_taken','total_spots','in_out'], axis=1, inplace=True)
    
    # Resample to hourly intervals
    df_hourly = df.set_index('datetime').resample('H').pad().reset_index()
    
    df_hourly['date']  = df_hourly['datetime'].dt.date
    df_hourly['month'] = df_hourly['datetime'].dt.month
    df_hourly['day']   = df_hourly['datetime'].dt.day
    df_hourly['hour']  = df_hourly['datetime'].dt.hour
    df_hourly['dow']   = df_hourly['datetime'].dt.dayofweek
    
    return df_hourly



def agg_lotspot_daily(df):
    '''
    Aggregate raw LotSpot data by day/date. Compute total # cars, and median/avg/max % capacity.

    INPUT
    df (Pandas Dataframe) : Dataframe of raw LotSpot data

    RETURNS
    df_gb_day
    '''
    df_gb_day = df.groupby('date').agg(total_cars=pd.NamedAgg(column='in_out',aggfunc='sum'),
        med_pc = pd.NamedAgg(column='percent_capacity', aggfunc='median'),
        avg_pc = pd.NamedAgg(column='percent_capacity', aggfunc='mean'),
        max_pc = pd.NamedAgg(column='percent_capacity', aggfunc='max')).reset_index()

    # Some dates may be missing; ensure we have all days in range (values will be nan if date is missing)
    all_dates = pd.date_range(start=df_gb_day['date'].min(), end=df_gb_day['date'].max(), freq='D')
    df_all_dates = pd.DataFrame({'date':all_dates})
    df_gb_day = pd.merge(df_all_dates, df_gb_day, how='left', left_on='date', right_on='date')

    return df_gb_day

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

        # Read in raw LotSpot data to pandas and save
        df = read_process_park_data(park_name)
        base_dir = './data/proc/LotSpot/'
        df.to_csv(base_dir  + park_name + '_raw.csv', index=False)
        df.to_pickle(base_dir  + park_name + '_raw.pkl')

        # Aggregate to daily and save
        df_daily = agg_lotspot_daily(df)
        base_dir = './data/proc/LotSpot/'
        df_daily.to_csv(base_dir  + park_name + '_daily.csv', index=False)
        df_daily.to_pickle(base_dir  + park_name + '_daily.pkl')

        # Resample to hourly data and save
        df_hourly = read_process_park_data_into_hourly(park_name)
        base_dir = './data/proc/LotSpot/'
        df_hourly.to_csv(base_dir  + park_name + '_resampled_hourly.csv', index=False)
        df_hourly.to_pickle(base_dir  + park_name + '_resampled_hourly.pkl')

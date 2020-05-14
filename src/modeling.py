# Train a random forest model to predict parking lot capacity

import pandas as pd
import numpy as np
np.random.seed(47)
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.inspection import plot_partial_dependence

# make plots look nice
plt.rcParams['font.size'] = 14
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'large'
plt.rcParams['ytick.labelsize'] = 'large'
plt.rcParams['lines.linewidth'] = 3
plt.style.use('ggplot')

def read_process_park_data_into_hourly(park_name):
    '''
    Read in raw LotSpot data for a park and process into dataframe, **resampled to 1-hour intervals**
    Convert timestamp to US/Mountain datetime, add various datetime fields for analysis.

    INPUT
    park_name (str) : Name of park to load

    RETURNS
    df_hourly (Pandas Dataframe), resampled to hourly intervals
    '''
    col_names = ['percent_capacity','spots_taken','total_spots','timestamp','in_out']
    df = pd.read_csv('./data/raw_data/' + park_name + '.csv', header=None, names=col_names )

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

if __name__=='__main__':

    park_name = 'east_mount_falcon'
    print(park_name)
    df = read_process_park_data_into_hourly(park_name)
    df['percent_capacity'] = df['percent_capacity']*100
    df = df[(df['hour']>5) & (df['hour']<20)]
    df = df[df['datetime']<'2020-03-01'] # pre-Covid19 time period
    df['is_wknd'] = df['dow'].apply(lambda x: 0 if x<5 else 1)
    df['hour']=df['hour'].astype('category')

    # load and merge weather data
    wea = pd.read_pickle('./data/weather/weather_combined_wea_hourly.pkl')
    wea = wea[['time','temperature','cloudCover','precipIntensity','uvIndex']]
    df = pd.merge(df, wea, left_on='datetime', right_on='time')

    # dummy-encode 'hour' feature
    df = pd.get_dummies(df,columns=['hour'], drop_first=True)

    # drop un-needed columns for model
    df.drop(['datetime','day','month','time','dow'], axis=1, inplace=True)
    
    # drop any rows with NaNs
    df.dropna(axis=0, how='any', inplace=True)

    # Train/test split ; Note I keep entire days together per Kayla's suggestion, 
    # since data within a certain day might be correlated
    df['date'] = df['date'].astype(str)
    uniq_dates = df['date'].unique()
    Ntrain = round(0.8*len(uniq_dates))
    train_dates = np.random.choice(uniq_dates, size=Ntrain, replace=False)
    df_train = df.loc[df['date'].isin(train_dates)]
    df_test = df.loc[~df['date'].isin(train_dates)]
    df_train.drop('date', axis=1, inplace=True)
    df_test.drop('date', axis=1, inplace=True)

    # Make target/feature arrays
    y_train = df_train.pop('percent_capacity').values
    y_test  = df_test.pop('percent_capacity').values
    feature_names = df_train.columns
    X_train = df_train.values
    X_test  = df_test.values
    
    # Predict the mean - hopefully we can do better!
    y_hat_mean = np.mean(y_train)*np.ones_like(y_train)
    print( 'Predict mean train  R^2:' +  str(round(r2_score(y_train,y_hat_mean),2)) )
    y_hat_mean = np.mean(y_train)*np.ones_like(y_test)
    print( 'Predict mean test R^2:' +  str(round(r2_score(y_test,y_hat_mean),2)) )
    print( 'Predict RMSE:' + str(round(np.sqrt(mean_squared_error(y_test,y_hat_mean)),2)) )

    # Fit Random Forest with default parameters
    rf = RandomForestRegressor(n_jobs=-1)
    rf.fit(X_train,y_train)
    y_hat_rf = rf.predict(X_test)
    print('RF-Default Train R^2: '  + str( round(rf.score(X_train,y_train),2) ) )
    print('RF-Default Test R^2: '   + str( round(rf.score(X_test,y_test),2) ) )
    print('RF-Default Test RMSE: '  + str( round(np.sqrt(mean_squared_error(y_test,y_hat_rf)),2) ) )

    # Use GridSearchCV to tune random forest model
    rf_params = {'n_estimators':[100, 200, 250],
                'max_features':['auto','sqrt','log2'],
                'min_samples_split':[2,5,10],
                'n_jobs':[-1],
                'max_depth':[None, 5, 10, 20]
                }
    cv = GridSearchCV(RandomForestRegressor(), rf_params, n_jobs=-1, verbose=1)
    cv.fit(X_train,y_train)

    rf_best = cv.best_estimator_

    print(rf_best)

    y_hat_rf_best = rf_best.predict(X_test)
    print('RF-Tuned Train R^2: '  + str(round(rf_best.score(X_train,y_train),2) ) )
    print('RF-Tuned Test R^2: '   + str(round(rf_best.score(X_test,y_test),2) ) )
    print('RF-Tuned Test RMSE: '  + str(round(np.sqrt(mean_squared_error(y_test, y_hat_rf_best)),2) ) )

    # Plot Feature Importances
    std = np.std([tree.feature_importances_ for tree in rf_best.estimators_], axis=0)
    feat_imp = pd.DataFrame({'feature_name':feature_names, 'feat_imp': rf.feature_importances_, 'std':std})
    feat_imp.sort_values('feat_imp',ascending=False,inplace=True)
    fig, ax = plt.subplots(1, figsize=(8,10))
    ax.barh(feat_imp['feature_name'], feat_imp['feat_imp'], xerr=feat_imp['std'])
    ax.invert_yaxis()
    ax.set_xlabel('Feature Importance')
    plt.savefig('./images/' + park_name + '_rf_featimp.png', bbox_inches='tight')

    # Make partial dependence plot
    my_plots = plot_partial_dependence(rf,       
                                    features=[0, 1, 2, 3, 4], # column numbers of plots we want to show
                                    X=X_train,            # raw predictors data.
                                    feature_names=['Is Weekend','Temperature','Cloud Cover','Precip. Intens.', 'uvIndex'], # labels on graphs
                                    grid_resolution=20) # number of values to plot on x axis
    fig = plt.gcf()
    fig.set_size_inches(11,8)
    plt.savefig('./images/' + park_name + '_rf_part_dep.png')
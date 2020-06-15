# Train a random forest model to predict parking lot capacity

import pandas as pd
import numpy as np
np.random.seed(47)
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.inspection import plot_partial_dependence

import pickle

# make plots look nice
plt.rcParams['font.size'] = 14
plt.rcParams['axes.labelsize'] = 'large'
plt.rcParams['xtick.labelsize'] = 'large'
plt.rcParams['ytick.labelsize'] = 'large'
plt.rcParams['lines.linewidth'] = 3
plt.style.use('ggplot')


def load_resampled_park_data(park_name):
    base_dir = './data/proc/LotSpot/'
    df = pd.read_pickle(base_dir  + park_name + '_resampled_hourly.pkl')
    return df

def train_test_split_days(df):
    '''
    Do train-test split for LotSpot data. Differs from usual split in that we keep
    entire days together (assuming there might be some correlation within a day).
    
    INPUT
    df - Pandas DataFrame of data to split; must contain 'date' and 'percent_capacity' columns. 
    
    '''
    df['date'] = df['date'].astype(str)
    uniq_dates = df['date'].unique()
    uniq_dates

    Ntrain = round(0.8*len(uniq_dates))
    train_dates = np.random.choice(uniq_dates, size=Ntrain, replace=False)

    df_train = df.loc[df['date'].isin(train_dates)]
    df_test = df.loc[~(df['date'].isin(train_dates))]
    #df_train.drop('date', axis=1, inplace=True)
    #df_test.drop('date', axis=1, inplace=True)

    y_train = df_train.pop('percent_capacity').values
    y_test  = df_test.pop('percent_capacity').values

    feature_names = df_train.drop('date', axis=1).columns

    X_train = df_train.drop('date', axis=1).values
    X_test  = df_test.drop('date', axis=1).values
    
    return X_train, X_test, y_train, y_test, feature_names, df_train, df_test

def plot_feature_importance(tree_model, feature_names):
    '''
    Plot the feature importances for a tree-based ensemble model (ie randomforest, boosted models)
    
    INPUTS
    tree_model: A fitted sk-learn type model that has 'feature_importances_' attribute
    feature_names : A list of the feature names corresponding to the columns of X the model was fit on
    
    OUTPUT
    
    '''
    std = np.std([tree.feature_importances_ for tree in tree_model.estimators_], axis=0)
    feat_imp = pd.DataFrame({'feature_name':feature_names, 'feat_imp': tree_model.feature_importances_, 'std':std})
    feat_imp.sort_values('feat_imp',ascending=False,inplace=True)
    
    fig, ax = plt.subplots(1, figsize=(8,10))
    ax.barh(feat_imp['feature_name'], feat_imp['feat_imp'], xerr=feat_imp['std'])
    ax.invert_yaxis()
    ax.set_xlabel('Feature Importance')
    return fig,ax

if __name__=='__main__':

    with open('./data/park_info.pkl', 'rb') as f:
        park_info = pickle.load(f)

    file1 = open("./model/model_summary.txt","a")

    file1.write('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    file1.write('\nModel Script Run on: ' + datetime.now().strftime('%Y-%m-%d'))

    for park_name in park_info.keys():

        print(park_name)
        file1.write('\n\n' + park_name + '\n\n')
        df = load_resampled_park_data(park_name)
        df = df[(df['hour']>5) & (df['hour']<20)]
        df['is_wknd'] = df['dow'].apply(lambda x: 0 if x<5 else 1)
        df['hour'] = df['hour'].astype('category')
        #df_post_covid = df[df['datetime']>'2020-03-01']
        #df = df[df['datetime']<'2020-03-01']

        # load and merge weather data
        wea = pd.read_pickle('./data/proc/weather/historical/combined/' + park_name + '_historical_combined_wea_hourly.pkl')
        wea = wea[['time','temperature','cloudCover','precipIntensity','uvIndex']]
        df = pd.merge(df,wea,left_on='datetime',right_on='time')

        # drop un-needed columns for model
        df.drop(['datetime','day','month','time','dow','precipIntensity'], axis=1, inplace=True)
        # drop any rows with NaNs
        df.dropna(axis=0, how='any', inplace=True)

        # Train/test split ; Note I keep entire days together per Kayla's suggestion, since data within a certain day might be correlated
        X_train, X_test, y_train, y_test, feature_names, df_train, df_test = train_test_split_days(df)
        
        file1.write('\nFeature names: ' + str(list(feature_names)) +'\n' )

        # Predict the mean - hopefully we can do better!
        y_hat_mean = np.mean(y_train)*np.ones_like(y_train)
        pred_mean_train_r2 = round(r2_score(y_train,y_hat_mean),2)
        y_hat_mean = np.mean(y_train)*np.ones_like(y_test)
        pred_mean_test_r2 = round(r2_score(y_test,y_hat_mean),2)        
        pred_mean_test_rmse = round(np.sqrt(mean_squared_error(y_test,y_hat_mean)),2)
        print( 'Predict mean train  R^2 : ' + str(pred_mean_train_r2)  )
        print( 'Predict mean test R^2 : ' +  str(pred_mean_test_r2) )
        print( 'Predict mean RMSE : ' + str(pred_mean_test_rmse) )

        file1.write('Predict mean train R^2 : ' + str(pred_mean_train_r2) + '\n')
        file1.write('Predict mean test R^2 : ' +  str(pred_mean_test_r2) + '\n')
        file1.write('Predict mean RMSE : ' + str(pred_mean_test_rmse) + '\n')

        # Fit Random Forest with default parameters
        rf = RandomForestRegressor(n_jobs=-1)
        rf.fit(X_train,y_train)
        y_hat_rf = rf.predict(X_test)
        rf_def_train_r2  = round(rf.score(X_train,y_train),2)
        rf_def_test_r2   = round(rf.score(X_test,y_test),2)
        rf_def_test_rmse = round(np.sqrt(mean_squared_error(y_test,y_hat_rf)),2)
        print('RF-Default Train R^2 : ' + str( rf_def_train_r2 ) )
        print('RF-Default Test R^2 : '  + str( rf_def_test_r2  ) )
        print('RF-Default Test RMSE : ' + str( rf_def_test_rmse) )

        file1.write('\nRF default train R^2 : ' + str(rf_def_train_r2)  + '\n')
        file1.write('RF default test R^2 : '    + str(rf_def_test_r2)   + '\n')
        file1.write('RF default test RMSE : '   + str(rf_def_test_rmse) + '\n')

        # Use GridSearchCV to tune random forest model
        rf_params = {'n_estimators':[100, 200, 250],
                    'max_features':['auto','sqrt','log2'],
                    'min_samples_split':[2,5,10],
                    'n_jobs':[-1],
                    'max_depth':[5,10,None]
                    }
        cv = GridSearchCV(RandomForestRegressor(), rf_params, n_jobs=-1, verbose=1)
        cv.fit(X_train,y_train)

        rf_best = cv.best_estimator_

        print(rf_best)
        file1.write('\nTuned Model Params: ' + str(rf_best) + '\n')

        y_hat_rf_best = rf_best.predict(X_test)
        rf_opt_train_r2  = round(rf_best.score(X_train,y_train),2)
        rf_opt_test_r2   = round(rf_best.score(X_test,y_test),2)
        rf_opt_test_rmse =round(np.sqrt(mean_squared_error(y_test, y_hat_rf_best)),2)

        print('RF-Tuned Train R^2 : '  + str(rf_opt_train_r2 ) )
        print('RF-Tuned Test R^2 : '   + str(rf_opt_test_r2) )
        print('RF-Tuned Test RMSE : '  + str(rf_opt_test_rmse ) )

        file1.write('\nRF tuned train  R^2 : ' + str(rf_opt_train_r2)  + '\n')
        file1.write('RF tuned test R^2 : '   + str(rf_opt_test_r2)   + '\n')
        file1.write('RF tuned test RMSE : '  + str(rf_opt_test_rmse) + '\n')

        # Plot Feature Importances
        plot_feature_importance(rf_best, feature_names)
        plt.savefig('./images/' + park_name + '_rf_featimp.png', bbox_inches='tight')

        # Make partial dependence plot
        my_plots = plot_partial_dependence(rf_best,       
                                    features=[0, 1, 2, 3, 4], # column numbers of plots we want to show
                                    X=X_train,            # raw predictors data.
                                    feature_names=['Hour','Is Weekend','Temperature','Cloud Cover','uvIndex'], # labels on graphs
                                    grid_resolution=20) # number of values to plot on x axis
        fig = plt.gcf()
        fig.set_size_inches(11,8)
        plt.savefig('./images/' + park_name + '_rf_part_dep.png')

        # save (pickle) model
        with open('./model/' + park_name + '_rf_model.pkl', 'wb') as f:
            pickle.dump(rf_best, f)
    
    file1.close()
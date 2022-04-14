#!/usr/bin/env python
# coding: utf-8
import sqlalchemy
from os import environ

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression,SGDClassifier


def import_data():
    engine = sqlalchemy.create_engine("mariadb+mariadbconnector://"+environ.get("USER")+                                  ":"+environ.get("PSWD")+"@127.0.0.1:3306/nba")

    command = "SELECT Teams.Name AS Team, Team_box_scores.* FROM Team_box_scores"+" INNER JOIN Teams ON Team_box_scores.Team_ID = Teams.ID " 

    df = pd.read_sql(command,engine,parse_dates='Game_day')
    drop_columns = ['Team_ID']
    df.drop(columns=drop_columns,inplace = True)
    
    
    return df


def made_playoffs(df):
    # Season_type will be used to differentiate regular season from playoffs.
    true = 1
    false = 0
    
    df['Year'] = df['Game_ID'].str.slice(3,5)
    
    playoffs = df[df['Game_ID'].str.contains('^004')].groupby(['Team','Year']).sum()
    
    idxs = playoffs.index
    del playoffs
    
    df['Playoffs'] = 0

    # Change Playoffs variable to False if there is no playoff data for that team that year.
    for t,y in idxs:
        df['Playoffs'].where(~((df["Year"]==y)&(df["Team"]==t)),true,inplace=True)

    # Now that the playoff status has been established, the temporary variables can be removed
#     df = df[df['Season_type']=='002']
    
    drop_cols = ['Year']
    df.drop(columns = drop_cols,inplace=True)
    
    
    return df[df['Game_ID'].str.contains('^002')]



def plot_hists(df):
    get_ipython().magic('matplotlib inline')
    df.hist(bins = 100,figsize=(30,15),grid=False)
    plt.show()
    
    return

def required_columns(df):
    features = ['Result', 'MINS', 'PTS', 'FGM', 'FGA', 'FGP', 'PM3', 'PA3', 'P3P','FTM','FTA',
                  'FTP', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK','PF']
    dependent = ['Playoffs']
    
    cols = features + dependent
    
    return df[cols]



def split_train_test(df, SEED = 10, test_size=0.2):
    train,test = train_test_split(df,random_state=SEED,test_size=test_size)
    
    return train, test


def plot_correlation_matrix(corr_matrix):
    precision = 2
    cmap = 'seismic' #'coolwarm'
    
    return corr_matrix.style.background_gradient(cmap=cmap,vmin=-1,vmax=1).format(precision=precision)



def make_boolean(df,true_value, column):
    df[column] = df[column]==true_val
    
    return df


def include_home(df):
    indicator_col = 'Matchup'
    # if Matchup record contains '@', game is away. Else game is home.
    ind = df[indicator_col].str.contains('@')
    df['Home'] = 0
    df['Home'].where(ind,1,inplace=True)
    
    return df


def include_conference(df):
    west = ['NOP','UTA', 'MEM','PHX', 'POR', 'SAC', 'SAS', 'OKC','DAL', 'DEN', 'GSW', 'HOU','LAC', 'LAL','MIN']
    
    df['Conference'] = 'West'
    df['Conference'].where(df['Team'].isin(west),'East',inplace=True)
    
    return df


def add_new_features(df):
    df["Poss"] = df["FGA"] - df["TOV"] + df["OREB"] + 0.44*df["FTA"]
    df["PPP"] = df["PTS"]/df["Poss"]
    df['OREB%'] = df["OREB"]/(df["FGA"] -df["FGM"])
    df['ATR'] = df["AST"]/df["TOV"]
    df['FTR'] = df["FTA"]/df["FGA"]
    df['eFG'] = 100*(df['FGM']+.5*df['PM3'])/df['FGA']
    
    df = include_conference(df)
    df = include_home(df)
    
    return df


def clean(df):
    percentage_fields = ['FGA','FTA','P3P']
    vals = {i:0 for i in percentage_fields}

    df.fillna(value=vals,inplace=True)

    return df.dropna()


def drop_noninformative(df):
    drop_cols = ['Team','Game_ID','Matchup','Game_day','MINS','PTS','REB']
    
    return df.drop(columns=drop_cols)


def transform(df):
    cleanup_cols = ['ATR', 'Result']
    # log transform on ATR 
    df['log(ATR)'] = np.log2(df['ATR'])
    
    # map results variable to a win variable
    df['Win'] = 1
    df['Win'] = df['Win'].where(df['Result']=='W',0)
    
    return df.drop(columns=cleanup_cols)


def fit_transformer(df,numeric_variables,ohe_cats):  
    transformer = ColumnTransformer([('numeric', StandardScaler(),numeric_variables),
                                 ('conference',OneHotEncoder(),ohe_cats)],remainder = 'passthrough')
    
    transformer.fit(df)
    
    return transformer


def preprocess(df,transformer=None):
    numeric_variables = ['FGM','FGA','FGP','PM3','PA3','P3P','FTM','FTA','FTP','OREB','DREB',
                     'AST','TOV','STL','BLK','PF','Poss','PPP','OREB%','log(ATR)','FTR','eFG']

    ohe_cats = ['Conference']

    boolean_variables = ['Home']

    response_variable = 'Playoffs'

    columns = numeric_variables + boolean_variables + ohe_cats

    df = clean(df)
    
    df = add_new_features(df)
    
    df = transform(df)
    
    df = drop_noninformative(df)
    to_transform = df[columns]
    
    if (transformer is None):
        transformer = fit_transformer(to_transform,numeric_variables,ohe_cats)
        
    x = transformer.transform(to_transform)
    y = df[response_variable]
    
    
    return x, y, transformer
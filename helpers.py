from dash import Dash
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from dash import dcc
import dash_daq as daq

import numpy as np
import pandas as pd

def map_conference(df):
    west = ['NOP','UTA', 'MEM','PHX', 'POR', 'SAC', 'SAS', 'OKC','DAL', 'DEN', 'GSW', 'HOU','LAC', 'LAL','MIN']
    
    df['Conference'] = 'west'
    df['Conference'].where(df['Team'].isin(west),'east',inplace=True)
    return df


def map_division(df):
    divisions = {}
    # eastern conference divisions
    divisions['atlantic'] = ['BOS','BKN','NYK','PHI','TOR']
    divisions['central'] = ['CHI','CLE','DET','IND','MIL']
    divisions['southeast'] = ['ATL','CHA','MIA','ORL','WAS']
    
    # western conference divisions
    divisions['northwest'] = ['DEN', 'MIN','OKC','POR','UTA']
    divisions['pacific'] = ['GSW','LAC','LAL','PHX','SAC']
    divisions['southwest'] = ['DAL','HOU','MEM','NOP','SAS']
    
    df['Division'] = 'west'
    
    for i in divisions:
        df['Division'].where(~df['Team'].isin(divisions[i]),i,inplace=True)
    return df

def calculate_features(df):
    df['eFG'] = 100*(df['FGM']+.5*df['PM3'])/df['FGA']
    df['PM2'] = df['FGM'] - df['PM3']

    return df



def teams(names):
    options = []
    for i in names:
        d = {}
        d["label"] = i
        d["value"] = i
        options.append(d)
        
    return options

def slider():
    slider = dcc.Slider(
        id = 'n_players',
        min = 1,
        max = 15,
        value = 5,
        marks = {year: str(year) for year in range(1,16)},
        step = None,
        tooltip={'always_visible':False}
    )
    return slider

def opposition_select(opps, i, t):
    opts = teams(opps)
    d = dcc.Dropdown(options=opts,value=t,id=i,multi=False)
    
    return d

def update_df(league,det,opp,n=5):
    opps = league.loc[league['Team']==opp].groupby('Name',as_index=False).mean().sort_values('PTS',ascending=False)
    opps['Team'] = opp
    
    d = det.groupby('Name',as_index=False).mean().sort_values('PTS',ascending=False)
    d['Team'] = 'DET'
    
    df = pd.concat((d.head(n),opps.head(n)))
    
    df= df.round(1)
    
    return df

def toggle_names(df,player_lab=True):
    
    if(player_lab):
        fig = px.scatter(y="PM3", x="PM2",color="eFG",size = "AST",data_frame = df,symbol='Team',
                         labels=dict(PM3='Average 3PM',PM2='Average 2PM',eFG='eFG%'),range_x=(-.2,df['PM2'].max()+2),
                         text="Name", hover_data = ['PM3','PM2','eFG','AST','Name'],
                         color_continuous_scale='RdBu_r',range_y=(-.2,df['PM3'].max()+1))
        fig.update_traces(textposition='top center')

    else:
        fig = px.scatter(y="PM3", x="PM2",color="eFG",size = "AST",data_frame = df,symbol='Team',
                         labels=dict(PM3='Average 3PM',PM2='Average 2PM',eFG='eFG%'),range_x=(-.2,df['PM2'].max()+2),
                         hover_data = ['PM3','PM2','eFG','AST','Name'],
                         color_continuous_scale='RdBu_r',range_y=(-.2,df['PM3'].max()+1))
        
    return fig

def add_lines(league_avg,fig,grouping='League'):
    avgs = {'League':league_avg}
    
    fig.add_hline(avgs[grouping]['PM3'],annotation_text = grouping+' average',
                  annotation_position='right top',line_dash='dash')
    fig.add_vline(avgs[grouping]['PM2'],annotation_text= grouping+' average',
                  annotation_position='right top',line_dash='dash')
    
    return fig

def left(opp_teams):
    d = html.Div([html.Label("Opposition: ", style = {'textAlign': 'center'}),
                    opposition_select(opp_teams,'drpdwn','ATL')])#'textAlign': 'left',
    
    return d

def right(t):
    d = html.Div([html.Label("Number of players for each team: ", style = {'textAlign': 'center'}),t],)
    return d


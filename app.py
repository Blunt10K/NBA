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

league = pd.read_csv('Pistons_dash.csv')

league = map_division(league)
league = map_conference(league)
league = calculate_features(league)

league_avg = league.dropna().mean(numeric_only=True)
div_avg = league.groupby('Division').mean()
conf_avg = league.groupby('Conference').mean()
team_avg = league.groupby("Team").mean()

det = league.loc[league['Team']=='DET']
det_avg = det.mean(numeric_only=True)


# def teams(names):
#     options = []
#     for i in names:
#         d = {}
#         d["label"] = i
#         d["value"] = i
#         options.append(d)
        
#     return options


# # In[26]:


# def opposition_select(opps, i):
#     opts = team(opps)
#     d = dcc.Dropdown(options=opts,value=None,id=i,multi=False)


# # In[38]:


opps = league.loc[league['Team']=='BKN'].groupby('Name').mean().sort_values('PTS',ascending=False)
opps['Team'] = 'BKN'
d = det.groupby('Name').mean().sort_values('PTS',ascending=False)
d['Team'] = 'DET'
df = pd.concat((d.head(10),opps.head(10)))

fig = px.scatter(y="PM3", x="PM2",color="eFG",size = "AST",data_frame = df,symbol='Team',text=df.index,
                 color_continuous_scale='RdBu_r')#RdYlBu_r
fig.update_layout(title ="Average 3PM vs 2PM", xaxis_title = "2PM",
                  title_x = 0.5,yaxis_title = "3PM",coloraxis_colorbar_x=1.15)

temp = det.groupby('Name').mean().sort_values('PM2',ascending=False)

fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

fig.add_hline(league_avg['PM3'],annotation_text = 'League PM3 average',annotation_position='left top')
fig.add_vline(league_avg['PM2'],annotation={'text':'League PM2 average'})
other = det.groupby('Name').mean()


fig.update_traces(textposition='top center')



app = Dash(__name__)
server = app.server


app.layout = html.Div(className="p-heading",
                      children=[html.H1(children="Detroit Pistons scoring"),
                                html.Div(children=[dcc.Graph(figure = fig, id = 'graph')])
])

@app.callback(
    Output('graph','figure'))
#     Output('graph2','figure'),
#     Output('graph3','figure'),
#     Input('g1','value'))
def update_figure():
    opps = league.loc[league['Team']=='BKN'].groupby('Name').mean().sort_values('PTS',ascending=False)
    opps['Team'] = 'BKN'
    d = det.groupby('Name').mean().sort_values('PTS',ascending=False)
    d['Team'] = 'DET'
    df = pd.concat((d.head(10),opps.head(10)))

    fig = px.scatter(y="PM3", x="PM2",color="eFG",size = "AST",data_frame = df,symbol='Team',text=df.index,
                    color_continuous_scale='RdBu_r')#RdYlBu_r
    fig.update_layout(title ="Average 3PM vs 2PM", xaxis_title = "2PM",
                    title_x = 0.5,yaxis_title = "3PM",coloraxis_colorbar_x=1.15)

    temp = det.groupby('Name').mean().sort_values('PM2',ascending=False)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    fig.add_hline(league_avg['PM3'],annotation_text = 'League PM3 average',annotation_position='left top')
    fig.add_vline(league_avg['PM2'],annotation={'text':'League PM2 average'})
    other = det.groupby('Name').mean()


    fig.update_traces(textposition='top center')
    return fig


if __name__ == '__main__':
    app.run_server()

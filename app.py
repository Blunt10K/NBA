from dash import Dash
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from dash import dcc
import dash_daq as daq

import numpy as np
import pandas as pd
from helpers import *


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



opps = league.loc[league['Team']=='ATL'].groupby('Name',as_index=False).mean().sort_values('PTS',ascending=False)
opps['Team'] = 'ATL'
d = det.groupby('Name',as_index=False).mean().sort_values('PTS',ascending=False)
d['Team'] = 'DET'
df = d.head()#pd.concat((d.head(5),opps.head(5)))
df= df.round(1)

league_efg =league['eFG'].mean()

fig = toggle_names(df,league_efg)
fig.update_layout(title ="Bubble size = Average AST",
                  title_x = 0.5,coloraxis_colorbar_x=1.15)



fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

fig.update_traces(textposition='top center')

fig = add_lines(league_avg,fig)

buttons_style = dict(width='45%',display='inline-block',height='5%')
toggle = daq.ToggleSwitch(value=True, vertical=False,label='Toggle player labels',id='player_lab',size=32)

opp_teams = [i for i in league['Team'].unique() if i != "DET"]
opp_teams = sorted(opp_teams)


app = Dash(__name__)
server = app.server



app.layout = html.Div(className="p-heading",
                      children=[html.H1(children="Detroit Pistons field goal analysis"),
                                html.Div(children=[html.Div(children=[left(opp_teams)],
                                                    style=buttons_style),
                                                    html.Div(children=[right(slider())],
                                                    style=buttons_style)]),
                                html.Div([toggle, dcc.Graph(figure = fig, id = 'graph')])
])

@app.callback(
    Output('graph','figure'),
    Input('drpdwn','value'),
    Input('player_lab','value'),
    Input('n_players','value'))
def update_figure(opp,player_lab,n):
    
    df = update_df(league,det,opp,n)

    fig = toggle_names(df,league_efg,player_lab)
    fig = add_lines(league_avg,fig)

    
    return fig

if __name__ == '__main__':
    app.run_server()

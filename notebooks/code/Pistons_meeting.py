import pandas as pd

from dash import Dash
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from dash import dcc

app = Dash(__name__)
# colours = {'text': '#7FDBFF', 'background':'#333333','radio_button':'#BBBBBB'} 
# text_size = {'H1':48,'H2':40,'text':28,'radio_button':20}

app.layout = html.Div(className="p-heading",
                      children=[html.H1(children="ESPN Fantasy Analysis"),
                                html.Div(children=[drpdwn('g1'), dcc.Graph(figure = fig, id = 'graph')]),
                                html.Div(children=[dcc.Graph(figure = fig2, id = 'graph2')]),
        html.Div(children=[dcc.Graph(figure = fig3, id = 'graph3')])
])

@app.callback(
    Output('graph','figure'),
    Output('graph2','figure'),
    Output('graph3','figure'),
    Input('g1','value'))
def update_figure(selected):
    d = box_scores.loc[box_scores['Name'].isin(selected)]
    
    fig = px.line(y="Rolling", x="Game_day",color="Name",data_frame = d, markers=True,range_y=(0,100))
    
    fig.update_layout(title ="Fantasy points during current season", xaxis_title = "Game Day",
                  title_x = 0.5,yaxis_title = "4 game Rolling mean / Fantasy points")
    
    fig2 = px.histogram(d, x= "Fantasy Points",color = "Name",marginal = 'box',barmode='overlay',
                        histnorm="probability")
    
    fig3 = px.ecdf(d,x="Fantasy Points",color="Name")

    
    return fig,fig2,fig3
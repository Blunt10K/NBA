from dash import Dash
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from dash import dcc

from helpers import *

season_types = ["regular_season","post_season"]
r_season = season_types[0]
p_season = season_types[1]


y = 2021
pos = 'PG'
top_n_players = 5


colours = {'text': '#7FDBFF', 'background':'#333333','radio_button':'#BBBBBB'}
text_size = {'H1':48,'H2':40,'text':28,'radio_button':20}

def player_slider():
	slider = dcc.Slider(
						id = 'n_players',
						min = 1,
						max = 10,
						value = 5,
						marks = {str(n): str(n) for n in range(1,11)},
						step = None,
						tooltip={'always_visible':False}
					)
	return slider

def year_slider():
	slider = dcc.Slider(
						id = 'years',
						min = min(reg_season.keys()),
						max = max(reg_season.keys()),
						value = max(reg_season.keys()),
						marks = {year: str(year) for year in reg_season.keys()},
						step = None,
						tooltip={'always_visible':False}
					)
	return slider


def player_stats():
	stats = dcc.RadioItems(
							options=[
								{'label': 'PTS','value':'PTS'},
								{'label': 'AST','value':'AST'},
								{'label': 'REB','value':'REB'},
								{'label': 'BLK','value':'BLK'},
								{'label': 'STL','value':'STL'}
							],
							value = 'PTS',
							labelStyle={'display': 'inline-block'},
							id = "stats",
							style = {'color':colours['radio_button'],
									 'fontSize':text_size['radio_button']}
					)
	return stats


def pos_dropdown():
	d = dcc.Dropdown(
					options = [
						{"value":"PG", "label":"Point Guard"},
						{"value":"SG", "label":"Shooting Guard"},
						{"value":"G", "label":"Guard"},
						{"value":"PF", "label":"Power Forward"},
						{"value":"SF", "label":"Small Forward"},
						{"value":"F", "label":"Forward"},
						{"value":"C", "label":"Centre"}
					],
					value = "PG",
					id = "pos_drop"
				)
	return d

def season_dropdown():
	d = dcc.Dropdown(
					options = [
						{"value":"regular", "label":"Regular"},
						{"value":"post", "label":"Post"}
					],
					value = "regular",
					id = "season_drop"
				)
	return d

reg_season = get_data(r_season)
post_season = get_data(p_season)

seasons = {"regular":reg_season, "post":post_season}


sorted_df = seasons["regular"][y][pos].sort_values("PTS",ascending = False).head(top_n_players)

fig = px.bar(sorted_df, x='PTS', y="Name", color="Team", barmode='overlay',opacity=1)
fig.update_layout(title_text="PTS for top "+str(top_n_players)+" players at "+ pos +\
                  " in the "+str(y) +" regular season", title_x=0.5)


app = Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor':colours['background'],'fontFamily':'Arial'}, children=[

	html.H1(children='NBA Data visualisation',
		style = {'textAlign': 'center',
				 'color':colours['text'],
				 'fontSize':text_size['H1']}),


	html.Div(children=[

			html.Div([html.Label("Position: ", style = {'textAlign': 'center',
						 'color':colours['text'],
						 'fontSize':text_size['text']}),
						pos_dropdown()
					],
				style = {'textAlign': 'left',"flex":1}
			),

			html.Div([html.Label("Season: ", style = {'textAlign': 'center',
						 'color':colours['text'],
						 'fontSize':text_size['text']}),
						season_dropdown()
					 ],
				style = {'textAlign': 'center',"flex":1}
			),

			html.Div([html.Label("Stats", style = {'textAlign': 'center',
						 'color':colours['text'],
						 'fontSize':text_size['text']}),
						player_stats()
					 ],
				style = {'textAlign': 'right',"flex":1}
			)

			

		],style = {'display':'flex','flex-direction': 'row'}
	),

	# html.br(),

	html.Div(player_slider(),
		style = {'textAlign': 'center',"flex":1}
	),

	# html.br(),

	html.Div(dcc.Graph(figure = fig, id = 'graph')
		# style = {'textAlign': 'right',"flex":1}
	),

	# html.br(),

	html.Div(year_slider(),
		style = {'textAlign': 'center',"flex":1}
	)
])

@app.callback(
	Output('graph','figure'),
	Input('stats','value'),
	Input('years','value'),
	Input('pos_drop','value'),
	Input('n_players','value'),
	Input('season_drop','value'))
def update_figure(stat,y,pos,top_n_players,season_type):

	sorted_df = seasons[season_type][y][pos].sort_values(stat,ascending = False).head(top_n_players)
	fig = px.bar(sorted_df, x=stat, y='Name', color="Team", barmode='overlay', opacity=1)

	fig.update_layout(yaxis={'categoryorder':'max ascending'},
					  title_text= +stat+ " per game for top "+str(top_n_players)+" players at "+ pos +\
					  " in the "+str(y) +' '+ season_type+ ' season', title_x=0.5)

	return fig

if __name__ == '__main__':
	app.run_server()

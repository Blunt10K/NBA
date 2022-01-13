from dash import dcc

colours = {'text': '#7FDBFF', 'background':'#333333','radio_button':'#BBBBBB'}
text_size = {'H1':48,'H2':40,'text':28,'radio_button':20}



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
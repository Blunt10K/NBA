from bs4 import BeautifulSoup
import json
import pandas as pd
from web_scraper import Play_by_play
from sqlalchemy import create_engine
from os import environ


def make_engine(user, pswd, db):

    return create_engine("mariadb+mariadbconnector://"\
                        +user+":"\
                        +pswd+"@127.0.0.1:3306/"+db)


def extract_application(html):
        
    soup = BeautifulSoup(html)
    app_script = soup.find('script',{'type':"application/json"})

    return json.loads(app_script.decode_contents())


def save_pbp(data):
    # filename is the gameid
    
    data = data['props']['pageProps']['playByPlay']

    filename = 'games/'+data['gameId']+'.json'

    with open(filename,'w') as f:
        json.dump(data,f)
        
    return 

def extract():
    command = "select distinct game_id, replace(replace(match_up,'.',''),' ','') "
    command += "as match_up from box_scores where match_up regexp 'vs' and game_id not in "
    command += "(select distinct game_id from play_by_plays) order by game_id limit 10;"

    engine = make_engine(environ.get('USER'),environ.get('PSWD'),'nba')

    df = pd.read_sql(command,engine)

    engine.dispose()

    pbp = Play_by_play()
    for page in pbp.get_pages(df):
        
        save_pbp(extract_application(page))

    return 
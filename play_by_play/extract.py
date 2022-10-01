import json
from sqlalchemy import create_engine

def make_engine(user, pswd, db):

    return create_engine("mariadb+mariadbconnector://"\
                        +user+":"\
                        +pswd+"@127.0.0.1:3306/"+db)


def extract_application(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html,'html5lib')

    return soup.find('script',{'type':"application/json"})


def save_pbp(app_script, directory):
    from os.path import join as osjoin
    # filename is the gameid

    if not app_script:
        return

    data = json.loads(app_script.decode_contents())
    data = data['props']['pageProps']['playByPlay']

    filename = data['gameId']+'.json'

    with open(osjoin(directory, filename),'w') as f:
        json.dump(data,f)
        
    return 

def extract():
    from os import environ, listdir
    from os.path import expanduser, join as osjoin
    import pandas as pd
    from web_scraper import Play_by_play

    directory = expanduser(osjoin('~/spark_apps','pbp','games'))
    

    command = "select distinct game_id, replace(replace(match_up,'.',''),' ','') "
    command += "as match_up from box_scores where match_up regexp 'vs' and game_id not in "
    command += "(select distinct game_id from play_by_plays) order by game_id limit 100;"

    engine = make_engine(environ.get('USER'),environ.get('PSWD'),'nba')

    df = pd.read_sql(command,engine)

    engine.dispose()

    # in case there are already some play-by-play data extracted but not processed
    existing_ids = [f.strip('.json') for f in listdir(directory)]
    df = df[~df['game_id'].isin(existing_ids)]


    pbp = Play_by_play()
    for page in pbp.get_pages(df):
        
        save_pbp(extract_application(page),directory)

    return 
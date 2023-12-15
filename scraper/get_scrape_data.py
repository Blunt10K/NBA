# %%
from datetime import datetime as dt, timedelta as td
from os.path import join
import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable
import re


def make_engine():
    host = Variable.get('HOSTNAME')
    db = Variable.get('NBA_DB')
    port = Variable.get('PORT')
    user = Variable.get('USER')
    pswd = Variable.get('PSWD')

    return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")
# %%
def extract_fields():
    
    with open('scrapy.log','r') as fp:
        logs = fp.read().split('\n')

    log_flag = r'[\s\S]+DEBUG: Crawled \((\d+)\)'
    game_pat = r'[\S\s]+https://www.nba.com/game/(\w+-vs-\w+)-(\d+)'
    referer_pat = r'[\s\S]+\([\s\S]+https://www.nba.com/games\?date=(\d+-\d+-\d+)'
    search_pat = log_flag + game_pat + referer_pat

    data = [dict(zip(['response','game_title','game_id','gate_date'],
                     re.search(search_pat,i).groups())) 
                     for i in logs if re.search(search_pat,i)]

    df = pd.DataFrame(data)
    return df

# %%
df = extract_fields()
conn = make_engine()

df.to_sql('scrape_logs', conn, if_exists='append', index=False)

conn.dispose()
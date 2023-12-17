# %%
import pandas as pd
import re
from db_utils import make_engine
from os.path import join
from airflow.models import Variable
from os import remove

crawl_logs = join(Variable.get('EXTDISK'),'spark_apps','NBA',
                  'crawled_dates.log')

def extract_fields():
    
    with open(crawl_logs,'r') as fp:
        logs = fp.read().split('\n')

    log_flag = r'[\s\S]+DEBUG: Crawled \((\d+)\)'
    game_pat = r'[\S\s]+https://www.nba.com/game/(\w+-vs-\w+)-(\d+)'
    referer_pat = r'[\s\S]+\([\s\S]+https://www.nba.com/games\?date=(\d+-\d+-\d+)'
    search_pat = log_flag + game_pat + referer_pat

    columns = ['response','game_title','game_id','game_date']

    data = [dict(zip(columns, re.search(search_pat,i).groups())) 
                     for i in logs if re.search(search_pat,i)]

    df = pd.DataFrame(data)
    return df

def clear_logs():
    remove(crawl_logs)


def write_to_db():

    df = extract_fields()
    conn = make_engine()

    df.to_sql('scrape_logs', conn.connect(), if_exists='append', index=False)

    conn.dispose()

    clear_logs()
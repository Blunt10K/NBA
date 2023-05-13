from time import strftime,localtime
from web_scraper import *
from spark_helpers import *
from schema import *
from os.path import expanduser,join as osjoin
import re
from datetime import datetime as dt
import numpy as np

def get_last_year(year):
    if(year > 2000):
        return year % 2000
    return year % 100


# %%
def extract():
    from db_utils import get_start_date
    import pandas as pd

    start_date = get_start_date()

    bs = Box_scores()
    year = int(strftime("%Y",localtime()))

    start_reg = 9
    end_reg = 4
    start_post = end_reg
    end_post = 7
    reg_season = True

    month = int(strftime('%m',localtime()))
    year_range = str(year-1) + "-{:0>2d}".format(get_last_year(year))

    if month <= end_reg or month >= start_reg:
        url = bs.build_url(year_range, start_date, reg_season)

    elif month >= start_post and month <= end_post:
        url = bs.build_url(year_range, start_date, not reg_season)

    else:
        return 

    directory = expanduser(osjoin('~/spark_apps','box_score','data'))

    date = strftime('%Y-%m-%d',localtime())
    count = 0
    rename_cols = {'min':'mins','3pm':'pm3','3pa':'pa3','+/-':'plus_minus','w/l':'result'}

    for page in bs.iter_all(url):
        df = bs.get_table(page)
        df.columns = [i.lower() for i in df.columns]

        pids, tids, gids = bs.get_player_and_team_ids(page)
        
        df['player_id'] = pids
        df['team_id'] = tids
        df['game_id'] = gids
        
        filename = date+'_page_'+str(count)+'.parquet'

        to_write = list(df.columns) + ['player_id','team_id','game_id']
        to_write = [re.sub('[\s]','_',i) for i in df.columns]

        df.columns = to_write

        df.rename(columns = rename_cols, inplace = True)

        df['game_date'] = pd.to_datetime(df['game_date'], format='%m/%d/%Y')

        df.to_parquet(osjoin(directory,filename),index=False)

        count += 1


    return


def transform():
    from pyspark.sql import SparkSession
    import pyspark.sql.functions as f
    from os import environ
    from os.path import expanduser, join as osjoin
    from db_utils import clear_dir


    spark = SparkSession.builder.appName('box_score').getOrCreate()  

    root = expanduser(osjoin('~/spark_apps','box_score'))
    path = osjoin(root, 'data')

    # read data
    df = spark.read.option('datetimeRebaseMode','EXCEPTION').parquet(path)

    df = df.withColumn('game_day',f.to_date('game_date'))

    box_scores(df, root)
    players(df, root)
    teams(df, root)

    clear_dir(path)

    return


def load():
    from pyspark.sql import SparkSession
    from os import environ
    from db_utils import primary_keys, add_box_scores


    spark = SparkSession.builder.appName('box_score').getOrCreate()  

    primary_keys(spark,'players')
    primary_keys(spark,'teams')
    add_box_scores(spark)



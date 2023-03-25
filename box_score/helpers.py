from time import strftime,localtime
from web_scraper import *
from spark_helpers import *
from schema import *
from os.path import expanduser,join as osjoin

def get_last_year(year):
    if(year > 2000):
        return year % 2000
    return year % 100


# %%
def extract():
    from db_utils import get_start_date
    import pandas as pd

    def get_table(html):
        dfs = pd.read_html(html,flavor = 'bs4')
        for idx, df in enumerate(dfs):
            if 'player' in [i.strip().lower() for i in df.columns]:
                return idx, df


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
    for page in bs.iter_all(url):
        df = bs.get_table(page)

        pids, tids, gids = bs.get_player_and_team_ids(page)
        
        df['pids'] = pids
        df['tids'] = tids
        df['gids'] = gids
        
        filename = date+'_page_'+str(count)+'.csv'

        to_write = bs.columns + ['pids','tids','gids']

        df.to_csv(osjoin(directory,filename),index=False, columns = to_write)

        count += 1

    return


def transform():
    from pyspark.sql import SparkSession
    from os import environ
    from os.path import expanduser, join as osjoin


    spark = SparkSession.builder.appName('box_score').getOrCreate()  

    root = expanduser(osjoin('~/spark_apps','box_score'))
    path = osjoin(root, 'data')

    # read data
    df = spark.read.option('sep',',').csv(path,
    schema=extract_schema(),header=True,dateFormat='MM/dd/yyyy')

    # drop unneeded columns
    df = df.drop('FP','3P%','FG%','FT%','REB')

    box_scores(df, root)
    players(df, root)
    teams(df, root)

    return


def load():
    from pyspark.sql import SparkSession
    from os import environ
    from db_utils import primary_keys, add_box_scores


    spark = SparkSession.builder.appName('box_score').getOrCreate()  

    primary_keys(spark,'players')
    primary_keys(spark,'teams')
    add_box_scores(spark)



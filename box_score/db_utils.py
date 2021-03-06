from sqlalchemy import create_engine
from os import environ
import pandas as pd
from spark_helpers import *
from schema import *

def make_engine(user, pswd, db):

    return create_engine("mariadb+mariadbconnector://"\
                        +user+":"\
                        +pswd+"@127.0.0.1:3306/"+db)


def get_start_date():
    db = 'nba'
    engine = make_engine(environ.get('USER'),environ.get('PSWD'),db)

    command = 'SELECT MAX(game_day)+1 as GD from box_scores;'
    max_date = pd.read_sql(command,engine)

    max_date['GD'] = pd.to_datetime(max_date['GD'],format='%Y%m%d')
    
    return max_date.loc[0,'GD']


def add_box_scores(spark):

    from os.path import expanduser, join as osjoin

    table = 'box_scores'

    path = osjoin('~','spark_apps','box_scores',table)
    path = expanduser(path)

    df = spark.read.option('cleanSource','delete').csv(path,schema=box_score_schema()).toPandas()

    add_new(df, table, 'game_id')
    clear_dir(path)


def add_new(df, table, column='id'):
    ids = str(tuple(df[column]))
    if ids == '()':
        return

    db = 'nba'
    engine = make_engine(environ.get('USER'),environ.get('PSWD'),db)


    existing = pd.read_sql(f'select {column} from {table} where {column} in {ids};',engine)

    merged = df.merge(existing,on=column,how='left',indicator=True)
    merged = merged[merged['_merge']=='left_only'].drop(columns=['_merge'])

    added = merged.to_sql(table,engine,index=False,if_exists='append',method='multi')

    print(f'{added} rows added')

    return


def primary_keys(spark,table):
    
    from os.path import expanduser, join as osjoin

    path = osjoin('~','spark_apps','box_score', table)
    path = expanduser(path)

    df = spark.read.option('cleanSource','delete').csv(path, schema=atom_schema()).toPandas()

    add_new(df,table)
    clear_dir(path)
    

def clear_dir(path):

    from os import listdir, remove
    from os.path import join

    for i in listdir(path):
        if i.endswith('csv'):
            remove(join(path,i))
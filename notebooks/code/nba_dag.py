# %%
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.python import PythonOperator
import pendulum

from time import strftime,localtime
from web_scraper import *

# %%
from os import environ
from db_utils import make_engine
import pandas as pd
from pyspark.sql import SparkSession
db = 'nba'

engine = make_engine(environ.get('USER'),environ.get('PSWD'),db)

# %%
def get_last_year(year):
        if(year > 2000):
            return year % 2000
        return year % 100

# %%
def extract(start_date):
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
                return # exit dag

        date = strftime('%Y-%m-%d',localtime())
        count = 0
        for p in bs.iter_all(url):
                df = pd.read_html(p,flavor = 'bs4')[0]

                pids, tids, gids = bs.get_player_and_team_ids(p)
                
                df['pids'] = pids
                df['tids'] = tids
                df['gids'] = gids
                
                fp = '../../../data/'+date+'_page_'+str(count)+'.csv'
                df.to_csv(fp,index=False)


                count += 1

# %%
def extract_schema():
    from pyspark.sql.types import StructType
# path = '../../../data/'

    # schema = StructType().add('Player','string').add('Team','string').add('Match Up','string').\
    #     add('Game Date','string').add('Season','string').add('W/L','string').add('MIN','integer').\
    #     add('PTS', 'integer').add('FGM', 'integer').add('FGA', 'integer').add('FG%', 'float').\
    #     add('3PM', 'integer').add('3PA', 'integer').add('3P%', 'float').add('FTM', 'integer').\
    #     add('FTA', 'integer').add('FT%', 'float').add('OREB', 'integer').add('DREB', 'integer').\
    #     add('REB', 'integer').add('AST', 'integer').add('STL', 'integer').add('BLK', 'integer').\
    #     add('TOV', 'integer').add('PF', 'integer').add('+/-', 'integer').add('FP', 'float').\
    #     add('pids', 'integer').add('tids', 'integer').add('gids','string')

    schema = StructType().add('Player','string',False).add('Team','string',False).\
    add('Match Up','string',False).\
    add('Game Date','date',False).add('Season','string').add('W/L','string').add('MIN','integer').\
    add('PTS', 'integer').add('FGM', 'integer').add('FGA', 'integer').add('FG%', 'float').\
    add('3PM', 'integer').add('3PA', 'integer').add('3P%', 'float').add('FTM', 'integer').\
    add('FTA', 'integer').add('FT%', 'float').add('OREB', 'integer').add('DREB', 'integer').\
    add('REB', 'integer').add('AST', 'integer').add('STL', 'integer').add('BLK', 'integer').\
    add('TOV', 'integer').add('PF', 'integer').add('+/-', 'integer').add('FP', 'float').\
    add('pids', 'integer',False).add('tids', 'integer',False).add('gids','string',False)

    return schema

# %%
def atom_schema():
    from pyspark.sql.types import StructType

    return StructType().add('id','integer',False).add('name','string',False)

# %%
def players(df):
    cols = ['pids','Player']

    rename_cols = ['id','name']

    player_df = df[cols].select('*').distinct()

    player_df = player_df.toDF(*rename_cols)

    player_df.writeStream.outputMode('append').format('csv').\
        option('path','../../../queries/players').option('checkpointLocation','../../../checkpoints').\
        start()

# %%
def teams(df):
    cols = ['tids','Team']

    # rename_cols = ['id','name']

    team_df = df[cols].select('*').distinct()

    # team_df = team_df.toDF(*rename_cols)

    team_df.writeStream.outputMode('append').format('csv').\
        option('path','../../../queries/teams').option('checkpointLocation','../../../checkpoints').\
        start()

# %%
def box_scores(df):
   cols = ['pids','tids', 'gids', 'MIN', 'PTS', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB',
      'DREB', 'AST', 'STL', 'BLK', 'TOV', 'PF', '+/-', 'W/L', 'Game Date', 'Match Up']

   box_df = df[cols]

   # rename_cols = ['player_id','team_id', 'game_id', 'mins','pts', 'fgm', 'fga', 'pm3',
   #    'pa3', 'ftm', 'fta', 'oreb','dreb', 'ast', 'stl', 'blk', 'tov', 'pf', 'plus_minus',
   #    'result', 'game_day', 'match_up']

   # box_df = box_df.toDF(*rename_cols)
   box_df.writeStream.outputMode('append').\
      format('csv').option('path','../../../queries/box_scores').\
      option('checkpointLocation','../../../checkpoints').start()

   # box_df.createOrReplaceTempView('box_scores')

# %%
def box_score_schema():
    from pyspark.sql.types import StructType

    schema = StructType().add('player_id','integer',False).add('team_id','string',False).\
    add('game_id','string',False).add('mins','integer').\
    add('pts', 'integer').add('fgm', 'integer').add('fga', 'integer').\
    add('pm3', 'integer').add('pa3', 'integer').add('ftm', 'integer').\
    add('fta', 'integer').add('oreb', 'integer').add('dreb', 'integer').\
    add('ast', 'integer').add('stl', 'integer').add('blk', 'integer').\
    add('tov', 'integer').add('pf', 'integer').add('plus_minus', 'integer').\
    add('result','string').add('game_day','date').add('match_up','string')

    return schema 

# %%
SparkSession.builder.config('spark.driver.extraClassPath',environ.get('SPARK_JDBC')).getOrCreate()
spark = SparkSession.builder.appName('nba_player_box_score').getOrCreate()

# %%
def transform(spark):    
    path = '../../../data/'
    # stream data
    df = spark.readStream.option('cleanSource','delete').option('sep',',').csv(path,
    schema=extract_schema(),header=True,dateFormat='MM/dd/yyyy')

    # drop unneeded columns
    df = df.drop('Season','FP','3P%','FG%','FT%','REB')

    box_scores(df)
    players(df)
    teams(df)

    return df

# %%
command = 'SELECT MAX(game_day) as GD from box_scores;'
max_date = pd.read_sql(command,engine,parse_dates=['GD'])
max_date = max_date.loc[0,'GD']

extract(max_date)
df = transform(engine,spark)

# %%
def add_new(df, table, engine):
    ids = str(tuple(df['id']))
    existing = pd.read_sql(f'select * from {table} where id in {ids};',engine)

    merged = df.merge(existing,on='id',how='left',indicator=True)
    merged = merged[merged['_merge']=='left_only']

    added = merged.to_sql(table,engine,index=False,if_exists='append',method='multi')

    print(f'{added} rows added')

    return

# %%
def primary_keys(spark,table,engine):
    path = f'../../../queries/{table}/*.csv'
    df = spark.read.csv(path,
        schema=atom_schema()).toPandas()

    add_new(df,table,engine)

# %%
def add_box_scores(spark,engine):
    path = '../../../queries/box_scores/*.csv'

    df = spark.read.csv(path, schema=box_score_schema()).toPandas()
    df['game_day'] = pd.to_datetime(df['game_day'])

    ids = str(tuple(df['game_id']))
    existing = pd.read_sql(f'select game_id from box_scores where game_id in {ids};',engine)

    merged = df.merge(existing,on='game_id',how='left',indicator=True)
    merged = merged[merged['_merge']=='left_only']

    added = merged.to_sql(box_scores,engine,index=False,if_exists='append',method='multi')

    print(f'{added} rows added')

# %%
def load(engine, spark):
    path = '../../../queries/'

    with TaskGroup("primary_keys", tooltip="Add new team and player primary keys") as primary_keys:
        player_task = PythonOperator(task_id = 'Add new players',python_callable=primary_keys,
            op_kwargs={'spark':spark,'engine':engine,'table':'players'})

        team_task = PythonOperator(task_id = 'Add new teams',python_callable=primary_keys,
            op_kwargs={'spark':spark,'engine':engine,'table':'teams'})

        player_task >> team_task
        # players_df = spark.read.csv(path + 'players/*.csv',
        # schema=atom_schema())
    with TaskGroup("stats", tooltip="Add new box score data") as new_box_scores:
        
        add_box_scores(box_df,engine)

    primary_keys >> new_box_scores



# %%
path = '../../../queries/'
box_df = spark.readStream.option('sep',',').csv(path + 'box_scores/',
schema=box_score_schema())

# %%
df = spark.read.csv(path + 'box_scores/*.csv',schema=box_score_schema())

# %%
t = df.toPandas()

# %%


# %%
with DAG('player_box_scores_etl',default_args={'retries': 4},description='NBA box score DAG',
schedule_interval='0 21 * * *',catchup=False,tags=['nba_stats'],
start_date=pendulum.datetime(2022, 6, 15, tz="UTC")) as dag:

    dag.doc_md = __doc__

    SparkSession.builder.config('spark.driver.extraClassPath',environ.get('SPARK_JDBC')).getOrCreate()
    spark = SparkSession.builder.appName('nba_player_box_score').getOrCreate()

    command = 'SELECT MAX(game_day) as GD from box_scores;'
    max_date = pd.read_sql(command,engine,parse_dates=['GD'])
    max_date = max_date.loc[0,'GD']

    extract_op = PythonOperator(task_id = 'extract',python_callable=extract,
    op_kwargs={'start_date':max_date})

    transform_op = PythonOperator(task_id = 'transform',python_callable=transform,
    op_kwargs={'start_date':max_date})

    load_op = PythonOperator(task_id = 'load',python_callable=load,
    op_kwargs={'spark':spark,'engine':engine})


    extract_op >> transform_op >> load_op

# %%
# rename_box_scores = ['player_id','team_id', 'game_id', 'mins','pts', 'fgm', 'fga', 'pm3',
# 'pa3', 'ftm', 'fta', 'oreb','dreb', 'ast', 'stl', 'blk', 'tov', 'pf', 'plus_minus',
# 'result', 'game_day', 'match_up']



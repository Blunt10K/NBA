# %%
from airflow import DAG
from airflow.decorators import task
import pendulum
import sys
from os.path import expanduser,join as osjoin


# %%
with DAG('play_by_play_etl',default_args={'retries': 4,'owner':'blunt10k'},description='NBA play by play DAG',
schedule_interval='0 15 * * *',catchup=False,tags=['nba_stats','nba_pbp'],
start_date=pendulum.datetime(2022, 6, 15, tz="UTC")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','NBA','play_by_play'))
    sys.path.insert(0,code_directory)

    from extract import extract
    from transform import transform_load
    # from load import load

    @task(task_id='extract')
    def extract_func():
        extract()

    @task(task_id='transform_load')
    def transform_load_func():
        transform_load()


    extract_op = extract_func()
    transform_op = transform_load_func()

    extract_op >> transform_op #>> load_op
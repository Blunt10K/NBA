# %%
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import sys
from os.path import expanduser,join as osjoin


# %%
with DAG('play_by_play_etl',default_args={'retries': 4,'owner':'blunt10k'},description='NBA play by play DAG',
schedule_interval='0 15 * * *',catchup=False,tags=['nba_pbp'],
start_date=pendulum.datetime(2022, 6, 15, tz="Africa/Harare")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','play_by_play'))
    sys.path.insert(0,code_directory)

    from extract import extract
    from transform import transform_load
    # from load import load

    extract_op = PythonOperator(task_id = 'extract',python_callable=extract)

    transform_op = PythonOperator(task_id = 'transform_load',python_callable=transform_load)

    extract_op >> transform_op #>> load_op
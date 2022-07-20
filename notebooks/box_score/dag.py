# %%
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum
import sys
from os.path import expanduser,join as osjoin

# %%
with DAG('player_box_scores_etl',default_args={'retries': 4,'owner':'blunt10k'},description='NBA box score DAG',
schedule_interval='0 21 * * *',catchup=False,tags=['nba_stats'],
start_date=pendulum.datetime(2022, 6, 15, tz="UTC")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','box_score'))
    sys.path.insert(0,code_directory)

    from helpers import extract,transform,load

    extract_op = PythonOperator(task_id = 'extract',python_callable=extract)

    transform_op = PythonOperator(task_id = 'transform',python_callable=transform)

    load_op = PythonOperator(task_id = 'load',python_callable=load)


    extract_op >> transform_op >> load_op


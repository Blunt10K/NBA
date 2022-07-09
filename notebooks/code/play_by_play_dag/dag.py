# %%
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

# %%
with DAG('play_by_play_etl',default_args={'retries': 4,'owner':'blunt10k'},description='NBA play by play DAG',
schedule_interval='0 10 * * *',catchup=False,tags=['nba_pbp'],
start_date=pendulum.datetime(2022, 6, 15, tz="UTC")) as dag:

    dag.doc_md = __doc__

    from extract import extract
    from transform import transform
    from load import load

    extract_op = PythonOperator(task_id = 'extract',python_callable=extract)

    transform_op = PythonOperator(task_id = 'transform',python_callable=transform)

    load_op = PythonOperator(task_id = 'load',python_callable=load)


    extract_op >> transform_op >> load_op
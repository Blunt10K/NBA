# %%
from airflow import DAG
from airflow.decorators import task
import pendulum
import sys
from os.path import expanduser,join as osjoin

# %%
with DAG('add_dates_to_calendar',default_args={'retries': 4,'owner':'blunt10k'},description='Data injector to calendar table',
schedule_interval='0 0 * * *',catchup=False,tags=['nba_stats'],
start_date=pendulum.datetime(2023, 12, 11, tz="UTC")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','NBA','data_injectors'))
    sys.path.insert(0,code_directory)

    from calendar_update import create_record

    @task(task_id="inject_date")
    def inject_date():
        create_record()
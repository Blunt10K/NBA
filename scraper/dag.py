# %%
from airflow import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
import pendulum
import sys
from os.path import expanduser,join as osjoin

# %%
with DAG('scrape_games',default_args={'retries': 4,'owner':'blunt10k'},description='Data injector to calendar table',
schedule_interval='0 * * * *',catchup=False,tags=['nba_stats'],
start_date=pendulum.datetime(2023, 12, 10, tz="UTC")) as dag:

    dag.doc_md = __doc__

    code_directory = expanduser(osjoin('~/airflow','dags','NBA','scraper'))
    sys.path.insert(0,code_directory)
    cwd = expanduser(osjoin('~/airflow','dags','NBA','scraper'))


    from get_scrape_data import write_to_db
    from db_utils import update_calendar

    @task(task_id="write_scrape_logs_to_db")
    def scrape_logs_to_db():
        write_to_db()
    
    @task(task_id="update_calendar",retries=0)
    def update_calendar_func():
        update_calendar()


    scrape_games = BashOperator(task_id="scrape_pbp",bash_command="bash scrape_games.sh ",cwd=cwd)
    failed_scrapes = BashOperator(task_id="get_failed_scrapes",bash_command="bash failed_games.sh ",cwd=cwd)
    load_logs = scrape_logs_to_db()
    update_scraped_games = update_calendar_func()

    scrape_games >> load_logs >> failed_scrapes >> update_scraped_games
from time import strftime,localtime
from web_scraper import *

def get_last_year(year):
        if(year > 2000):
            return year % 2000
        return year % 100

def player_boxes(**kwargs):
    from stats import Box

    bs = Box_scores()
    year = int(strftime("%Y"))

    start_reg = 9
    end_reg = 4
    start_post = end_reg
    end_post = 7
    reg_season = True

    month = int(strftime('%m'))
    year_range = str(year-1) + "-{:0>2d}".format(get_last_year(year))

    ti = kwargs['ti']
    if month <= end_reg or month >= start_reg:

        url = bs.build_url(year_range, not reg_season)
        return bs.iter_all(url)

    elif month >= start_post and month <= end_post:

        url = bs.build_url(year_range, not reg_season)
        return bs.iter_all(url,)

        from airflow import DAG

from airflow import DAG

from airflow.operators.python import PythonOperator

with DAG('')
# %%
from datetime import date as date_class
from datetime import timedelta, datetime
import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable


def make_engine(host, port, user, pswd, db):

    return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")


def get_quarter(p_date: date_class) -> int:
    return (p_date.month - 1) // 3 + 1


def get_first_day_of_the_quarter(p_date: date_class):
    return datetime(p_date.year, 3 * ((p_date.month - 1) // 3) + 1, 1)


def get_last_day_of_the_quarter(p_date: date_class):
    quarter = get_quarter(p_date)
    return datetime(p_date.year + 3 * quarter // 12, 3 * quarter % 12 + 1, 1) + timedelta(days=-1)
# %%

def create_connector():
    host = Variable.get('HOSTNAME')
    db = Variable.get('NBA_DB')
    port = Variable.get('PORT')
    user = Variable.get('USER')
    pswd = Variable.get('PSWD!')

    conn = make_engine(host, port, user, pswd, db)
    
    return conn


def create_record():
    conn = create_connector()
    table = 'calendar'

    df = pd.DataFrame(data=dict(game_date = [datetime.today()],
                                quarter_from = [get_first_day_of_the_quarter(datetime.today())],
                                quarter_to = [get_last_day_of_the_quarter(datetime.today())]))
    
    
    df.to_sql(table, conn, if_exists = 'append', index = False)
    conn.dispose()

    return

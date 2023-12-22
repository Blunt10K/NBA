from sqlalchemy import create_engine, text
from airflow.models import Variable
from datetime import timedelta as td

def make_engine():
    host = Variable.get('HOSTNAME')
    db = Variable.get('NBA_DB')
    port = Variable.get('PORT')
    user = Variable.get('USER')
    pswd = Variable.get('PSWD')

    return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")

def get_latest(connection):

    latest = '''SELECT max(game_date) from calendar 
            where scraped = TRUE'''

    t = text(latest)
    latest_scrape = connection.execute(t).first()[0]

    return latest_scrape


def get_bounds(connection, latest_scrape):
    query = f'''SELECT min(game_date), max(game_date) from calendar
            where
            (to_date('{(latest_scrape + td(30)).strftime('%Y-%m-%d')}',
                'YYYY-MM-DD')
                between quarter_from and quarter_to
            ) and
            game_date > to_date(
                '{(latest_scrape).strftime('%Y-%m-%d')}','YYYY-MM-DD')
            '''

    t = text(query)

    dates = connection.execute(t)
    min_date, max_date = dates.first()

    return min_date, max_date


def update_query(min_date, max_date):

    lower_bound = f'''to_date('{min_date.strftime('%Y-%m-%d')}',
                'YYYY-MM-DD')'''
    
    upper_bound = f'''to_date('{max_date.strftime('%Y-%m-%d')}',
                'YYYY-MM-DD')'''

    update = f'''UPDATE calendar
                SET scraped = True
                where
                game_date between {lower_bound} and {upper_bound}
            '''
    
    return update

def update_calendar():

    conn = make_engine()

    
    connection = conn.connect()

    latest_scrape = get_latest(connection)

    min_date, max_date = get_bounds(connection, latest_scrape)


    t = text(update_query(min_date, max_date))
    
    connection.execute(t)
    connection.commit()

    connection.close()

    return
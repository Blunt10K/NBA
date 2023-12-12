from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime as dt, timedelta as td
import json
from os.path import join
import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable


def make_engine():
    host = Variable.get('HOSTNAME')
    db = Variable.get('NBA_DB')
    port = Variable.get('PORT')
    user = Variable.get('USER')
    pswd = Variable.get('PSWD')

    return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")


def game_dates():
    engine = make_engine()
    latest_scrape = pd.read_sql('SELECT max(game_date) as latest from scraped_games', engine)
    latest_scrape = latest_scrape.loc[0,'latest']

    if latest_scrape:
        query = f'''SELECT game_date from calendar
        where (game_date > to_date({latest_scrape.strftime('%Y-%m-%d')},'YYYY-MM-DD'))
        AND (to_date({(latest_scrape + td(1)).strftime('%Y-%m-%d')},'YYYY-MM-DD') between quarter_from and quarter_to)'''
    else:
        query = f'''SELECT game_date from calendar
        where (game_date > to_date('1996-11-01','YYYY-MM-DD'))
        AND (to_date('1996-11-01','YYYY-MM-DD') between quarter_from and quarter_to)'''

    df = pd.read_sql(query, engine)

    engine.dispose()

    for i in df.itertuples():
        yield 'https://www.nba.com/games?date='+dt.strftime(i.game_date, '%Y-%m-%d')


class GamesSpider(CrawlSpider):

    name = 'pbp-games'
    allowed_domains = ['nba.com']
    start_urls = list(game_dates())
    REDIRECT_ENABLED = False
    # extract_path = join(Variable.get('EXTDISK'),'spark_apps','games','data.json')

    # custom_settings = dict(FEEDS = {extract_path: {'format':'jsonl','overwrite':False}})
    FEEDS = {join(Variable.get('EXTDISK'),'spark_apps','games','data.json') : {'format': 'jsonlines'}}

    rules = [Rule(LinkExtractor(allow=['\w+-vs-\w+-\d+/box-score#box-score']), callback='parse_start_url')]

    

    def parse_start_url(self, response):
        items = response.css('script[type="application/json"]::text')
        # self.logger.info(f"done: {items[0].get()}")

        for i in items:
            yield dict(pbp = json.loads(i.get()))
            # to_write = json.loads(i.get())['props']['pageProps']
            # fname = join(extract_path, to_write['playByPlay']['gameId'] + '.json')
            # with open(fname, 'w') as fp:
            #     json.dump(to_write, fp)
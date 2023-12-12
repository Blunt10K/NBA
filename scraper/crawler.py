from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime as dt, timedelta as td
import json
from os.path import join, expanduser
import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable


class GamesSpider(CrawlSpider):

    def __init__(self, *a, **kw):
        # super().__init__(*a, **kw)
        self.name = 'pbp-games'
        self.allowed_domains = ['nba.com']
        self.start_urls = list(self.game_dates())
        self.REDIRECT_ENABLED = False
        # extract_path = join(Variable.get('EXTDISK'),'spark_apps','games','data.json')

        # custom_settings = dict(FEEDS = {extract_path: {'format':'jsonl','overwrite':False}})

        self.rules = [Rule(LinkExtractor(allow=['\w+-vs-\w+-\d+/box-score#box-score']), callback=self.parse_page)]
    
    @staticmethod
    def make_engine(self):
        host = Variable.get('HOSTNAME')
        db = Variable.get('NBA_DB')
        port = Variable.get('PORT')
        user = Variable.get('USER')
        pswd = Variable.get('PSWD')

        return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")

    @staticmethod
    def game_dates(self):
        engine = self.make_engine()
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

    def parse_page(self, response):
        items = response.css('script[type="application/json"]::text')

        extract_path = join(Variable.get('EXTDISK'),'spark_apps','games')
        print(extract_path)

        for i in items:
            # yield i.get()
            to_write = json.loads(i.get())['props']['pageProps']
            fname = join(extract_path, to_write['playByPlay']['gameId'] + '.json')
            with open(fname, 'w') as fp:
                json.dump(to_write, fp)
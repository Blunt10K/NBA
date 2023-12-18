from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime as dt, timedelta as td
import json
from os.path import join
import pandas as pd
from airflow.models import Variable
import re
from db_utils import make_engine


def game_dates():
    engine = make_engine()
    latest_scrape = pd.read_sql('SELECT max(game_date) as latest from scrape_logs', engine)
    latest_scrape = latest_scrape.loc[0,'latest']

    if latest_scrape:
        query = f'''SELECT game_date from calendar
        where (to_date('{(latest_scrape + td(30)).strftime('%Y-%m-%d')}','YYYY-MM-DD')
        between quarter_from and quarter_to)
        '''
    else:
        query = f'''SELECT game_date from calendar
        where (game_date >= to_date('1996-11-01','YYYY-MM-DD'))
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
    allow_pat = r'game/\w+-vs-\w+-\d+'
    rules = [Rule(LinkExtractor(allow=[allow_pat]), callback='parse_game',follow=True)]

    
    def parse_start_url(self, response):
        script = response.css('script[type="application/json"]::text')
        
        for s in script:
            links = set(re.findall(self.allow_pat, s.get()))
            for link in links:
                yield response.follow(link,callback = self.parse_game)

    def parse_game(self, response):
        items = response.css('script[type="application/json"]::text')

        for i in items:
            extract_path = join(Variable.get('EXTDISK'),'spark_apps','NBA','games')
            to_write = json.loads(i.get())['props']['pageProps']
            fname = join(extract_path, to_write['playByPlay']['gameId'] + '.json')

            with open(fname, 'w') as fp:
                json.dump(to_write, fp)
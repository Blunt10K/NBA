from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime as dt, timedelta as td
import json
from os.path import join
import pandas as pd
from sqlalchemy import create_engine
from airflow.models import Variable
from scrapy.item import Item, Field
import re


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


class PlayByPlay(Item):
    pbp = Field()

    def __repr__(self):
        # """only print out attr1 after exiting the Pipeline"""
        return repr('')
    
class PlayByPlayGroup(Item):
    item = Field()

    def __repr__(self):
        # """only print out attr1 after exiting the Pipeline"""
        return repr('')

class GamesSpider(CrawlSpider):

    name = 'pbp-games'
    allowed_domains = ['nba.com']
    start_urls = list(game_dates())
    REDIRECT_ENABLED = False
    # extract_path = join(Variable.get('EXTDISK'),'spark_apps','games','data.json')

    # custom_settings = dict(FEEDS = {extract_path: {'format':'jsonl','overwrite':False}})
    # FEEDS = {join(Variable.get('EXTDISK'),'spark_apps','games','data.json') : {'format': 'jsonlines'}} \w+\-vs\-\w+\-\d+

    rules = [Rule(LinkExtractor(allow=[r'game/\w+-vs-\w+-\d+']), callback='parse_game',follow=True)]

    allow_pat = 'game/\w+-vs-\w+-\d+'

    
    def parse_start_url(self, response):
        script = response.css('script[type="application/json"]::text')
        
        for s in script:
            for link in re.findall(self.allow_pat, s.get()):
                yield response.follow(link,callback = self.parse_game)

    def parse_game(self, response):
        items = response.css('script[type="application/json"]::text')

        for i in items:
            extract_path = join(Variable.get('EXTDISK'),'spark_apps','games')
            to_write = json.loads(i.get())['props']['pageProps']
            fname = join(extract_path, to_write['playByPlay']['gameId'] + '.json')
            
            with open(fname, 'w') as fp:
                json.dump(to_write, fp)
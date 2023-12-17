
# %%
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import pandas as pd
from sqlalchemy import text as sql_text
from airflow.models import Variable
from os.path import join
import json
from db_utils import make_engine


def list_failed():
    success = '''(select game_title, game_id FROM scrape_logs
    WHERE response = 200) successful_scrape'''
    failed = '''(select game_title as failed_title, game_id as failed_game
    FROM scrape_logs WHERE response <> 200) failed_scrape'''
    condition = '''ON failed_scrape.failed_game = successful_scrape.game_id
    WHERE game_id IS NULL'''
    query = f'''select failed_title, failed_game from {success}
    RIGHT OUTER JOIN {failed} {condition}'''

    conn = make_engine()
    df = pd.read_sql(sql_text(query),conn.connect())

    for i in df.itertuples():
        yield f'https://www.nba.com/game/{i.failed_title}-{i.failed_game}'

# %%
class GamesSpider(CrawlSpider):

    name = 'pbp-games-failed'
    allowed_domains = ['nba.com']
    start_urls = set(list_failed())
    REDIRECT_ENABLED = False
    allow_pat = r'game/\w+-vs-\w+-\d+'
    rules = [Rule(LinkExtractor(allow=[allow_pat]),
                  callback='parse_start_url')]

    
    def parse_start_url(self, response):
        items = response.css('script[type="application/json"]::text')

        for i in items:
            extract_path = join(Variable.get('EXTDISK'),'spark_apps','NBA',
                                'failed_scrapes')
            
            to_write = json.loads(i.get())['props']['pageProps']
            fname = join(extract_path,
                         f"{to_write['playByPlay']['gameId']}.json")

            with open(fname, 'w') as fp:
                json.dump(to_write, fp)

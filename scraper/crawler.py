from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime as dt, timedelta as td
import json
from os.path import join, expanduser

def game_dates():
    start_date = dt(1996,10,8)
    end_date = dt.today()

    days = (end_date - start_date).days

    for i in range(days):
        yield 'https://www.nba.com/games?date='+dt.strftime(start_date + td(i+1), '%Y-%m-%d')

class GamesSpider(CrawlSpider):
    name = 'pbp-games'
    allowed_domains = ['nba.com']
    start_urls = list(game_dates())
    REDIRECT_ENABLED = False

    rules = [Rule(LinkExtractor(allow=['\w+-vs-\w+-\d+/box-score#box-score']), callback='parse_page')]

    def parse_page(self, response):
        items = response.css('script[type="application/json"]::text')

        extract_path = expanduser(join('~','spark_apps','games'))

        for i in items:
            to_write = json.loads(i.get())['props']['pageProps']
            fname = join(extract_path, to_write['playByPlay']['gameId'] + '.json')
            with open(fname, 'w') as fp:
                json.dump(to_write, fp)

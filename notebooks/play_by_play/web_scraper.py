import requests
class Play_by_play:
    # https://www.nba.com/game/<matchup, home team>-<game_id>/box-score

    def __init__(self):
        self.root = "https://www.nba.com/game/" #SACvsPOR-xxxxxxxxxx/box-score"
        self.tail = "/box-score" 

    def build_url(self,matchup, game_id):

        return self.root + matchup + '-' + game_id + self.tail


    def get_source(self, matchup, game_id):
        url = self.build_url(matchup,game_id)
        response = requests.get(url)

        return response.content
    
    def get_pages(self, df):
        for row in df.iterrows():
            yield self.get_source(row[1]['match_up'], row[1]['game_id'])

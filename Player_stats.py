from os.path import exists
from os import mkdir
import pandas as pd

class Player_stats:
    def __init__(self,players):
        self.players = players
        team_abb = pd.read_csv("team_names.csv")
        self.teams = tuple(team_abb["prefix_1"].str.lower())
        del team_abb
        self.root = "./player_stats"
        self.REG = 0
        self.POST = 1
        self.labels =("/regular_season.csv", "/post_season.csv")
        
    def make_dir(self, path):
        if(not exists(path)):
            mkdir(path)
        return path
        
    def get_player_stats(self,last_n_years):
        this_year = strftime("%Y",localtime())
        year = int(this_year)
        
        for y in range(year,year-last_n_years,-1):
            file_dir = self.make_dir(self.root + "/" + str(y-1))
            
            if(exists(file_dir)):
                continue # there already is data on this year, skip
                
            yr = str(y-1)
            
            df = []
            reg_fp = file_dir + self.labels[self.REG]
            
            post_fp = file_dir + self.labels[self.POST]
            
            i = 0
            for t in self.teams:
                url = self.players.build_url(yr,t)
                print(url)
                df = self.players.build_table(url,t)
                
                df.to_csv(reg_fp, index = False,header = i==0, mode = "a")
                
                
                url = self.players.build_url(yr,t,True)
                df = self.players.build_table(url,t)
                df.to_csv(post_fp, index = False,header = i==0, mode = "a")
                i+=1
        
        return
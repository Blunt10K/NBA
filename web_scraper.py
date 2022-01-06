#!/usr/bin/env python

from time import strftime,localtime
import pandas as pd
from os.path import exists


class Team_standings:
    
    def __init__(self):
        team_abbrvs = pd.read_csv("team_names.csv",usecols=["prefix_1"])
        self.team_names = "|".join(list(team_abbrvs["prefix_1"].str.upper()))
        del team_abbrvs
    
    
    def build_table(self,url):
        dfs = pd.read_html(url)
        stats = dfs[1] 
        teams = dfs[0]
        teams = teams.rename(columns={0:"Team"})

        return teams.join(stats)
    
    def gen_key(self, year, season_type):
        return year+"_"+season_type

    def build_url(self, root,year_n, tail,preseason = False):
        if(not preseason):
            return root +  "/" + year_n + tail
        else:
            return root + "/" + year_n + tail
        
    def update_team_standings(self):
        REG = 0
        PRE = 1
        labels =("regular_season", "pre_season")
        this_year = strftime("%Y",localtime())

        
        root = "https://www.espn.com/nba/standings/_"
        tail = "/group/league"
        
        filename = self.gen_key(this_year, labels[REG]) + ".csv"
        filepath = "./team_standings/reg_season/" +filename

        this_year_reg_season = root + tail
        table = self.build_table(this_year_reg_season)
        
        self.preprocess(table,False)
        table.to_csv(filepath, index = False)
        
        filename = self.gen_key(this_year, labels[PRE]) + ".csv"
        filepath = "./team_standings/pre_season/" +filename
        
        this_year_pre_season = root + "/seasontype/pre" + tail
        table = self.build_table(this_year_pre_season)
        
        self.preprocess(table,False)
        table.to_csv(filepath, index = False)

        return
    
    def preprocess(self, df, complete_league = True):
        
        if(complete_league):
            df["Team"] = df["Team"].str.extract(r'(^.+--)(.+)',expand = True)[1]
        
        processed = df["Team"].str.extract(fr'({self.team_names})(.+)',expand=True)
        
        df.insert(0,"ID",processed[0])
        df["Team"] = processed[1]
        
        return df
        
        
    def save_standings(self,filepath,year,preseason = False):
        if(not exists(filepath)):
            return
        
        root = "https://www.espn.com/nba/standings/_"
        tail = "/group/league"
        
        
        if(preseason):
            preseason_root = root + "/seasontype/pre/season"
            season = self.build_url(preseason_root, year, tail)
            table = self.build_table(season)
            self.preprocess(table,False)
        else:
            reg_season_root = root + "/season"
            season = self.build_url(reg_season_root, year, tail)
            table = self.build_table(season)
            self.preprocess(table)
            
        table.to_csv(filepath, index = False)
        
        return

    
    def get_team_standings(self, last_n_years, include_preseason = False):
        REG = 0
        PRE = 1
        labels =("regular_season", "pre_season")
        this_year = strftime("%Y",localtime())

        year = int(this_year)

        for y in range(year,year-last_n_years,-1):
            filename = self.gen_key(str(y-1),labels[REG]) + ".csv"
            filepath = "./team_standings/reg_season/" + filename
            
            self.save_standings(filepath,year = str(y-1))
            
            filename = self.gen_key(str(y-1),labels[PRE]) + ".csv"
            filepath = "./team_standings/pre_season/" + filename
            
            self.save_standings(filepath,year=str(y-1),preseason=True)

                
        return
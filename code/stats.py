from time import strftime,localtime
import pandas as pd
from os.path import exists
from os import mkdir
from selenium import webdriver
from web_scraper import Teams, Players

class Player_stats:
    def __init__(self):
        self.players = Players()        
        self.root = "../player_stats"
        self.REG = 0
        self.POST = 1
        self.labels =("/regular_season.csv", "/playoffs.csv")
        
        
    def write(self,html,pids,tids,fp):
        df = pd.read_html(html)[0]
        df["PLAYER_ID"] = pids
        df["TEAM_ID"] = tids
        
        df = df.dropna('columns')
        df.to_csv(fp)
        return 
    
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100
        
    def get_season(self, driver, year,fp, reg_season=True):
        
        url = self.players.build_url(year,reg_season)
        
        print(url)
        while(1<2):
            try:
                html = self.players.click_all(url, driver)
                pids, tids = self.players.get_player_and_team_ids(html)
                break
            except:
                print("Error. Trying again.")
        
        self.write(html,pids,tids,fp)
        
        return
        
       
    def get_player_stats(self,last_n_years):
        year = int(strftime("%Y",localtime()))-1
        
        with webdriver.Chrome() as driver:
            for y in range(year,year-last_n_years-1,-1):
                year_range = str(y-1) + "-{:0>2d}".format(self.get_last_year(y))

                file_dir = self.root + "/" + year_range

                if(not exists(file_dir)):# there is no data on this year, get it
                    mkdir(file_dir)

                    fp = file_dir + self.labels[self.REG]
                    self.get_season(driver,year_range,fp)


                    fp = file_dir + self.labels[self.POST]
                    self.get_season(driver,year_range,fp,reg_season=False)

        return


class Team_standings:
    
    def __init__(self):
        self.REG = 0
        self.POST = 1
        self.labels =("/regular_season.csv", "/playoffs.csv")
        self.teams = Teams()
        self.root = "../team_standings/"
        
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100


    def save_standings(self,filepath,year,preseason=False):
        if(exists(filepath)):
            return
        
        
        return
    
    def write(self,html,tids,fp):
        df = pd.read_html(html)[0]
        df["TEAM_ID"] = tids
        
        df = df.dropna('columns')
        df.to_csv(fp)
        return 

    def get_season(self, driver, year,fp, reg_season=True):
        
        url = self.teams.build_url(year,reg_season)
        
        print(url)
        
        html,tids = self.teams.get_source_and_teams(url, driver)
        
        self.write(html,tids,fp)
        
        return
    
    def get_team_standings(self,last_n_years):
        this_year = strftime("%Y",localtime())
        year = int(this_year) -  1
        
        with webdriver.Chrome() as driver:
            for y in range(year,year-last_n_years-1,-1):
                year_range = str(y-1) + "-{:0>2d}".format(self.get_last_year(y))
                
                file_dir = self.root + year_range
                if(not exists(file_dir)):# there is no data on this year, get it
                    mkdir(file_dir)
                
                    fp = file_dir + self.labels[self.REG]
                    self.get_season(driver,year_range,fp)

                    fp = file_dir + self.labels[self.POST]
                    self.get_season(driver,year_range,fp,reg_season=False)

        
        return
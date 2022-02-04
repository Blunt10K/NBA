from time import strftime,localtime
import pandas as pd
from os.path import exists
from os import mkdir
from selenium import webdriver
from web_scraper import Teams, Players

<<<<<<< HEAD
=======
from sqlalchemy import create_engine
from os import environ


def add_new_players(engine, names, ids):
    condition = str(tuple(ids))
    existing_players = pd.read_sql("select * from Players where ID IN "+condition,engine)
        
    c = pd.DataFrame({"ID":ids,"Name":names}).drop_duplicates()
    e = c.merge(existing_players,on="ID",how='left',indicator=True,suffixes = ('','_y'))
    e = e.loc[e["_merge"]== "left_only"][["ID","Name"]]
        
    e.to_sql("Players",engine,index=False, if_exists="append")
    
    return

def add_new_box_scores(engine,df):
    existing = pd.read_sql("select * from Box_scores",engine)
    
    e = df.merge(existing,on=["Player_ID","Team_ID","Game_ID"],how='left',indicator=True,suffixes = ('','_y'))
    e = e.loc[e["_merge"]== "left_only"][df.columns]
    
    e.to_sql("Box_scores",engine,index=False, if_exists="append")
    
    return

>>>>>>> oldPandas
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


<<<<<<< HEAD
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
=======
    def write(self,html,tids,fp):
        df = pd.read_html(html)[0]
        df["TEAM_ID"] = tids

        df = df.dropna('columns')
        df.to_csv(fp)
        return
>>>>>>> oldPandas

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

        
<<<<<<< HEAD
=======
        return


class Box:
    def __init__(self,boxes):
        self.boxes = boxes        
        self.table = "Box_scores"
        self.scores =[]
        self.page_count = pd.read_csv("../box_score.csv")
        self.engine = create_engine("mariadb+mariadbconnector://"\
                                  +environ.get("USER")+":"\
                                  +environ.get("PSWD")+"@127.0.0.1:3306/nba")
        
        self.db_columns = ['Player_ID', 'Team_ID', 'Game_ID', 'Matchup', 'Game_day', 'Result',
                        'MINS', 'PTS', 'FGM', 'FGA', 'FGP', 'PM3', 'PA3', 'P3P', 'FTM', 'FTA',
                        'FTP', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',  'PF']

        
    def write(self,html,pids,tids,gids):
        df = pd.read_html(html,na_values=['-'])[0]
        self.scores = df
        df = df.drop(columns = ['Season','+/-','FP'])
        
        add_new_players(self.engine, df[df.columns[0]],pids)
        df = df[df.columns[2:]]
        
        d = dict(zip(df.columns,self.db_columns[3:]))
        df = df.rename(columns=d)
        
        df.insert(0, "Player_ID",pids)
        df.insert(1, "Team_ID",tids)
        df.insert(2, "Game_ID",gids)
        
        
        df['Game_day'] = pd.to_datetime(df['Game_day'])
        
        df = df[self.db_columns]
        df = df.drop_duplicates()

        add_new_box_scores(self.engine,df)
        
        return 
    
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100
        
    def get_season(self, driver, year, reg_season=True):
        
        url = self.boxes.build_url(year,reg_season)
        
#         box_key = int(year.split("-")[0])+1
#         pages = 
        for html in self.boxes.iter_all(url, driver):
            pids, tids, gids = self.boxes.get_player_and_team_ids(html)
            self.write(html,pids,tids,gids)
        
        return
        
       
    def get_player_stats(self,year,reg_season = True):
        with webdriver.Chrome() as driver:
            year_range = str(year-1) + "-{:0>2d}".format(self.get_last_year(year))

            self.get_season(driver,year_range,reg_season)

>>>>>>> oldPandas
        return
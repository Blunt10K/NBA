from time import strftime,localtime
import pandas as pd
from os.path import exists
from os import mkdir
from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

from web_scraper import Teams, Players,Box_scores,Team_box_scores

from sqlalchemy import create_engine
from os import environ



class Player_stats:
    def __init__(self):
        self.players = Players()        
        self.REG = "002"
        self.POST = "004"
        self.db_columns = ['Player_ID', 'Team_ID', 'Age', 'GP', 'W', 'L', 'MINS', 'PTS', 'FGM',
                           'FGA', 'FGP', 'PM3', 'PA3', 'P3P', 'FTM', 'FTA', 'FTP', 'OREB', 'DREB',
                           'REB', 'AST', 'TOV', 'STL', 'BLK', 'PF', 'DD2', 'TD3', 'Season_ID']
        self.engine = create_engine("mariadb+mariadbconnector://"\
                                  +environ.get("USER")+":"\
                                  +environ.get("PSWD")+"@127.0.0.1:3306/nba")
        
        
    def write(self,html,pids,tids,season_id):
        df = pd.read_html(html)[0]
        
        df = df.drop(columns = ['PLAYER','TEAM','+/-'])
        df = df.dropna('columns')

        
        d = dict(zip(df.columns[1:],self.db_columns[2:-1]))
        df = df.rename(columns=d)
        
        
        df.insert(0,"Player_ID",pids)
        df.insert(1,"Team_ID",tids)
        df.insert(len(self.db_columns)-1,"Season_ID",season_id)
        
        df = df[self.db_columns]
        
        df.to_sql("Seasonal_performance",self.engine,index=False, if_exists="append")
        
        return 
    
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100
        
    def get_season(self, driver, year,season_id, reg_season=True):
        
        url = self.players.build_url(year,reg_season)
        
        # print(url)

        html = self.players.click_all(url, driver)
        pids, tids = self.players.get_player_and_team_ids(html)
        
        self.write(html,pids,tids,season_id)
        
        return
        
       
    def get_player_stats(self,last_n_years):
        year = int(strftime("%Y",localtime()))
        
        with webdriver.Chrome() as driver:
            for y in range(year,year-last_n_years-1,-1):
                id_year = "{:0>2d}".format(self.get_last_year(y-1))
                
                select = "select SEASON_ID from Seasonal_performance "
                condition = "where SEASON_ID LIKE '%" + id_year+"'"
                limit = " limit 10"
                
                query = select + condition +limit
                d = pd.read_sql(query,self.engine)

                if(len(d)== 0):# there is no data on this year, get it
                    year_range = str(y-1) + "-{:0>2d}".format(self.get_last_year(y))
                    season_id = self.REG + id_year
                    self.get_season(driver,year_range,season_id)

                    season_id = self.POST + id_year
                    self.get_season(driver,year_range,season_id,reg_season=False)

        return

class Team_standings:
    
    def __init__(self):
        self.REG = "002"
        self.POST = "004"
        self.teams = Teams()
        self.db_columns = ['SEASON_ID', 'TEAM_ID', 'GP', 'W', 'L', 'WINP', 'MINS', 'PTS', 'FGM',
                        'FGA', 'FGP', 'PM3', 'PA3', 'P3P', 'FTM', 'FTA', 'FTP', 'OREB', 'DREB',
                        'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD']
        self.engine = create_engine("mariadb+mariadbconnector://"\
                                  +environ.get("USER")+":"\
                                  +environ.get("PSWD")+"@127.0.0.1:3306/nba")
        
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100

    
    def write(self,html,tids,season_id):
        df = pd.read_html(html)[0]
        df = df.drop(columns = ['TEAM','+/-'])
        df = df.dropna('columns')
        
        d = dict(zip(df.columns,self.db_columns[2:]))
        df = df.rename(columns=d)
        
        df["TEAM_ID"] = tids
        df["SEASON_ID"] = season_id
        
        
        df = df[self.db_columns]
        df = df.drop_duplicates()
        df.to_sql("Team_standings",self.engine,index=False, if_exists="append")
        
        return 

    def get_season(self, driver, year,season_id, reg_season=True):
        
        url = self.teams.build_url(year,reg_season)
        
        # print(url)
        
        html,tids = self.teams.get_source_and_teams(url, driver)
        
        self.write(html,tids,season_id)
        
        return
    
    def get_team_standings(self,last_n_years):
        this_year = strftime("%Y",localtime())
        year = int(this_year) -  1
        
        with webdriver.Chrome() as driver:
            for y in range(year,year-last_n_years-1,-1):
                id_year = "{:0>2d}".format(self.get_last_year(y-1))
                
                select = "select SEASON_ID from Team_standings "
                condition = "where SEASON_ID LIKE '%" + id_year+"'"
                limit = " limit 10"
                
                query = select + condition +limit
                d = pd.read_sql(query,self.engine)
                if(len(d)== 0):# there is no data on this year, get it
                    year_range = str(y-1) + "-{:0>2d}".format(self.get_last_year(y))
                    season_id = self.REG + id_year
                    self.get_season(driver,year_range,season_id)

                    season_id = self.POST + id_year
                    self.get_season(driver,year_range,season_id,reg_season=False)

        
        return

class Box:
    def __init__(self):
        self.boxes = Box_scores()        
        self.table = "Box_scores"
        self.scores =[]
        command = 'SELECT MAX(Game_day) as GD from Box_scores'

        self.engine = create_engine("mariadb+mariadbconnector://"\
                                  +environ.get("USER")+":"\
                                  +environ.get("PSWD")+"@127.0.0.1:3306/nba")

        self.max_date = pd.read_sql(command,self.engine,parse_dates=['GD'])
        
        self.db_columns = ['Player_ID', 'Team_ID', 'Game_ID', 'Matchup', 'Game_day', 'Result',
                        'MINS', 'PTS', 'FGM', 'FGA', 'FGP', 'PM3', 'PA3', 'P3P', 'FTM', 'FTA',
                        'FTP', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',  'PF']

    def add_new_players(self, names, ids):
        condition = str(tuple(ids))
        existing_players = pd.read_sql("select * from Players where ID IN "+condition,self.engine)
            
        c = pd.DataFrame({"ID":ids,"Name":names}).drop_duplicates()
        e = c.merge(existing_players,on="ID",how='left',indicator=True,suffixes = ('','_y'))
        e = e.loc[e["_merge"]== "left_only"][["ID","Name"]]
            
        e.to_sql("Players",self.engine,index=False, if_exists="append")
        
        return

    def add_new_box_scores(self,df):
        existing = pd.read_sql("select * from Box_scores",self.engine)
        
        e = df.merge(existing,on=["Player_ID","Team_ID","Game_ID"],how='left',indicator=True,suffixes = ('','_y'))
        e = e.loc[e["_merge"]== "left_only"][df.columns]
        
        e.to_sql("Box_scores",self.engine,index=False, if_exists="append")
        
        return   

    def write(self,df):        
                
        df = df[self.db_columns]
        df = df.drop_duplicates()
        df = df.dropna(subset = ['Result'])
        self.add_new_box_scores(df)
        
        return
    
    def preprocess(self,html, pids, tids, gids):
        df = pd.read_html(html,na_values=['-'])[0]
        df = df.drop(columns = ['Season','+/-','FP'])

        self.add_new_players(df[df.columns[0]],pids)
        df = df[df.columns[2:]]

        d = dict(zip(df.columns,self.db_columns[3:]))
        df = df.rename(columns=d)
        
        df.insert(0, "Player_ID",pids)
        df.insert(1, "Team_ID",tids)
        df.insert(2, "Game_ID",gids)
        df['Game_day'] = pd.to_datetime(df['Game_day'])
        
        
        return df

        
    def get_season(self, driver, year, reg_season=True):
        
        url = self.boxes.build_url(year,reg_season)
        df = pd.DataFrame()
        
        for html in self.boxes.iter_all(url, driver):
            pids, tids, gids = self.boxes.get_player_and_team_ids(html)
            df = pd.concat((df,self.preprocess(html,pids, tids, gids)))  

            if self.max_date['GD'].max() > df['Game_day'].max():
                break

                
        self.write(df)
        
        return
         
       
    def get_player_stats(self,year,reg_season = True):
        with webdriver.Chrome() as driver:
            year_range = str(year-1) + "-{:0>2d}".format(self.get_last_year(year))

            self.get_season(driver,year_range,reg_season)

        return

    @staticmethod
    def get_last_year(year):
        if(year > 2000):
            return year % 2000
        return year % 100

class Team_Box:
    def __init__(self):
        self.boxes = Team_box_scores()        
        self.table = "Team_box_scores"
        self.scores =[]
#         self.page_count = pd.read_csv("../box_score.csv")
        self.engine = create_engine("mariadb+mariadbconnector://"\
                                  +environ.get("USER")+":"\
                                  +environ.get("PSWD")+"@127.0.0.1:3306/nba")
        
        self.db_columns = ['Team_ID', 'Game_ID', 'Matchup', 'Game_day', 'Result',
                        'MINS', 'PTS', 'FGM', 'FGA', 'FGP', 'PM3', 'PA3', 'P3P', 'FTM', 'FTA',
                        'FTP', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV',  'PF']
        
    def add_new_box_scores(self,df):
        existing = pd.read_sql("select * from "+self.table,self.engine)

        e = df.merge(existing,on=["Team_ID","Game_ID"],how='left',indicator=True,suffixes = ('','_y'))
        e = e.loc[e["_merge"]== "left_only"][df.columns]

        e.to_sql(self.table,self.engine,index=False, if_exists="append")

        return
    # TODO: Update column renaming     
    def write(self,html,tids,gids):
        df = pd.read_html(html,na_values=['-'])[0]
        self.scores = df
        df = df.drop(columns = ['Season','+/-'])
        
#         add_new_players(self.engine, df[df.columns[0]],pids)
        df = df[df.columns[1:]]
        
        d = dict(zip(df.columns,self.db_columns[2:]))
        df = df.rename(columns=d)
        
        df.insert(0, "Team_ID",tids)
        df.insert(1, "Game_ID",gids)
        
        
        df['Game_day'] = pd.to_datetime(df['Game_day'])
        
        df = df[self.db_columns]
        df = df.drop_duplicates()

        self.add_new_box_scores(df)
        
        return 
    
    def get_last_year(self,year):
        if(year > 2000):
            return year % 2000
        return year % 100
        
    def get_season(self, driver, year, reg_season=True):
        
        url = self.boxes.build_url(year,reg_season)
        
        for html in self.boxes.iter_all(url, driver):
            tids, gids = self.boxes.get_player_and_team_ids(html)
            self.write(html,tids,gids)
        
        return
        
       
    def get_team_stats(self,year,reg_season = True):
        with webdriver.Chrome() as driver:
            year_range = str(year-1) + "-{:0>2d}".format(self.get_last_year(year))

            self.get_season(driver,year_range,reg_season)

        return

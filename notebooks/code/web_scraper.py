from bs4 import BeautifulSoup
import re
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from re import search
import pandas as pd

class Teams:
    def __init__(self):
        self.root = "https://www.nba.com/stats/teams/traditional/?"
        self.REG = "Regular%20Season"
        self.POST = "Playoffs"
        self.mid = "Season=" # +[year] YYYY-YY +
        self.tail = "&SeasonType=" # + [Regular%20Season|Playoffs]
#             self.xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table"

    def build_url(self,year,reg_season = False):
        if(reg_season):
            return self.root + self.mid + year + self.tail + self.REG

        return self.root + self.mid + year + self.tail + self.POST

    def get_team_ids(self,html):
        soup = BeautifulSoup(html,'html.parser')
        table = soup.find("table")

        tids = []
        team_reg = '/team/\d+'

        for l in table.find_all('a'):
            team_match = re.search(team_reg,l.get('href'))

            if(team_match):
                team_id = int(re.search('\d+',team_match.group()).group())
            team_match = search(team_reg,l.get('href'))

            if(team_match):
                team_id = int(search('\d+',team_match.group()).group())
                tids.append(team_id)

        return tids

    def get_source_and_teams(self, url, driver):
        while(1<2):
            try:
                driver.get(url)
                html = driver.page_source
                return html, self.get_team_ids(html)
            except:
                pass


class Players:
    def __init__(self):
        self.REG = "Regular%20Season"
        self.POST = "Playoffs"
        self.root = "https://www.nba.com/stats/players/traditional/?" # + [teamname -prefix_1] +
        self.mid = "Season=" # +[year] YYYY-YY +
        self.tail = "&SeasonType=" # + [Regular%20Season|Playoffs]
        self.xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select"

    def build_url(self,year,reg_season = False):
        if(reg_season):
            return self.root + self.mid + year + self.tail + self.REG

        return self.root + self.mid + year + self.tail + self.POST

    def click_all(self, url, driver):
        driver.get(url)
        s = driver.find_element(By.XPATH,self.xpath)
        s = Select(s)
        s.select_by_visible_text("All")

        return driver.page_source


    def get_player_and_team_ids(self,html):

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table")

        pids = []
        tids = []

        player_reg = '/player/\d+'
        team_reg = '/team/\d+'

        for l in table.find_all('a'):
            player_match = re.search(player_reg,l.get('href'))

            team_match = re.search(team_reg,l.get('href'))

            if(player_match):
                player_id = int(re.search('\d+',player_match.group()).group())
                pids.append(player_id)
            elif(team_match):
                team_id = int(re.search('\d+',team_match.group()).group())
                tids.append(team_id)

        return pids, tids


class Box_scores:
        def __init__(self):
            self.REG = "Regular%20Season"
            self.POST = "Playoffs"
            self.root = "https://www.nba.com/stats/players/boxscores/?" # + [teamname -prefix_1] +
            self.mid = "Season=" # +[year] YYYY-YY +
            self.tail = "&SeasonType=" # + [Regular%20Season|Playoffs]
            self.xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table"
            self.select_xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select"
            
<<<<<<< Updated upstream
        def build_url(self,year,reg_season = False):
=======
        def build_url(self,year,s,reg_season = False):
            form = '%m-%d-%Y'
            d = datetime.datetime
            e = datetime.date.today() 

            s = d.strftime(s,form)
            e = d.strftime(e,form)
            start = '&DateFrom='+ s.replace('-','%2F')
            end = '&DateTo='+ e.replace('-','%2F')
            
>>>>>>> Stashed changes
            if(reg_season):
                return self.root + self.mid + year + self.tail + self.REG + start + end 
            
            return self.root + self.mid + year + self.tail + self.POST + start + end
        
        
        def iter_all(self, url, driver):
            wait = 20
            driver.get(url)
            element = WebDriverWait(driver,wait).until(EC.presence_of_element_located((By.XPATH,self.xpath)))
            s = driver.find_element(By.XPATH,self.select_xpath)
            t = s.text
            t = t.split("\n")

            
            for i in t[1:]:
                s = driver.find_element(By.XPATH,self.select_xpath)
                s = Select(s)
                s.select_by_visible_text(i)
                yield driver.page_source
            

            return
            
        
        def get_player_and_team_ids(self,html):
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find("table")
            
            pids = []
            tids = []
            gids = []
            
            player_reg = '/player/\d+'
            team_reg = '/team/\d+'
            game_reg = '/game/\d+'

            for l in table.find_all('a'):
                player_match = search(player_reg,l.get('href'))

                team_match = search(team_reg,l.get('href'))
                
                game_match = search(game_reg,l.get('href'))

                if(player_match):
                    player_id = int(search('\d+',player_match.group()).group())
                    pids.append(player_id)
                elif(team_match):
                    team_id = int(search('\d+',team_match.group()).group())
                    tids.append(team_id)
                elif(game_match):
                    game_id = search('\d+',game_match.group()).group()
                    gids.append(game_id)
                    
            return pids, tids, gids


class Team_box_scores:
    def __init__(self):
        self.REG = "Regular%20Season"
        self.POST = "Playoffs"
        self.root = "https://www.nba.com/stats/teams/boxscores/?" # + [teamname -prefix_1] +
        self.mid = "Season=" # +[year] YYYY-YY +
        self.tail = "&SeasonType=" # + [Regular%20Season|Playoffs]
        self.xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[2]/div[1]/table"
        self.select_xpath = "/html/body/main/div/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select"

    def build_url(self,year,reg_season = False):
        if(reg_season):
            return self.root + self.mid + year + self.tail + self.REG #+ self.date + d

        return self.root + self.mid + year + self.tail + self.POST #8+ self.date + d


    def iter_all(self, url, driver):
        wait = 10
        driver.get(url)
        element = WebDriverWait(driver,wait).until(EC.presence_of_element_located((By.XPATH,self.xpath)))
        s = driver.find_element(By.XPATH,self.select_xpath)
        t = s.text
        t = t.split("\n")

        for i in t[1:]:
            s = driver.find_element(By.XPATH,self.select_xpath)
            s = Select(s)
            s.select_by_visible_text(i)
            yield driver.page_source

        return


    def get_player_and_team_ids(self,html):

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find("table")

        tids = []
        gids = []

        team_reg = '/team/\d+'
        game_reg = '/game/\d+'

        for l in table.find_all('a'):

            team_match = search(team_reg,l.get('href'))

            game_match = search(game_reg,l.get('href'))

            if(team_match):
                team_id = int(search('\d+',team_match.group()).group())
                tids.append(team_id)
            elif(game_match):
                game_id = search('\d+',game_match.group()).group()
                gids.append(game_id)

        return tids, gids
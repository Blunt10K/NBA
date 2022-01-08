import pandas as pd
# import requests as req
# from requests.exceptions import Timeout 

class Teams:
    def __init__(self):
        self.root = "https://www.espn.com/nba/standings/_"
        self.tail = "/group/league"
        team_abbrvs = pd.read_csv("team_names.csv",usecols=["prefix_1"])
        self.team_names = "|".join(list(team_abbrvs["prefix_1"].str.upper()))
        del team_abbrvs
        
    def build_url(self,year_n,current = True,preseason = False):
        if(current and not preseason):
            return self.root + self.tail
        elif(current and preseason):
            return self.root + "/seasontype/pre" + self.tail
        elif(not current and preseason):
            return self.root + "/seasontype/pre/season/" + year_n + self.tail
        else:
            return self.root + "/season/" + year_n + self.tail
        

    def correct_teams(self, df):
        teams = df
        first = teams.columns[0]
        row_0 = pd.DataFrame([first],columns=["Team"])
        teams = teams.rename(columns={first:"Team"})
        teams = pd.concat([row_0,teams],ignore_index=True)

        return teams
    
    def preprocess(self,df, complete_league = True):
        if(complete_league):
            df["Team"] = df["Team"].str.extract(r'(.+--)(.+)', expand = True)[1]

        processed = df["Team"].str.extract(fr'({self.team_names})(.+)', expand = True)

        df.insert(0,"ID",processed[0])
        df["Team"] = processed[1]

        return df

    def build_table(self, url,complete_league=True):
        # try:
        #     page = req.get(url)
        # except Timeout:
        dfs = pd.read_html(url,match=".+ | \n")
        stats = dfs[1] 
        teams = self.correct_teams(dfs[0]) # Needed to correct empty table header on espn site
        table = teams.join(stats)

        return self.preprocess(table,complete_league)


class Players:
    def __init__(self):
        self.REG = "2"
        self.POST = "3"
        self.root = "https://www.espn.com/nba/team/stats/_/name" # + [teamname -prefix_1] +
        self.mid = "/season" # +[year] YYYY +
        self.tail = "/seasontype" # + [2|3] 2 = regular season, 3 = postseason
        team_abbrvs = pd.read_csv("team_names.csv",usecols=["prefix_1"])
        self.team_names = "|".join(list(team_abbrvs["prefix_1"].str.upper()))
        del team_abbrvs
        
    def build_url(self,year,team,postseason = False):
        if(postseason):
            return self.root + "/" + team + self.mid + "/" +year + self.tail + "/" +self.POST
        
        return self.root + "/" + team + self.mid + "/" +year + self.tail + "/" +self.REG
    
    def preprocess(self,df,shooting = True):
        processed = df["Name"].str.extract(r'(.+ | Total)([A-Z]+\**)',expand = True)
        
        processed = processed.drop([len(processed)-1])
        
        if(shooting):
            df.insert(1,"POS",processed[1])
            
        df["Name"] = processed[0].str.strip()
        
        df = df.drop([len(df)-1])

        return df
        
    def build_table(self, url, team):
        dfs = pd.read_html(url)
        
        players = pd.concat([dfs[0],dfs[1]],axis=1)
        shooting = pd.concat([dfs[2],dfs[3]],axis=1)
        
        players = self.preprocess(players,False)
        shooting = self.preprocess(shooting)
        
        table = shooting.join(players.set_index("Name"),on = "Name")
        table["Team"] = team.upper()

        return table
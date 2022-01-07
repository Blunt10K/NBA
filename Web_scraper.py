import pandas as pd

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
        dfs = pd.read_html(url,match=".+ | \n")
        stats = dfs[1] 
        teams = self.correct_teams(dfs[0]) # Needed to correct empty table header on espn site
        table = teams.join(stats)

        return self.preprocess(table,complete_league)
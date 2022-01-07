class Team_standings:
    
    def __init__(self, teams):
        self.REG = 0
        self.PRE = 1
        self.labels =("regular_season", "pre_season")
        self.teams = teams
        self.reg_fp = "./team_standings/reg_season/"
        self.pre_fp = "./team_standings/pre_season/"


    def gen_key(self, year, season_type):
        return year+"_"+season_type

    
    def save_standings(self,filepath,year,preseason=False):
        if(exists(filepath)):
            return
        
        current = False
        season = self.teams.build_url(year,current, preseason)

        if(preseason):
            table = self.teams.build_table(season,False)
        else:
            table = self.teams.build_table(season)
            
        table.to_csv(filepath,index = False)
        
        return

    def update_team_standings(self):
        this_year = strftime("%Y",localtime())

        filename = self.gen_key(this_year,self.labels[self.REG]) + ".csv"
        filepath = self.reg_fp + filename
        
        reg_season = self.teams.build_url(this_year)
        table = self.teams.build_table(reg_season,False)
        table.to_csv(filepath,index = False)
        
        
        filename = self.gen_key(this_year,self.labels[self.PRE]) + ".csv"
        filepath =  self.pre_fp + filename
        
        pre_season = self.teams.build_url(this_year,preseason = True)
        table = self.teams.build_table(pre_season,False)
        table.to_csv(filepath,index = False)
    
        return
        
        
    
    def get_team_standings(self,last_n_years):
        this_year = strftime("%Y",localtime())
        year = int(this_year)

        for y in range(year,year-last_n_years,-1):
            filename = self.gen_key(str(y-1),self.labels[self.REG]) + ".csv"
            filepath = self.reg_fp + filename
            self.save_standings(filepath,str(y-1))
            
            
            filename = self.gen_key(str(y-1),self.labels[self.PRE]) + ".csv"
            filepath = self.pre_fp + filename
            self.save_standings(filepath,str(y-1),True)
        
        return
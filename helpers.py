import pandas as pd

def segment_data(df):
    pos_dict = {}
    pos = ['PG','SG','PF','SF','C','F','G']
    
    for p in pos:
        pos_dict[p] = df.loc[df['POS'] == p]
        
    return pos_dict

def get_data(last_n_years,season):
    from time import strftime, localtime
    import pandas as pd
    
    this_year = int(strftime("%Y",localtime())) -1
    dfs = {}
    for y in range(this_year,this_year - last_n_years,-1):
        df = pd.read_csv("./player_stats/"+str(y)+"/"+season+".csv")
        dfs[y] = segment_data(df)
        
    return dfs
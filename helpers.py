def segment_data(df):
    pos_dict = {}
    pos = ['PG','SG','PF','SF','C','F','G']

    for p in pos:
        pos_dict[p] = df.loc[df['POS'] == p]

    return pos_dict

def get_data(season,last_n_years=5):
    from time import strftime, localtime
    import pandas as pd

    url_base = 'https://github.com/Blunt10K/NBA/blob/dash/'
    this_year = int(strftime("%Y",localtime())) -1
    dfs = {}
    for y in range(this_year,this_year - last_n_years,-1):
        url = url_base + str(y)+"_"+season+".csv"
        df = pd.read_csv(url)
        dfs[y] = segment_data(df)

    return dfs

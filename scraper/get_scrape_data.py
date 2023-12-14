# %%
import re
import pandas as pd

# %%
with open('results.log','r') as fp:
    logs = fp.read().split('\n')

# %%
search_pat = r'[\s\S]+DEBUG: Crawled \((\d+)\)[\S\s]+https://www.nba.com/game/(\w+-vs-\w+)-(\d+)[\s\S]+\([\s\S]+https://www.nba.com/games\?date=(\d+-\d+-\d+)'
# [dict(response = )]
# %%

data = [dict(zip(['response','vs','game_id','gate_date'],re.search(search_pat,i).groups())) for i in logs if re.search(search_pat,i)]

# %%
data[:10]
# %%
df = pd.DataFrame(data)
# %%
df
# %%

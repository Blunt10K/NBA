from time import strftime,localtime
from stats import Box

bs = Box()
year = int(strftime("%Y"))

start_reg = 9
end_reg = 4
start_post = end_reg
end_post = 7
reg_season = True

month = int(strftime('%m'))

if month <= end_reg or month >= start_reg:
    bs.get_player_stats(year,reg_season)

elif month >= start_post and month <= end_post:
    bs.get_player_stats(year, not reg_season)
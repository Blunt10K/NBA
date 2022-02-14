from time import strftime,localtime
from stats import Box

bs = Box()
year = int(strftime("%Y"))

bs.get_player_stats(year)
from os.path import join as osjoin
def players(df,root):
    cols = ['player_id','player']

    rename_cols = ['id','name']

    player_df = df.select(*cols).distinct()

    player_df = player_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'players')

    player_df.write.mode('append').parquet(path)


def teams(df,root):
    cols = ['team_id','team']
    rename_cols = ['id','name']

    team_df = df.select(*cols).distinct()

    team_df = team_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'teams')

    team_df.write.mode('append').parquet(path)

# %%
def box_scores(df,root):
    cols = ['player_id','team_id', 'game_id', 'mins', 'pts', 'fgm', 'fga', 'pm3', 'pa3', 'ftm', 'fta', 'oreb',
        'dreb', 'ast', 'stl', 'blk', 'tov', 'pf', 'plus_minus', 'result', 'game_day', 'match_up']

    box_df = df.select(*cols)
    non_null = ['player_id','team_id', 'game_id', 'result', 'game_day', 'match_up']

    box_df = box_df.na.drop(subset=non_null)
    
    path = osjoin(root, 'box_scores')

    box_df.write.mode('append').parquet(path)
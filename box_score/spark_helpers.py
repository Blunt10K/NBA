from os.path import join as osjoin
def players(df,root):
    cols = ['pids','Player']

    rename_cols = ['id','name']

    player_df = df.select(*cols).distinct()

    player_df = player_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'players')

    player_df.write.mode('append').csv(path)


def teams(df,root):
    cols = ['tids','Team']
    rename_cols = ['id','name']

    team_df = df.select(*cols).distinct()

    team_df = team_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'teams')

    team_df.write.mode('append').csv(path)

# %%
def box_scores(df,root):
    cols = ['pids','tids', 'gids', 'MIN', 'PTS', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB',
        'DREB', 'AST', 'STL', 'BLK', 'TOV', 'PF', '+/-', 'W/L', 'Game Date', 'Match Up']

    box_df = df.select(*cols)
    non_null = ['pids','tids', 'gids', 'W/L', 'Game Date', 'Match Up']

    box_df = box_df.na.drop(subset=non_null)
    
    path = osjoin(root, 'box_scores')

    box_df.write.mode('append').csv(path)
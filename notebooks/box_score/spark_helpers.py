from os.path import join as osjoin
def players(df,root):
    cols = ['pids','Player']

    rename_cols = ['id','name']

    player_df = df.select(*cols).distinct()

    player_df = player_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'players')
    checkpoint = osjoin(root, 'checkpoints')

    player_df.writeStream.outputMode('append').format('csv').\
        option('path',path).\
        option('checkpointLocation',checkpoint).start()


def teams(df,root):
    cols = ['tids','Team']
    rename_cols = ['id','name']

    team_df = df.select(*cols).distinct()

    team_df = team_df.withColumnRenamed(cols[0],rename_cols[0]).withColumnRenamed(cols[1],rename_cols[1])

    path = osjoin(root, 'teams')
    checkpoint = osjoin(root, 'checkpoints')

    team_df.writeStream.outputMode('append').format('csv').\
        option('path',path).\
        option('checkpointLocation',checkpoint).start()

# %%
def box_scores(df,root):
    cols = ['pids','tids', 'gids', 'MIN', 'PTS', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB',
        'DREB', 'AST', 'STL', 'BLK', 'TOV', 'PF', '+/-', 'W/L', 'Game Date', 'Match Up']

    box_df = df.select(*cols)

    path = osjoin(root, 'box_scores')
    checkpoint = osjoin(root, 'checkpoints')

    box_df.writeStream.outputMode('append').\
        format('csv').option('path',path).\
        option('checkpointLocation',checkpoint).start()
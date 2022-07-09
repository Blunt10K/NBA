
def players(df,root):
    cols = ['pids','Player']

    rename_cols = ['id','name']

    player_df = df[cols].select('*').distinct()

    player_df = player_df.toDF(*rename_cols)

    path = root + 'queries/players'
    checkpoint = root + 'checkpoints'

    player_df.writeStream.queryName('players').outputMode('append').format('csv').\
        option('path',path).\
        option('checkpointLocation',checkpoint).start()


def teams(df,root):
    cols = ['tids','Team']

    team_df = df[cols].select('*').distinct()

    path = root + 'queries/teams'
    checkpoint = root + 'checkpoints'

    team_df.writeStream.queryName('teams').outputMode('append').format('csv').\
        option('path',path).\
        option('checkpointLocation',checkpoint).start()

# %%
def box_scores(df,root):
    cols = ['pids','tids', 'gids', 'MIN', 'PTS', 'FGM', 'FGA', '3PM', '3PA', 'FTM', 'FTA', 'OREB',
        'DREB', 'AST', 'STL', 'BLK', 'TOV', 'PF', '+/-', 'W/L', 'Game Date', 'Match Up']

    box_df = df[cols]

    path = root + 'queries/players'
    checkpoint = root + 'checkpoints'

    box_df.writeStream.outputMode('append').queryName('box_scores').\
        format('csv').option('path',path).\
        option('checkpointLocation',checkpoint).start()
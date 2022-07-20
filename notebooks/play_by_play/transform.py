def extract_cols(df):
    from pyspark.sql.functions import explode

    pbp = df.withColumn('actions',explode(df.actions)).withColumnRenamed('gameId','game_id')
    
    db = pbp.withColumn('action_id',pbp.actions.getItem('actionId')).\
        withColumn('player_id', pbp.actions.getItem('personId')).\
        withColumn('team_id', pbp.actions.getItem('teamId')).\
        withColumn('period', pbp.actions.getItem('period')).\
        withColumn('clock', pbp.actions.getItem('clock')).\
        withColumn('x_loc', pbp.actions.getItem('xLegacy')).\
        withColumn('y_loc', pbp.actions.getItem('yLegacy')).\
        withColumn('shot_distance', pbp.actions.getItem('shotDistance')).\
        withColumn('shot_result', pbp.actions.getItem('shotResult')).\
        withColumn('field_goal', pbp.actions.getItem('isFieldGoal')).\
        withColumn('home_score', pbp.actions.getItem('scoreHome').cast('integer')).\
        withColumn('away_score', pbp.actions.getItem('scoreAway').cast('integer')).\
        withColumn('total_points', pbp.actions.getItem('pointsTotal')).\
        withColumn('location', pbp.actions.getItem('location')).\
        withColumn('description', pbp.actions.getItem('description')).\
        withColumn('action_type', pbp.actions.getItem('actionType')).\
        withColumn('sub_type', pbp.actions.getItem('subType'))

    return db


def reorder_columns(df):
    table_order = ['game_id', 'action_id', 'player_id', 'team_id', 'period', 'minute',
        'seconds', 'x_loc', 'y_loc', 'shot_distance', 'shot_result',
        'field_goal', 'home_score', 'away_score', 'total_points', 'location',
        'description', 'action_type', 'sub_type']

    return df[table_order]


def write_to_db(df,existing_players,existing_teams,url,user,password):    

    special_events = df.select('*').\
                     filter(f'team_id not in {existing_teams} and player_id not in {existing_players}')
    pbp = df.select('*').filter(f'team_id in {existing_teams} and player_id in {existing_players}')

    special_events.write.format('jdbc').option('url',url).\
    option('user',user).option('password',password).\
    option("dbtable", "play_by_play_stoppages").mode('append').save()


    pbp.write.format('jdbc').option('url',url).\
    option('user',user).option('password',password).\
    option("dbtable", "play_by_plays").mode('append').save()

    return


def transform_load():
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import regexp_extract
    from os import remove, listdir, environ
    from schema import extract_schema
    from os.path import expanduser, join as osjoin


    app_name = 'pbp'
    directory = expanduser(osjoin('~/spark_apps',app_name))
    input_dir = osjoin(directory,'games')

    spark = SparkSession.builder.appName(app_name).getOrCreate()

    # read data and drop unnecessary columns
    df = spark.read.option('cleanSource','delete').schema(extract_schema()).json(input_dir)
    df = df.drop('source','videoAvailable')

    # expand json and select required columns
    db = extract_cols(df)

    # extract minutes and seconds from clock column
    db = db.withColumn('minute',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',1).cast('integer'))
    db = db.withColumn('seconds',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',2).cast('float'))

    # reorder columns to conform to db table
    db = reorder_columns(db)

    players = 'select id from players'
    teams = 'select id from teams'

    user = environ.get('USER')
    url = 'jdbc:mysql://127.0.0.1:3306/nba'
    password = environ.get('PSWD')

    players = spark.read.format('jdbc').option('url',url).\
        option('user',user).option('password',password).\
        option('query',players).load()

    teams = spark.read.format('jdbc').option('url',url).\
        option('user',user).option('password',password).\
        option('query',teams).load()

    existing_players = str(tuple(players.toPandas()['id']))
    existing_teams = str(tuple(teams.toPandas()['id']))

    # write
    write_to_db(db,existing_players,existing_teams,url,user,password)

    # clean up files
    for file in listdir(input_dir):
        remove(osjoin(input_dir,file))

    return

# transform_load()
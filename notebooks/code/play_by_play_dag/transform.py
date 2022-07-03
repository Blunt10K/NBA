from schema import extract_schema

def extract_cols(pbp):
    
    pbp = pbp.withColumn('action_id',pbp.actions.getItem('actionId'))

    db = pbp.withColumn('player_id', pbp.actions.getItem('personId')).\
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

def transform():
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import explode, regexp_extract

    spark = SparkSession.builder.appName('pbp').getOrCreate()

    df = spark.readStream.option('cleanSource','delete').schema(extract_schema()).json('games')
    # print(df.printSchema())
    df = df.drop('source','videoAvailable')

    table_order = ['game_id', 'action_id', 'player_id', 'team_id', 'period', 'minute',
        'seconds', 'x_loc', 'y_loc', 'shot_distance', 'shot_result',
        'field_goal', 'home_score', 'away_score', 'total_points', 'location',
        'description', 'action_type', 'sub_type']

    pbp = df.withColumn('actions',explode(df.actions)).withColumnRenamed('gameId','game_id')

    db = extract_cols(pbp)

    db = db.withColumn('minute',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',1).cast('integer'))
    db = db.withColumn('seconds',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',2).cast('float'))

    db = db[table_order]

    db.writeStream.format("parquet").option("path", "to_db").option("checkpointLocation", "checkpoints").start()
    
    return
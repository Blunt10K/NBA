from sre_parse import expand_template
from schema import extract_schema
from os.path import expanduser, join as osjoin

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


def transform():
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import regexp_extract

    app_name = 'pbp'

    directory = expanduser(osjoin('~/spark_apps',app_name))
    input_dir = osjoin(directory,'games')
    checkpoint_dir = osjoin(directory,'checkpoints')
    output_dir = osjoin(directory,'to_db')

    spark = SparkSession.builder.appName(app_name).getOrCreate()

    df = spark.readStream.option('cleanSource','delete').schema(extract_schema()).json(input_dir)

    # drop unnecessary columns
    df = df.drop('source','videoAvailable')

    # expand json and select required columns
    db = extract_cols(df)

    # extract minutes and seconds from clock column
    db = db.withColumn('minute',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',1).cast('integer'))
    db = db.withColumn('seconds',regexp_extract(db.clock,r'PT(\d+)M(\d+\.\d+)S',2).cast('float'))

    # reorder columns to conform to db table
    db = reorder_columns(db)

    # write
    db.writeStream.format("parquet").option("path", output_dir).option('cleanSource','delete').\
        option('checkpointLocation', checkpoint_dir).start()
    
    return
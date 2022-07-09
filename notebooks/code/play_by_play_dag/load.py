from os import environ
from os.path import expanduser, join as osjoin
from schema import load_schema


def write_to_db(df,epoch):
    user = environ.get('USER'),
    url = 'jdbc:mysql://localhost:3306'
    password = environ.get('PSWD')

    df.persist()

    special_events = df.select('*').filter(df.team_id == 0)
    pbp = df.select('*').filter(df.team_id != 0)

    special_events.write.format('jdbc').option('url',url).\
    option('user',user).option('password',password).\
    option("dbtable", "nba.play_by_play_stoppages").mode('append').save()


    pbp.write.format('jdbc').option('url',url).\
    option('user',user).option('password',password).\
    option("dbtable", "nba.play_by_plays").mode('append').save()

    
    df.unpersist()

    return


def load():
    from pyspark.sql import SparkSession

    app_name = 'pbp'
    input_dir = expanduser(osjoin('~/spark_apps',app_name,'to_db'))

    SparkSession.builder.config('spark.driver.extraClassPath',environ.get('SPARK_JDBC')).getOrCreate()
    spark = SparkSession.builder.appName(app_name).getOrCreate()

    df = spark.readStream.schema(load_schema()).parquet(input_dir,mergeSchema=True)

    df.writeStream.outputMode('append').foreachBatch(write_to_db).start()

    return

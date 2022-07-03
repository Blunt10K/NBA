from os import environ
from schema import load_schema


def write_to_db(df,epoch):
    df.persist()

    special_events = df.select('*').filter(df.team_id == 0)
    pbp = df.select('*').filter(df.team_id != 0)

    special_events.write.format('jdbc').option('url','jdbc:mysql://localhost:3306').\
    option('user',environ.get('USER')).option('password',environ.get('PSWD')).\
    option("dbtable", "nba.play_by_play_stoppages").mode('append').save()


    pbp.write.format('jdbc').option('url','jdbc:mysql://localhost:3306').\
    option('user',environ.get('USER')).option('password',environ.get('PSWD')).\
    option("dbtable", "nba.play_by_plays").mode('append').save()

    
    df.unpersist()

    return


def load():
    from pyspark.sql import SparkSession

    SparkSession.builder.config('spark.driver.extraClassPath',environ.get('SPARK_JDBC')).getOrCreate()
    spark = SparkSession.builder.appName('pbp').getOrCreate()

    df = spark.readStream.schema(load_schema()).parquet('to_db',mergeSchema=True)

    df.writeStream.outputMode('append').foreachBatch(write_to_db).start()

    return

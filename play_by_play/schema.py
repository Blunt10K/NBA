from pyspark.sql.types import ArrayType,StructField,StringType,StructType,IntegerType,FloatType

def extract_schema():
    schema = StructType([StructField('actions',ArrayType(
        StructType([StructField('actionId',IntegerType()),StructField('actionNumber',IntegerType()),
                    StructField('actionType',StringType()),StructField('clock',StringType()),
                    StructField('description',StringType()),StructField('isFieldGoal',IntegerType()),
                    StructField('location',StringType()),StructField('period',IntegerType()),
                    StructField('personId',IntegerType()),StructField('playerName',StringType()),
                    StructField('playerNameI',StringType()),StructField('pointsTotal',IntegerType()),
                    StructField('scoreAway',StringType()),StructField('scoreHome',StringType()),
                    StructField('shotDistance',IntegerType()),StructField('shotResult',StringType()),
                    StructField('subType',StringType()),StructField('teamId',IntegerType()),
                    StructField('teamTricode',StringType()),StructField('videoAvailable',IntegerType()),
                    StructField('xLegacy',IntegerType()),StructField('yLegacy',IntegerType())]
                )
            )
        ),
    StructField('gameId',StringType(),False),
    StructField('source',StringType() ),
    StructField('videoAvailable',IntegerType())])

    return schema


def load_schema():
    schema = StructType([StructField('game_id',StringType()),StructField('action_id',IntegerType()),
                    StructField('player_id',IntegerType()),StructField('team_id',IntegerType()),
                    StructField('period',IntegerType()),StructField('minute',IntegerType()),
                    StructField('seconds',FloatType()),StructField('x_loc',IntegerType()),
                    StructField('y_loc',IntegerType()),StructField('shot_distance',IntegerType()),
                    StructField('shot_result',StringType()),StructField('field_goal',IntegerType()),
                    StructField('home_score',IntegerType()),StructField('away_score',IntegerType()),
                    StructField('total_points',IntegerType()),StructField('location',StringType()),
                    StructField('description',StringType()),StructField('action_type',StringType()),
                    StructField('sub_type',StringType())]
                )

    return schema
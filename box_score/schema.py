from pyspark.sql.types import StructType

def box_score_schema():

    schema = StructType().add('player_id','integer',False).add('team_id','string',False).\
    add('game_id','string',False).add('mins','integer').\
    add('pts', 'integer').add('fgm', 'integer').add('fga', 'integer').\
    add('pm3', 'integer').add('pa3', 'integer').add('ftm', 'integer').\
    add('fta', 'integer').add('oreb', 'integer').add('dreb', 'integer').\
    add('ast', 'integer').add('stl', 'integer').add('blk', 'integer').\
    add('tov', 'integer').add('pf', 'integer').add('plus_minus', 'integer').\
    add('result','string').add('game_day','date').add('match_up','string')

    return schema 

def extract_schema():    

    schema = StructType().add('Player','string',False).add('Team','string',False).\
    add('Match Up','string',False).\
    add('Game Date','date',False).add('W/L','string').add('MIN','integer').\
    add('PTS', 'integer').add('FGM', 'integer').add('FGA', 'integer').add('FG%', 'float').\
    add('3PM', 'integer').add('3PA', 'integer').add('3P%', 'float').add('FTM', 'integer').\
    add('FTA', 'integer').add('FT%', 'float').add('OREB', 'integer').add('DREB', 'integer').\
    add('REB', 'integer').add('AST', 'integer').add('STL', 'integer').add('BLK', 'integer').\
    add('TOV', 'integer').add('PF', 'integer').add('+/-', 'integer').add('FP', 'float').\
    add('pids', 'integer',False).add('tids', 'integer',False).add('gids','string',False)

    return schema

def atom_schema():

    return StructType().add('id','integer',False).add('name','string',False)
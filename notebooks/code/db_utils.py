from sqlalchemy import create_engine

def make_engine(user, pswd, db):

    return create_engine("mariadb+mariadbconnector://"\
                        +user+":"\
                        +pswd+"@127.0.0.1:3306/"+db)
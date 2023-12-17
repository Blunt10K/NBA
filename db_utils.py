from sqlalchemy import create_engine
from airflow.models import Variable

def make_engine():
    host = Variable.get('HOSTNAME')
    db = Variable.get('NBA_DB')
    port = Variable.get('PORT')
    user = Variable.get('USER')
    pswd = Variable.get('PSWD')

    return create_engine(f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{db}")
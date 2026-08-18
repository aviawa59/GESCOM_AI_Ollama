import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

load_dotenv()

def create_connection():
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    database = os.getenv("DB_NAME")


    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )
    return engine

def query_database(sql):
    engine = create_connection()

    with engine.connect() as connection:

        # Clean escaped formatting characters from LLM-generated SQL
        sql = sql.replace("\\n", "\n").replace("\\t", "\t")
        result = connection.execute(text(sql))

        rows = result.mappings().all()

        return [dict(row) for row in rows]


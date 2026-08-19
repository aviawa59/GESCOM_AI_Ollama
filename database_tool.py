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

def query_database(sql, params=None):
    try:
        engine = create_connection()

        with engine.connect() as connection:

            # Clean escaped formatting characters from LLM-generated SQL
            sql = sql.replace("\\n", "\n").replace("\\t", "\t")

            result = connection.execute(
                text(sql),
                params or {}
            )

            rows = result.mappings().all()

            return {
                "success": True,
                "data": [dict(row) for row in rows]
            }

    except Exception as e:
        return {
            "success": False,
            "error_type": "database_error",
            "message": str(e)
        }
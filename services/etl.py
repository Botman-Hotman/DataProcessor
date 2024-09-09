from core.db import sync_engine
from sqlalchemy import text
import logging


def create_etl():
    logging.info('Creating ETL data warehouse')
    with sync_engine.begin() as conn:
        with open('sql/etl.sql', 'r') as sql_file:
            statements = sql_file.read()
            for stmt in statements.split(';'):
                if stmt.strip() == '':
                    pass
                else:
                    conn.execute(text(stmt.strip()))
        conn.commit()
        conn.close()
        logging.info('ETL data warehouse ready! Check the database')

def create_analysis():
    logging.info('Creating analysis views in data warehouse')
    with sync_engine.begin() as conn:
        with open('sql/analysis.sql', 'r') as sql_file:
            statements = sql_file.read()
            for stmt in statements.split(';'):
                if stmt.strip() == '':
                    pass
                else:
                    conn.execute(text(stmt.strip()))
        conn.commit()
        conn.close()
        logging.info('analysis views in data warehouse ready! Check the database')

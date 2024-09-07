import logging
import time

import pandas as pd
from core.config import settings
from core.db import (
    map_dtype_to_postgres,
    async_engine,
    sync_engine,
    sync_session_factory
)
from datetime import datetime
import os
from sqlalchemy import text, MetaData, Table, insert


async def import_data_to_staging(file_path: str):
    file_name = os.path.basename(file_path)
    logging.debug(f'Importing data {file_name}...')
    df: pd.DataFrame = pd.read_csv(file_path)
    df.columns = [f"column_{i}" if col.startswith('Unnamed') else col.strip().replace(' ', '_').lower() for i, col in enumerate(df.columns)]

    if df.shape[0] > 0:
        logging.info(f'{df.shape[0]} rows detected for {file_name}, importing to database...')

        # make the staging table name file name with todays date as an integer
        table_name: str = f"{file_name.split('.')[0].strip().replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}"

        # map pandas data column types into postgres
        column_definitions = [f""""{col}" {map_dtype_to_postgres(df[col].dtype)}""" for col in df.columns]

        async with async_engine.begin() as conn:
            create_table_query = f"""CREATE TABLE IF NOT EXISTS {settings.staging_schema}."{table_name}" ({", ".join(column_definitions)});"""
            await conn.execute(text(create_table_query))
            await conn.commit()

        time.sleep(1)

        metadata = MetaData(schema=settings.staging_schema)
        with sync_engine.connect() as connection:
            # create abstract orm object based on the existing schema made above
            table = Table(table_name, metadata, autoload_with=connection)

            with sync_session_factory() as session:
                try:
                    records = df.to_dict(orient='records')

                    # Create insert statement
                    stmt = insert(table)

                    # Execute the insert statement with the records
                    connection.execute(stmt, records)
                    session.commit()
                    session.close()
                    logging.info(f"{file_name} imported {df.shape[0]} rows successfully")

                except Exception as e:
                    session.rollback()
                    logging.exception(f"Error occurred with {file_name} : {e}")

            connection.commit()
            connection.close()

    else:
        logging.warning(f"{file_name} has no rows to process!")

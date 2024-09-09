import logging
import time

import pandas as pd
from core.config import settings
from core.utils import row_to_uuid, flatten_list
from core.db import (
    map_dtype_to_postgres,
    async_engine,
    sync_engine,
    sync_session_factory
)
import os
from sqlalchemy import text, MetaData, Table
from sqlalchemy.dialects.postgresql import insert


async def check_table_status(table_name: str, target_df: pd.DataFrame) -> None:
    """
    Check if a table exists in the database, if not create it and its primary key
    :param table_name:
    :param target_df:
    :return:
    """
    # map pandas data column types into postgres
    column_definitions: list = [f""""{col}" {map_dtype_to_postgres(target_df[col].dtype)}""" for col in target_df.columns]

    async with async_engine.begin() as conn:
        table_exists_query = f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = '{settings.staging_schema}' 
                                AND table_name = '{table_name}'
                            );
                        """
        result = await conn.execute(text(table_exists_query))
        table_exists = result.scalar()

        if not table_exists:
            # Create table if it doesn't exist, or ensure structure if it does
            create_table_query = f"""CREATE TABLE IF NOT EXISTS {settings.staging_schema}."{table_name}" ({", ".join(column_definitions)});"""

            await conn.execute(text(create_table_query))

            # Add the unique constraint, set id as NOT NULL, and make it the primary key
            await conn.execute(text(f"""ALTER TABLE {settings.staging_schema}."{table_name}" ADD CONSTRAINT unique_title UNIQUE (title);"""))
            await conn.execute(text(f"""ALTER TABLE {settings.staging_schema}."{table_name}" ALTER COLUMN title SET NOT NULL;"""))
            await conn.execute(text(f"""ALTER TABLE {settings.staging_schema}."{table_name}" ADD PRIMARY KEY (title);"""))
            await conn.commit()


async def import_data_to_staging(file_path: str) -> None:
    """
    Creates/Updates a table in postgres from the target file path.
    This process will create an ID that is a hash of all the row data for better duplicate detection.
    :param file_path:
    :return:
    """
    file_name: str = os.path.basename(file_path)
    logging.debug(f'Importing data from {file_name}')
    df: pd.DataFrame = pd.read_csv(file_path)

    if df.shape[0] > 0:
        logging.info(f'{df.shape[0]} rows detected for {file_name}')

        # standardise columns and remove whitespace
        df.columns = [f"column_{i}" if col.startswith('Unnamed') else col.strip().replace(' ', '_').lower() for i, col in enumerate(df.columns)]

        cols_to_keep = ["title", "pdl_count", "top_related_titles"]

        # Identify the columns beyond the first three (the ones to flatten)
        cols_to_flatten = df.columns[3:]

        # Create a new DataFrame where each row's flattened values are combined into a list
        df['related_titles'] = df[cols_to_flatten].apply(lambda row: row.dropna().tolist(), axis=1)

        # Keep only the first three columns and the new 'flattened_columns' column
        df = df[cols_to_keep + ['related_titles']]

        # recreate related titles as a list
        df = df.groupby('title').agg({
            'pdl_count': 'first',  # Keep the first pdl_count value for each group
            'top_related_titles': 'first',  # Keep the first top_related_titles value
            'related_titles': lambda x: list(set(flatten_list(x)))  # Flatten, clean up strings, remove duplicates
        }).reset_index()

        # make an id column that is hash of the data Move the 'id' column to the first position
        # df['id'] = df.apply(row_to_uuid, axis=1)
        # columns = ['id'] + [col for col in df.columns if col != 'id']
        # df = df[columns]

        # make the staging table name file name with today's date as an integer
        # table_name: str = f"{file_name.split('.')[0].strip().replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}"
        table_name: str = f"{file_name.split('.')[0].strip().replace(' ', '_')}"

        # check that the table exists and perform db operations
        # to create the table based on the imported flat file
        await check_table_status(table_name, df)

        time.sleep(1)

        metadata = MetaData(schema=settings.staging_schema)
        with sync_engine.connect() as connection:
            # create abstract orm object based on the existing schema
            table = Table(table_name, metadata, autoload_with=connection)

            with sync_session_factory() as session:
                try:
                    records = df.to_dict(orient='records')

                    # Create insert statement that
                    stmt = insert(table).on_conflict_do_update(
                        index_elements=['title'],  # Specify the primary key or unique column
                        set_={col.name: col for col in table.c if col.name != 'title'}  # Update all columns except 'id'
                    )

                    # Execute the insert statement with the records
                    connection.execute(stmt, records)
                    session.commit()
                    session.close()
                    logging.info(f"{file_name} imported {df.shape[0]} rows processed successfully")

                except Exception as e:
                    session.rollback()
                    logging.exception(f"Error occurred with {file_name} : {e}")

            connection.commit()
            connection.close()

    else:
        logging.warning(f"{file_name} has no rows to process!")

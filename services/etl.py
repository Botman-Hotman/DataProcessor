
from core.db import sync_engine
import pandas as pd
import logging


def create_datawarehouse_schema():
    ...



def task_one():
    with sync_engine() as conn:
        df = pd.read_sql_query("""SELECT * FROM staging."2019_free_title_data" """, conn)

    if df.shape[0] > 0:
        target_columns = df.columns.tolist()
        target_columns.remove('id')
        target_columns.remove('pdl_count')
        related_titles_df = df.melt(
            id_vars=['top_related_titles'],
            value_vars=target_columns,
            var_name='source_column',
            value_name='related_title'
        )
        related_titles_df.sort_values('top_related_titles', inplace=True)
        related_titles_df.drop('source_column', inplace=True, axis=1)
        related_titles_df['top_related_titles'] = related_titles_df['top_related_titles'].str.strip()
        related_titles_df['top_related_titles'] = related_titles_df['top_related_titles'].str.lower()

        related_titles_df['related_title'] = related_titles_df['related_title'].str.strip()
        related_titles_df['related_title'] = related_titles_df['related_title'].str.lower()
        related_titles_df.drop_duplicates(inplace=True)



    else:
        logging.info('target data returned no values')

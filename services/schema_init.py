import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List, Type
from core import Base


async def populate_dimensions_on_startup(db: AsyncSession):

    """
    Used to start the database with any base dimension data
    :param db:
    :return:
    """
    logging.info('Init database dimensions...')


class SchemaInit:
    @staticmethod
    async def populate_default_data(
            db: AsyncSession, model_class: Type[Base], default_data: List[Base]
    ) -> None:
        """
        Function to check if dimensions already exist, and to use the target SQL model to insert data
        :param db:
        :param model_class:
        :param default_data:
        :return:
        """

        # Check if the table associated with the model_class is empty
        result = await db.execute(select(model_class))
        existing_data = result.scalars().all()

        if not existing_data:
            db.add_all(default_data)
            await db.commit()
            await db.aclose()

    @staticmethod
    async def create_schema(db: AsyncSession, schema_name: str) -> None:
        await db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name.strip().replace(' ', '_').lower()}"))
        await db.commit()


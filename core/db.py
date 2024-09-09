import json
import pandas as pd

from .config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncConnection,
    create_async_engine,
    AsyncEngine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine


class MyBase:
    """
    useful functions for serilising items
    """
    __abstract__ = True

    def to_dict(self):
        """Convert the SQLAlchemy object to a dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def to_json(self):
        """Convert the SQLAlchemy object to JSON."""
        return json.dumps(self.to_dict())


# passing functions into all sql alchelmy objects
Base = declarative_base(cls=MyBase)


def map_dtype_to_postgres(dtype) -> str:
    """
    Function to map pandas data types to PostgreSQL types
    :param dtype:
    :return:
    """
    if pd.api.types.is_integer_dtype(dtype):
        return 'INT'
    elif pd.api.types.is_float_dtype(dtype):
        return 'FLOAT'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'BOOLEAN'
    elif pd.api.types.is_list_like(dtype) or pd.api.types.is_array_like(dtype):
        return 'TEXT[]'
    else:
        return 'TEXT'


# create a database engine to make raw connections to the db
async_engine: AsyncEngine = create_async_engine(
    settings.db_string_async,
    echo=settings.echo_sql,  # Useful for logging SQL queries
    pool_size=10,  # Max number of connections in the pool
    max_overflow=5,  # Max additional connections allowed beyond pool_size
    pool_timeout=30,  # Timeout for acquiring a connection from the pool
    pool_recycle=1800  # Recycle connections after 30 minutes to prevent stale connections
)

# Create a session factory bound to the async engine
async_session_factory = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Recommended for async to prevent object expiration after commit
)


sync_engine = create_engine(
    settings.db_string,
    echo=settings.echo_sql,  # Useful for logging SQL queries
    pool_size=10,  # Max number of connections in the pool
    max_overflow=5,  # Max additional connections allowed beyond pool_size
    pool_timeout=30,  # Timeout for acquiring a connection from the pool
    pool_recycle=1800  # Recycle connections after 30 minutes to prevent stale connections
)

sync_session_factory = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False
)

# Used for testing
async def create_all_schema(connection: AsyncConnection):
    await connection.run_sync(Base.metadata.create_all)


async def drop_all_schema(connection: AsyncConnection):
    await connection.run_sync(Base.metadata.drop_all)

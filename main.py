import argparse
import asyncio

from core.config import settings
from logging.handlers import RotatingFileHandler
from core.db import async_session_factory, async_engine, drop_all_schema, create_all_schema
from services.directory_watcher import watch_folder
import logging

from services.schema_init import SchemaInit, populate_dimensions_on_startup

logging.basicConfig(
    format='%(asctime)s : %(name)s :  %(levelname)s : %(funcName)s :  %(message)s'
    , level=logging.DEBUG if settings.debug_logs else logging.INFO
    , handlers=[
        RotatingFileHandler(
            filename="logs/import_data.log",
            maxBytes=10 * 1024 * 1024,  # 100 MB per file,
            backupCount=7  # keep 7 backups
        ),
        logging.StreamHandler()  # Continue to log to the console as well
    ]
)

# Create arg parser object
parser = argparse.ArgumentParser()
parser.add_argument("--watch", help="start the file watching system on a specified folder i.e. --watch 'imports'")
parser.add_argument('--pipeline', help="run the etl pipeline")

async def init_database():
    """
    Init general database and schema
    :return:
    """
    if settings.init_db:
        async with async_session_factory() as session:
            await SchemaInit().create_schema(session, settings.staging_schema)
            await SchemaInit().create_schema(session, settings.dw_schema)

        async with async_engine.begin() as conn:
            if settings.dev:
                await drop_all_schema(conn)  # drop the schema for dev work

            await create_all_schema(conn)  # Create database schemas

        async with async_session_factory() as session:
            await populate_dimensions_on_startup(session)


async def watcher(target_directory):
    await init_database()

    loop = asyncio.get_running_loop()
    await watch_folder(loop, target_directory)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.watch:
        # Run the main function asynchronously
        asyncio.run(watcher(args.watch))

    elif args.pipeline:
        ...

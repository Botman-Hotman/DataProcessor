from pydantic_settings import BaseSettings

import os
from dotenv import load_dotenv

# Load the stored environment variables
load_dotenv()


class Settings(BaseSettings):
    debug_logs: bool = bool(os.environ.get('debug_logs'))
    dev: bool = bool(os.environ.get('dev'))
    init_db: bool = bool(os.environ.get('init_db'))
    db_string: str = str(os.environ.get('db_string'))
    db_string_async: str = str(os.environ.get('db_string_async'))
    echo_sql: bool = True
    test: bool = False
    staging_schema: str = str(os.environ.get('staging_schema'))
    dw_schema: str = str(os.environ.get('dw_schema'))


settings = Settings()

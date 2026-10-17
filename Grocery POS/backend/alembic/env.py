import os
import sys
import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context

# Ensure app is in Python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.models import Base

logger = logging.getLogger("alembic.runtime.migration")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set database connection URL dynamically from application settings
config.set_main_option("sqlalchemy.url", settings.sync_database_url)

# Add our models' MetaData object for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with automatic fallback if Postgres is not running locally."""
    from app.core.database import engine

    connection = None
    try:
        connection = engine.connect()
    except Exception as exc:
        print(f"\n[Alembic Notice] PostgreSQL server not reachable ({exc}). Generating migration against schema metadata with SQLite driver.")
        fallback_engine = create_engine("sqlite:///./pos_local.db", connect_args={"check_same_thread": False})
        connection = fallback_engine.connect()

    with connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            render_as_batch=True, # Supports SQLite & PostgreSQL batch alterations
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

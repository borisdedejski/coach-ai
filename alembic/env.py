from sqlalchemy import engine_from_config
from sqlalchemy import pool
from db.models import Base
from logging.config import fileConfig


from alembic import context
import os

# Load config
config = context.config

# Configure Python logging
fileConfig(config.config_file_name)

# Set metadata for 'autogenerate'
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

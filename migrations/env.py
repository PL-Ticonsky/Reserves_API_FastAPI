"""

Purpose:
- Configure Alembic migrations for this project.
- Load DATABASE_URL from application settings (.env).
- Point Alembic autogenerate to SQLAlchemy metadata (Base.metadata).

Key idea:
- Migrations are the source of truth for database schema changes.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base  # must import models inside Base module for metadata to include them


# Alembic Config object (reads alembic.ini)
config = context.config

# Configure Python logging using alembic.ini settings
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the runtime DATABASE_URL (from .env) into Alembic configuration
config.set_main_option("sqlalchemy.url", settings.database_url)

# Target metadata for 'alembic revision --autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    In offline mode Alembic does not create a DB connection.
    It emits SQL to the script output instead.
    """
    url = config.get_main_option("sqlalchemy.url")
    assert url is not None

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In online mode Alembic creates an Engine and runs migrations against the DB.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

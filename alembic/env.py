"""
Alembic environment configuration — MagicPic Backend
=====================================================
This file is executed by every `alembic` CLI command.

Key responsibilities:
  1. Point Alembic at the application's SQLAlchemy metadata (Base.metadata)
     so `--autogenerate` can diff models vs the live database.
  2. Inject the database URL from the app's own config system instead of
     hard-coding it in alembic.ini.
  3. Import every ORM model module so their tables are registered with
     Base.metadata before autogenerate runs.

HOW TO USE
----------
Generate a new migration after changing a model:
    alembic revision --autogenerate -m "describe_your_change"

Apply all pending migrations:
    alembic upgrade head

Roll back one migration:
    alembic downgrade -1

See current revision in the DB:
    alembic current

See full migration history:
    alembic history --verbose

Stamp production without running migrations (first-time setup on existing DB):
    alembic stamp head
"""

import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so app.* imports resolve.
# This is already handled by alembic.ini's prepend_sys_path = .
# but we add it explicitly here as a safety net when running env.py
# programmatically (e.g., from pytest or CI scripts).
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Load the Alembic config object (wraps alembic.ini)
# ---------------------------------------------------------------------------
config = context.config

# Set up Python logging as defined in alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Load the app's Settings singleton so we can read DATABASE_URL.
# We intentionally do NOT use config.set_main_option() here because
# configparser (which backs alembic.ini) treats % as an interpolation
# character.  A URL-encoded password such as admin%40123 contains %40,
# which configparser rejects as invalid interpolation syntax.
# Instead we pass the URL directly to create_engine() below, bypassing
# configparser entirely.
# ---------------------------------------------------------------------------
from app.core.config import settings  # noqa: E402

# ---------------------------------------------------------------------------
# Import the shared SQLAlchemy Base.
# ALL models must inherit from this Base — that is what makes them visible
# to autogenerate.
# ---------------------------------------------------------------------------
from app.core.database import Base  # noqa: E402

# ---------------------------------------------------------------------------
# Import every model module so their classes are registered with Base.metadata
# before autogenerate compares models vs the live DB.
#
# Rule: any time you add a new models/*.py file, add an import here.
# ---------------------------------------------------------------------------
import app.models.user      # noqa: F401  — User
import app.models.style     # noqa: F401  — Category, Style, Challenge, Creation,
                            #               GuestUsage, CreationLike,
                            #               Collection, CollectionCreation
import app.models.payment   # noqa: F401  — Transaction
import app.models.rewards   # noqa: F401  — CreditTransaction, AdWatch

# ---------------------------------------------------------------------------
# This is the metadata object autogenerate inspects.
# ---------------------------------------------------------------------------
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# OFFLINE mode — emit SQL to stdout without a live DB connection.
# Useful for generating SQL scripts to review before applying.
# Usage: alembic upgrade head --sql
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    # Use settings.DATABASE_URL directly — never touch configparser.
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# ONLINE mode — connect to the live DB and apply migrations.
# This is the mode used by `alembic upgrade head`.
# ---------------------------------------------------------------------------
def run_migrations_online() -> None:
    from sqlalchemy import create_engine  # noqa: E402

    # Build the engine directly from settings.DATABASE_URL.
    # This completely sidesteps configparser and its % interpolation rules,
    # so passwords with special characters (@ # % etc.) work without issues.
    connectable = create_engine(settings.DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

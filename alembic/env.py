# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Импортируем Base и все модели, чтобы они были видны в памяти
from app.core.base import Base  # noqa: F401
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Подставляем строку подключения из настроек приложения.
# Для синхронного Alembic убираем асинхронные драйверы:
db_url = settings.database_url
if db_url is None:
    raise RuntimeError(
        'Переменная DATABASE_URL не задана! '
        'Добавьте её в файл .env в корне проекта.'
    )
db_url = db_url.replace('sqlite+aiosqlite', 'sqlite')
db_url = db_url.replace('postgresql+asyncpg', 'postgresql')
config.set_main_option('sqlalchemy.url', db_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata  # ← ЭТО КЛЮЧЕВАЯ ПРАВКА


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

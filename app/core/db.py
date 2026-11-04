# app/core/db.py

from sqlalchemy import Integer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class CommonMixin:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Асинхронный генератор сессий.
async def get_async_session():
    # При каждом вызове get_async_session()
    # из AsyncSessionLocal извлекается сессия и возвращается
    # тому, кто её запросил.
    async with AsyncSessionLocal() as async_session:
        yield async_session
        # Когда HTTP-запрос отработает, выполнение кода вернётся сюда.
        # Контекстный менеджер завершит работу.
        # При завершении работы контекстного менеджера
        # сессия будет автоматически закрыта.

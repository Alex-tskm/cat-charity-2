# app/crud/base.py
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:

    # Инициализатор класса на вход принимает модель,
    # с которой нужно выполнить операции.
    def __init__(self, model): # типизацию обобщим позже
        self.model = model

    # Универсальный метод для получения объекта по его ID:
    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    # Универсальный метод для получения всех объектов заданной модели:
    async def get_multi(
        self,
        session: AsyncSession
    ):
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    # Универсальный метод для добавления записи в базу:
    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj) # refresh() подтягивает сгенерированные БД поля (например, id)
        return db_obj

    # Универсальный метод для обновления записи по ID:
    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    # Ещё один универсальный метод, тоже пригодится:
    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        await session.delete(db_obj)
        await session.commit()
        return db_obj

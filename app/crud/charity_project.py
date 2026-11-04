# app/crud/charity_project.py
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_all_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        # Открытые проекты: берём по порядку создания,
        # чтобы инвестировать их в порядке очереди (FIFO).
        db_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(False)
            ).order_by(CharityProject.create_date)
        )
        return list(db_projects.scalars().all())


charity_project_crud = CRUDCharityProject(CharityProject)

# Добавь в существующий app/api/validators.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject


async def check_charity_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    return charity_project


async def check_charity_project_not_invested(
    charity_project: CharityProject,
) -> None:
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Нельзя изменять или удалять закрытый проект!'
        )

# app/api/endpoints/charity_project.py
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_charity_project_exists
from app.core.db import get_async_session
from app.core.user import get_current_superuser
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investment import invest

router = APIRouter(
    prefix='/charity_project',
    tags=['charity_projects']
)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
SuperUserDep = Annotated[CharityProject, Depends(get_current_superuser)]


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def create_new_charity_project(
    charity_project: CharityProjectCreate,
    session: SessionDep,
    superuser: SuperUserDep,
):
    await check_name_duplicate(charity_project.name, session)
    new_project = CharityProject(**charity_project.model_dump())
    session.add(new_project)
    free_donations = await donation_crud.get_all_not_fully_invested(
        session
    )
    invest(new_project, free_donations)
    await session.commit()
    await session.refresh(new_project)
    return new_project


async def check_name_duplicate(
    project_name: str,
    session: AsyncSession,
) -> None:
    project_id = await charity_project_crud.get_project_id_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=400,  # 400, а не 422 — по спецификации
            detail='Проект с таким именем уже существует!'
        )


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_charity_projects(session: SessionDep):
    return await charity_project_crud.get_multi(session)


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: SessionDep,
    superuser: SuperUserDep,
):
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail='Закрытый проект нельзя редактировать!'
        )

    if obj_in.name is not None and obj_in.name != charity_project.name:
        await check_name_duplicate(obj_in.name, session)

    # Нельзя установить требуемую сумму меньше уже вложенной.
    if (
        obj_in.full_amount is not None
        and obj_in.full_amount < charity_project.invested_amount
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                'Нелья установить значение full_amount '
                'меньше уже вложенной суммы.'
            )
        )

    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )

    # Если требуемая сумма стала равна вложенной — проект закрывается.
    if charity_project.invested_amount >= charity_project.full_amount:
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()

    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep,
    superuser: SuperUserDep,
):
    charity_project = await check_charity_project_exists(
        project_id, session
    )
    # Нельзя удалять проект, в который уже инвестированы средства
    # (или который закрыт — он тоже с вложениями).
    if charity_project.fully_invested or charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return await charity_project_crud.remove(charity_project, session)

# app/endpoints/donation.py
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import get_current_superuser, get_current_user
from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import (
    DonationCreate, DonationDB, DonationFullInfoDB
)
from app.services.investment import invest

router = APIRouter(
    prefix='/donation',
    tags=['donations']
)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
UserDep = Annotated[User, Depends(get_current_user)]
SuperUserDep = Annotated[User, Depends(get_current_superuser)]


@router.post(
    '/',
    response_model=DonationDB,
)
async def create_new_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: UserDep,
):
    new_donation = Donation(
        **donation.model_dump(),
        user_id=user.id,
        invested_amount=0,
        fully_invested=False,
    )
    session.add(new_donation)
    open_projects = await charity_project_crud.get_all_not_fully_invested(
        session
    )
    invest(new_donation, open_projects)
    await session.commit()
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
)
async def get_all_donations(session: SessionDep, superuser: SuperUserDep):
    return await donation_crud.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationDB],
)
async def get_my_donations(session: SessionDep, user: UserDep):
    donations = await session.scalars(
        select(Donation).where(Donation.user_id == user.id)
    )
    return list(donations)

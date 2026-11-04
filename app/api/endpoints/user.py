# app/api/endpoints/user.py
import hashlib
import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import get_current_superuser
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

EMAIL_PATTERN = re.compile(
    r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
)

router = APIRouter(tags=['users'])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def validate_password(password: str) -> None:
    """Бросает 400, если пароль не соответствует требованиям."""
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать не менее 8 символов.",
        )

    if not re.search(r"[A-Za-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы одну букву.",
        )

    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать хотя бы одну цифру.",
        )


@router.post(
    '/auth/register',
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Регистрация нового пользователя."""
    email = user_in.email.strip().lower()
    validate_password(user_in.password)

    existing = await session.scalar(
        select(User).where(User.email == email)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь с таким email уже зарегистрирован',
        )

    user = User(
        email=email,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get('/users', response_model=list[UserRead])
async def get_users(
    session: AsyncSession = Depends(get_async_session),
    superuser: User = Depends(get_current_superuser),
) -> list[User]:
    """Список всех пользователей — только для суперпользователя."""
    users = await session.scalars(select(User))
    return list(users)

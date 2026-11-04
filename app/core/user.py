# app/core/user.py
"""Простая проверка авторизации по email.

Пользователь передаёт свой email в заголовке запроса,
мы находим его в базе и считаем авторизованным.
Для суперпользователя дополнительно проверяется флаг is_superuser.
"""
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.user import User


async def get_current_user(
    email: str = Header(..., description='Email пользователя'),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    user = await session.scalar(select(User).where(User.email == email))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь с таким email не найден',
        )
    return user


async def get_current_superuser(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав. Требуются права суперпользователя',
        )
    return user


# Под этими именами зависимости импортируют эндпоинты и тесты (conftest)
current_user = get_current_user
current_superuser = get_current_superuser

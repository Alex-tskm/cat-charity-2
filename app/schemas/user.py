# app/schemas/user.py
"""Схемы пользователей для простой email-авторизации.

Зависимость fastapi-users больше не используется, поэтому схемы
наследуются напрямую от pydantic.BaseModel.
"""
from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    is_superuser: bool | None = None

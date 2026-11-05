# app/models/user.py

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import (
    MAX_LENGTH_USER_EMAIL,
    MAX_LENGTH_USER_PASSWORD_HASH,
)
from app.core.db import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_USER_EMAIL), unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=MAX_LENGTH_USER_PASSWORD_HASH), default=''
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    def __str__(self) -> str:
        return self.email

    # Отладочный метод: удобно смотреть объект в консоли и логах.
    def __repr__(self) -> str:
        return f'User(id={self.id}, email={self.email!r})'

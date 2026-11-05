# app/models/donation.py
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin


class Donation(CommonMixin, Base):
    # Пользователь, сделавший пожертвование.
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    # Необязательный комментарий к пожертвованию.
    comment: Mapped[str | None] = mapped_column(String, nullable=True)

    # Сумма пожертвования: целое число больше 0.
    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    # Сумма из пожертвования, уже распределённая по проектам: по умолчанию 0.
    invested_amount: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # Флаг: все ли деньги из пожертвования переведены в проекты.
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Питоновский дефолт (а не server_default): datetime.now()
    # даёт микросекунды, поэтому два пожертвования подряд
    # получат разные даты — этого требует тест.
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Дата полного распределения суммы по проектам.
    close_date: Mapped[datetime | None] = mapped_column(DateTime)

    # Отладочный метод: удобно смотреть объект в консоли и логах.
    def __repr__(self) -> str:
        return (
            f'Donation(id={self.id}, '
            f'full_amount={self.full_amount}, '
            f'invested_amount={self.invested_amount}, '
            f'fully_invested={self.fully_invested}, '
            f'user_id={self.user_id})'
        )

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name='check_full_amount_gt_0',
        ),
        CheckConstraint(
            'invested_amount >= 0',
            name='check_invested_amount_ge_0',
        ),
        CheckConstraint(
            'invested_amount <= full_amount',
            name='check_invested_amount_le_full_amount',
        ),
    )

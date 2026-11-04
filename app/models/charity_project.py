# app/models/charity_project.py
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base, CommonMixin


class CharityProject(CommonMixin, Base):
    # Уникальное название проекта: от 5 до 100 символов.
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    # Описание проекта: не менее 10 символов.
    description: Mapped[str] = mapped_column(String, nullable=False)

    # Требуемая сумма: целое число больше 0.
    # Ограничение «больше 0» задаётся на уровне БД через CheckConstraint.
    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    # Собранная сумма: по умолчанию 0.
    invested_amount: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # Флаг закрытия проекта: по умолчанию False.
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Дата создания проставляется автоматически при вставке записи.
    create_date: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    # Дата закрытия заполняется только когда набрана нужная сумма,
    # поэтому по умолчанию NULL.
    close_date: Mapped[datetime | None] = mapped_column(DateTime)

    # Ограничения на уровне БД:
    # — название от 5 до 100 символов;
    # — описание не менее 10 символов;
    # — требуемая сумма строго больше 0;
    # — собранная сумма не может быть отрицательной.
    __table_args__ = (
        CheckConstraint(
            'LENGTH(name) BETWEEN 5 AND 100',
            name='check_name_length',
        ),
        CheckConstraint(
            'LENGTH(description) >= 10',
            name='check_description_length',
        ),
        CheckConstraint(
            'full_amount > 0',
            name='check_full_amount_gt_0',
        ),
        CheckConstraint(
            'invested_amount >= 0',
            name='check_invested_amount_ge_0',
        ),
    )

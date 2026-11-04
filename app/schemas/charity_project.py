# app/schemas/charity_project.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CharityProjectBase(BaseModel):
    # Лишние поля в запросе (id, invested_amount, fully_invested,
    # create_date, close_date) теперь вызывают 422 вместо молчаливого игнора.
    model_config = ConfigDict(extra='forbid')

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[int] = Field(None, gt=0)


class CharityProjectCreate(CharityProjectBase):
    # При создании все три поля обязательны.
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: int = Field(..., gt=0)


class CharityProjectUpdate(CharityProjectBase):
    @field_validator('name')
    @classmethod
    def name_cannot_be_too_short(cls, value: Optional[str]):
        if value is not None and len(value) < 5:
            raise ValueError('Имя проекта не может быть короче 5 символов!')
        return value

    @field_validator('description')
    @classmethod
    def description_cannot_be_too_short(cls, value: Optional[str]):
        if value is not None and len(value) < 10:
            raise ValueError('Описание не может быть короче 10 символов!')
        return value

    @field_validator('full_amount')
    @classmethod
    def full_amount_must_be_positive(cls, value: Optional[int]):
        if value is not None and value <= 0:
            raise ValueError('Требуемая сумма должна быть больше 0!')
        return value


# Наследуем от Create: в ответе name, description, full_amount
# обязательны и проходят те же ограничения, как в спецификации.
class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

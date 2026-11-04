# app/schemas/donation.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationBase(BaseModel):
    # Запрет лишних полей: fully_invested, user_id, create_date,
    # invested_amount в запросе теперь дают 422.
    model_config = ConfigDict(extra='forbid')

    full_amount: Optional[int] = Field(None, gt=0)
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    full_amount: int = Field(..., gt=0)


# Схема ответа на POST /donation/ и GET /donation/my:
# только сумма, комментарий, id и дата создания.
class DonationDB(DonationCreate):
    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


# Полная схема для GET /donation/: видны все служебные поля,
# включая автора пожертвования.
class DonationFullInfoDB(DonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None
